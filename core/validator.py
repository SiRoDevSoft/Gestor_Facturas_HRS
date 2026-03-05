#validator.py

class FinancialValidator:
    @staticmethod
    def validate_row_integrity(partes_fila):
        """
        Valida que la suma de los componentes individuales de la línea 
        coincida con los totales reportados en la misma fila de 17 campos.
        """
        from utils.helpers import clean_currency
        
        try:
            # 1. Extraer los componentes para la suma dinámica (Indices 1 al 6)
            # 'Plan de voz', 'Servicios voz', 'Pack sms', 'Pack datos', 'Garantia', 'Otros Servicios'
            cargos_individuales = [clean_currency(partes_fila[i]) for i in range(1, 7)]
            
            # 2. El valor de referencia que debe ser el total (Indice 7)
            total_fijo_reportado = clean_currency(partes_fila[7])
            
            # 3. El neto final de la línea (Indice 16)
            total_neto_reportado = clean_currency(partes_fila[16])

            # --- LA REGLA DE ORO ---
            # La suma de los índices 1-6 debe ser igual al índice 7
            suma_calculada_fijos = round(sum(cargos_individuales), 2)
            
            if suma_calculada_fijos != round(total_fijo_reportado, 2):
                return False, 0.0, 0.0

            # Verificación lógica: El neto no puede ser menor a los fijos
            if total_neto_reportado < total_fijo_reportado:
                return False, 0.0, 0.0

            return True, total_fijo_reportado, total_neto_reportado
            
        except (ValueError, IndexError):
            return False, 0.0, 0.0

    @staticmethod
    def check_integrity(neto_abonados, impuestos_mora, total_pdf):
        """
        Validación macro: Compara la suma de todos los abonados + extras 
        contra el total leído del PDF con margen de error de $1.50.
        """
        calculado = round(neto_abonados + impuestos_mora, 2)
        diferencia = abs(calculado - total_pdf)
        
        # Tolerancia por redondeos de centavos en 106 líneas
        if diferencia <= 1.5:
            return True, calculado
        
        return False, calculado