# # from fpdf import FPDF
# # import pandas as pd

# # class BoletosPDF(FPDF):
# #     def header(self):
# #         self.set_font('Arial', 'B', 15)
# #         self.cell(0, 10, 'HIERROSAN S.A.', 0, 1, 'C')
# #         self.ln(5)

# # def generar_pdf_bytes(grupo, df, total):
# #     pdf = BoletosPDF()
# #     pdf.add_page()
# #     pdf.set_font("Arial", 'B', 12)
# #     pdf.cell(0, 10, f"GRUPO: {grupo}", 0, 1)
# #     pdf.set_font("Arial", size=10)
# #     pdf.cell(0, 10, f"Fecha: {pd.Timestamp.now().strftime('%d/%m/%Y')}", 0, 1)
# #     pdf.ln(5)

# #     headers = ["Línea", "Fijo", "Variable", "Juegos", "Total c/Imp"]
# #     pdf.set_fill_color(200, 220, 255)
# #     for h in headers:
# #         pdf.cell(38, 10, h, 1, 0, 'C', 1)
# #     pdf.ln()

# #     for _, row in df.iterrows():
# #         pdf.cell(38, 8, str(row['Línea']), 1)
# #         pdf.cell(38, 8, f"$ {row['Fijo']:,.2f}", 1)
# #         pdf.cell(38, 8, f"$ {row['Variable']:,.2f}", 1)
# #         pdf.cell(38, 8, f"$ {row['Juegos']:,.2f}", 1)
# #         pdf.cell(38, 8, f"$ {row['Total c/Imp']:,.2f}", 1)
# #         pdf.ln()

# #     pdf.ln(5)
# #     pdf.set_font("Arial", 'B', 14)
# #     pdf.cell(0, 10, f"TOTAL A PAGAR: $ {total:,.2f}", 0, 1, 'R')
# #     return pdf.output()

# def generar_pdf_bytes(grupo, df, total):
#     pdf = BoletosPDF()
#     pdf.add_page()
    
#     # Encabezado de Grupo y Fecha [cite: 1, 2, 3]
#     pdf.set_font("Arial", 'B', 12)
#     pdf.cell(0, 10, f"GRUPO: {grupo}", 0, 1)
#     pdf.set_font("Arial", size=10)
#     pdf.cell(0, 10, f"Fecha de Emisión: {pd.Timestamp.now().strftime('%d/%m/%Y')}", 0, 1) [cite: 2]
#     pdf.ln(5)

#     # Lógica de Columnas Dinámicas 
#     # Si es TERCEROS_HRS, incluimos "Usuario" y achicamos las otras columnas
#     if "Usuario" in df.columns:
#         headers = ["Usuario", "Línea", "Fijo", "Var", "Juegos", "Total c/Imp"]
#         col_widths = [55, 30, 25, 20, 25, 35] # Total 190mm (ancho A4 útil)
#     else:
#         headers = ["Línea", "Fijo", "Variable", "Juegos", "Total c/Imp"]
#         col_widths = [45, 35, 35, 30, 45]

#     # Renderizado de Encabezados 
#     pdf.set_fill_color(200, 220, 255)
#     pdf.set_font("Arial", 'B', 9)
#     for i, h in enumerate(headers):
#         pdf.cell(col_widths[i], 10, h, 1, 0, 'C', 1)
#     pdf.ln()

#     # Renderizado de Filas (Ordenadas alfabéticamente desde la vista) 
#     pdf.set_font("Arial", size=9)
#     for _, row in df.iterrows():
#         # Ajustamos según el set de columnas elegido
#         if "Usuario" in df.columns:
#             pdf.cell(col_widths[0], 8, str(row['Usuario'])[:25], 1) # Truncamos a 25 caracteres
#             pdf.cell(col_widths[1], 8, str(row['Línea']), 1, 0, 'C')
#             pdf.cell(col_widths[2], 8, f"$ {row['Fijo']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[3], 8, f"$ {row['Variable']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[4], 8, f"$ {row['Juegos']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[5], 8, f"$ {row['Total c/Imp']:,.2f}", 1, 0, 'R')
#         else:
#             pdf.cell(col_widths[0], 8, str(row['Línea']), 1, 0, 'C')
#             pdf.cell(col_widths[1], 8, f"$ {row['Fijo']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[2], 8, f"$ {row['Variable']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[3], 8, f"$ {row['Juegos']:,.2f}", 1, 0, 'R')
#             pdf.cell(col_widths[4], 8, f"$ {row['Total c/Imp']:,.2f}", 1, 0, 'R')
#         pdf.ln()

#     # Total Final [cite: 5]
#     pdf.ln(5)
#     pdf.set_font("Arial", 'B', 14)
#     pdf.cell(0, 10, f"TOTAL A PAGAR: $ {total:,.2f}", 0, 1, 'R') [cite: 5]
    
#     return pdf.output()
#######################################################################################

from fpdf import FPDF
import pandas as pd
import os

class BoletosPDF(FPDF):
    def header(self):
        # Definimos la ruta correcta hacia la carpeta assets
        # Si 'core' y 'assets' están al mismo nivel, subimos un nivel con '..'
        ruta_logo = os.path.join("assets", "logo.png")
        
        # 1. Logo en la parte superior izquierda
        if os.path.exists(ruta_logo):
            self.image(ruta_logo, 15, 12, 50)
        else:
            # Opcional: imprimir un log en consola si no se encuentra
            print(f"Advertencia: No se encontró el logo en {ruta_logo}")
        
        # 2. Datos de la empresa en la parte opuesta (derecha)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(50, 50, 50)
        self.set_xy(140, 8)
        self.multi_cell(60, 4, 
            "RAMON SANCHEZ E HIJOS SRL\n"
            "AV. MITRE 828 CP 5600\n"
            "SAN RAFAEL, MENDOZA, AR.", 
            0, 'R')
        
        # Línea decorativa celeste Hierrosan
        self.set_draw_color(0, 157, 223)
        self.line(10, 28, 200, 28)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()} - Generado por Hierrosan ERP', 0, 0, 'C')

def generar_pdf_bytes(grupo, df, total):
    pdf = BoletosPDF()
    pdf.add_page()
    
    # Título del Reporte
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"BOLETO DE COBRO: {grupo}", 0, 1, 'L')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Fecha de Emisión: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
    pdf.ln(5)

    # Lógica de Columnas Dinámicas (Senior Check)
    if "Usuario" in df.columns:
        headers = ["Usuario", "Línea", "Fijo", "Var.", "Juegos", "Total c/Imp"]
        col_widths = [55, 30, 25, 20, 25, 35]
    else:
        headers = ["Línea", "Fijo", "Variable", "Juegos", "Total c/Imp"]
        col_widths = [45, 35, 35, 30, 45]

    # Encabezados de Tabla
    pdf.set_fill_color(0, 157, 223) # Azul Hierrosan
    pdf.set_text_color(255, 255, 255) # Texto blanco
    pdf.set_font("Arial", 'B', 9)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, 1, 0, 'C', 1)
    pdf.ln()

    # Filas de Datos
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        if "Usuario" in df.columns:
            pdf.cell(col_widths[0], 8, str(row['Usuario'])[:28], 1)
            pdf.cell(col_widths[1], 8, str(row['Línea']), 1, 0, 'C')
            pdf.cell(col_widths[2], 8, f"$ {row['Fijo']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[3], 8, f"$ {row['Variable']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[4], 8, f"$ {row['Juegos']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[5], 8, f"$ {row['Total c/Imp']:,.2f}", 1, 0, 'R')
        else:
            pdf.cell(col_widths[0], 8, str(row['Línea']), 1, 0, 'C')
            pdf.cell(col_widths[1], 8, f"$ {row['Fijo']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[2], 8, f"$ {row['Variable']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[3], 8, f"$ {row['Juegos']:,.2f}", 1, 0, 'R')
            pdf.cell(col_widths[4], 8, f"$ {row['Total c/Imp']:,.2f}", 1, 0, 'R')
        pdf.ln()

    # Totalizador Final
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(sum(col_widths[:-1]), 10, "TOTAL A ABONAR:", 0, 0, 'R')
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(col_widths[-1], 10, f"$ {total:,.2f}", 1, 1, 'R', 1)
    
    return pdf.output()