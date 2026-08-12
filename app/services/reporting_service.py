import pdfkit
import pandas as pd
from flask import render_template, make_response
import os
from datetime import datetime

class ReportingService:
    @staticmethod
    def generate_pdf(template_name, context, filename):
        """
        Generates a premium PDF report from an HTML template.
        """
        html = render_template(template_name, **context)
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None,
            'quiet': ''
        }
        
        try:
            # Try to find wkhtmltopdf if not in path (Common on Windows)
            config = None
            if os.name == 'nt':
                # Common paths for Windows
                paths = [
                    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                    r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
                ]
                for p in paths:
                    if os.path.exists(p):
                        config = pdfkit.configuration(wkhtmltopdf=p)
                        break
            
            pdf = pdfkit.from_string(html, False, options=options, configuration=config)
            
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        except Exception as e:
            # Fallback: If pdfkit fails (e.g. binary missing), we can return HTML with a print script
            print(f"PDF Generation Error: {e}")
            return html # Returning HTML so user can print via browser if needed

    @staticmethod
    def generate_excel(data, columns, filename):
        """
        Generates a professional Excel report.
        """
        df = pd.DataFrame(data, columns=columns)
        
        # Create a temporary file path
        temp_path = f"temp_{filename}"
        
        # Use pandas ExcelWriter for better formatting
        writer = pd.ExcelWriter(temp_path, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Report')
        
        # Access the openpyxl workbook and sheet to add styles
        workbook = writer.book
        worksheet = writer.sheets['Report']
        
        # Add some basic styling
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        header_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            
        writer.close()
        
        with open(temp_path, 'rb') as f:
            excel_data = f.read()
            
        os.remove(temp_path)
        
        response = make_response(excel_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
