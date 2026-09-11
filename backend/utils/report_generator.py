from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from datetime import datetime
from typing import Dict, List
import io

class ReportGenerator:
    """Generate PDF reports for diagnoses"""
    
    def __init__(self):
        self.page_size = letter
        self.margin = 0.5 * inch
    
    def generate_diagnosis_report(
        self,
        patient_info: Dict,
        diagnosis_info: Dict,
        blood_values: Dict = None,
        image_findings: List[str] = None
    ) -> bytes:
        """
        Generate a comprehensive diagnosis report as PDF
        """
        # Create BytesIO buffer
        buffer = io.BytesIO()
        
        # Create PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build document
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("🏥 Medical Diagnosis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report date
        date_text = f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information Section
        story.append(Paragraph("Patient Information", styles['Heading2']))
        patient_data = [
            ["Name:", patient_info.get("name", "N/A")],
            ["Age:", str(patient_info.get("age", "N/A"))],
            ["Gender:", patient_info.get("gender", "N/A")],
            ["ID:", str(patient_info.get("id", "N/A"))],
        ]
        patient_table = Table(patient_data, colWidths=[1.5*inch, 3.5*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Diagnosis Section
        story.append(Paragraph("Diagnosis Results", styles['Heading2']))
        diagnosis_data = [
            ["Primary Diagnosis:", diagnosis_info.get("primary_diagnosis", "N/A")],
            ["Probability:", f"{diagnosis_info.get('primary_probability', 0) * 100:.1f}%"],
            ["Severity:", diagnosis_info.get("severity", "N/A").upper()],
        ]
        diagnosis_table = Table(diagnosis_data, colWidths=[1.5*inch, 3.5*inch])
        diagnosis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        story.append(diagnosis_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Blood Test Results (if available)
        if blood_values:
            story.append(Paragraph("Blood Test Results", styles['Heading2']))
            blood_data = [["Test", "Value", "Unit"]]
            for test, value in blood_values.items():
                blood_data.append([test.replace("_", " ").title(), str(value), "mg/dL"])
            
            blood_table = Table(blood_data, colWidths=[2*inch, 1.5*inch, 1*inch])
            blood_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
            ]))
            story.append(blood_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations Section
        story.append(Paragraph("Recommendations", styles['Heading2']))
        recommendations = diagnosis_info.get("recommended_tests", [])
        recommendations_text = "<br/>".join([f"• {rec}" for rec in recommendations])
        story.append(Paragraph(recommendations_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = "<i>This report is for informational purposes only. Always consult with a qualified healthcare professional for diagnosis and treatment.</i>"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

# Singleton
_report_generator = None

def get_report_generator() -> ReportGenerator:
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator