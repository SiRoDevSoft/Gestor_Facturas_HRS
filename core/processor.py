import json
import re
from core.extractor import PDFExtractor
from core.validator import FinancialValidator
from utils.helpers import clean_currency

class BillingProcessor:
    def __init__(self, config_path='json/config_lineas.json'):
        self.config_lineas = self._load_json(config_path)
        self.extractor = PDFExtractor()
        self.LINEA_FIN_PRINCIPAL = "5266781997" 

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: 
            return {}

    def process_invoice(self, pdf_principal, pdf_juegos=None, otros_cargos_manual=0.0, juegos_manuales=None):
        datos_validados = {}
        
        # --- MODIFICACIÓN PARA STREAMLIT CLOUD ---
        # Aseguramos que el puntero del archivo esté al inicio
        if hasattr(pdf_principal, 'seek'):
            pdf_principal.seek(0)
            
        lines_p, _ = self.extractor.fetch_raw_data(pdf_principal)
        
        # --- 1. PROCESAR ABONADOS ---
        for line in lines_p:
            partes = line.split()
            if len(partes) == 17 and partes[0] in self.config_lineas:
                nro = partes[0]
                es_valida, t_fijo, t_neto = FinancialValidator.validate_row_integrity(partes)
                if es_valida:
                    info = self.config_lineas[nro]
                    datos_validados[nro] = {
                        "linea": nro,
                        "nombre": info.get("nombre", "S/D"),
                        "categoria": info.get("grupo", "VARIOS"),
                        "total_fijo": t_fijo,
                        "total_variable": round(t_neto - t_fijo, 2),
                        "juegos_extra": 0.0,
                        "total_neto": t_neto
                    }
                if nro == self.LINEA_FIN_PRINCIPAL: break

        # --- 2. PROCESAR JUEGOS (PDF) ---
        if pdf_juegos:
            # Rebobinamos también el anexo de juegos
            if hasattr(pdf_juegos, 'seek'):
                pdf_juegos.seek(0)
                
            lines_j, _ = self.extractor.fetch_raw_data(pdf_juegos)
            for line in lines_j:
                if any(x in line for x in ["Suscripción", "Servicio Tono"]):
                    match_nro = re.search(r'(\d{10})', line)
                    if match_nro:
                        nro_det = match_nro.group(1)
                        if nro_det in datos_validados:
                            monto = clean_currency(line.split()[-1])
                            datos_validados[nro_det]["juegos_extra"] += monto

        # --- 3. APLICAR JUEGOS MANUALES (Si existen) ---
        if juegos_manuales:
            for nro, monto in juegos_manuales.items():
                nro_str = str(nro).strip()
                if nro_str in datos_validados:
                    # Sumamos el manual al del PDF (o reemplazamos)
                    datos_validados[nro_str]["juegos_extra"] += monto

        # --- 4. RECALCULAR TOTALES NETOS POR LÍNEA ---
        for nro in datos_validados:
            d = datos_validados[nro]
            d["total_neto"] = round(d["total_fijo"] + d["total_variable"] + d["juegos_extra"], 2)

        lista_final = list(datos_validados.values())
        neto_abonados_juegos = sum(d['total_neto'] for d in lista_final)
        neto_total_con_ajustes = round(neto_abonados_juegos + otros_cargos_manual, 2)

        # --- 5. AUDITORÍA ---
        resumen_tax, aud_fiscal = self._extract_and_audit_tax(lines_p, neto_total_con_ajustes)

        return {
            "datos": lista_final,
            "resumen_impositivo": resumen_tax,
            "auditoria_fiscal": aud_fiscal,
            "total_principal": round(sum(d['total_fijo'] + d['total_variable'] for d in lista_final), 2),
            "total_juegos": round(sum(d['juegos_extra'] for d in lista_final), 2),
            "total_final": neto_total_con_ajustes
        }

    def _extract_and_audit_tax(self, lines, neto_sistema):
        resumen = []
        en_seccion = False
        s_iva = 0.0
        aud_fiscal = {
            "iva_ok": False, 
            "match_factura": False, 
            "iva_pdf": 0.0, 
            "factura_pdf": 0.0, 
            "calculo_sistema": 0.0,
            "error_lectura": True
        }

        content_full = " ".join(lines)
        if "RESUMEN IMPOSITIVO" not in content_full:
            return resumen, aud_fiscal

        for line in lines:
            if "RESUMEN IMPOSITIVO" in line:
                en_seccion = True
                continue
            if not en_seccion: continue
            partes = line.split()
            if not partes: continue

            if any(k in line for k in ["Ingresos Brutos", "Ley 27.430", "Percepción I.V.A."]):
                v = clean_currency(partes[-1])
                resumen.append({"Concepto": " ".join(partes[:-1]), "Base Imponible": v, "IVA": 0.0, "Total": 0.0, "Total Factura": 0.0})
            elif "IVA" in line and ("21,00%" in line or "27,00%" in line):
                base, iva_v = clean_currency(partes[2]), clean_currency(partes[3])
                s_iva += iva_v
                resumen.append({"Concepto": f"{partes[0]} {partes[1]}", "Base Imponible": base, "IVA": iva_v, "Total": 0.0, "Total Factura": 0.0})
            elif "Totales" in partes[0]:
                iva_p, tot_i = clean_currency(partes[1]), clean_currency(partes[2])
                total_f = round(neto_sistema + tot_i, 2)
                f_pdf = 0.0
                for i, p in enumerate(partes):
                    if "TOTAL" in p.upper() and (i+1) < len(partes):
                        f_pdf = clean_currency(partes[i+1])
                        break
                resumen.append({"Concepto": 
                                "Totales", 
                                "Base Imponible": 0.0, 
                                "IVA": iva_p, "Total": tot_i, 
                                "Total Factura": total_f
                                })
                aud_fiscal = {"iva_ok": round(s_iva, 2) == iva_p, 
                              "match_factura": total_f == f_pdf, 
                              "iva_pdf": iva_p, 
                              "factura_pdf": f_pdf, 
                              "calculo_sistema": total_f,
                              "error_lectura": False}
                break 
        return resumen, aud_fiscal
