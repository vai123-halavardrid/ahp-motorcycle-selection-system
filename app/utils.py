import pandas as pd
import io
from datetime import datetime

def create_sample_excel():
    """Create a sample Excel file template for alternatives import"""
    # Create sample data
    data = {
        'Tên xe máy': [
            'Honda Wave Alpha',
            'Yamaha Exciter',
            'Honda Vision',
            'Yamaha Sirius'
        ],
        'Ngân sách': [
            18000000,
            50000000,
            30000000,
            20000000
        ],
        'Kiểu dáng': [
            'Xe số phổ thông',
            'Xe côn tay thể thao',
            'Xe tay ga hiện đại',
            'Xe số tiêu chuẩn'
        ],
        'Hiệu suất & Công suất': [
            '8.5 mã lực/8000 rpm',
            '15.4 mã lực/8500 rpm',
            '8.2 mã lực/7500 rpm',
            '9.3 mã lực/7500 rpm'
        ],
        'Tiết kiệm nhiên liệu': [
            '1.6L/100km',
            '2.2L/100km',
            '1.8L/100km',
            '1.7L/100km'
        ],
        'Công nghệ & Tính năng': [
            'Phanh đĩa, Đèn LED',
            'ABS, Đèn LED, Màn hình LCD',
            'Smart Key, Đèn LED, Cốp rộng',
            'Phanh đĩa, Đèn LED'
        ],
        'Kích thước & Trọng lượng': [
            '1.914x688x1.075 mm, 97kg',
            '1.975x665x1.085 mm, 117kg',
            '1.871x686x1.101 mm, 96kg',
            '1.907x680x1.075 mm, 96kg'
        ]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create Excel writer object
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mẫu nhập liệu')
        
        # Get the worksheet
        worksheet = writer.sheets['Mẫu nhập liệu']
        
        # Format headers
        for col in range(len(df.columns)):
            cell = worksheet.cell(row=1, column=col+1)
            cell.font = cell.font.copy(bold=True)
            
        # Auto-adjust columns' width
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    return output.getvalue()

def format_number(value):
    """Format numbers with thousand separators"""
    try:
        return "{:,.0f}".format(value)
    except:
        return value

def generate_pdf_report(results, chart_path):
    """Generate PDF report with results and chart"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Create story (content)
    story = []
    
    # Add title
    story.append(Paragraph('Kết quả phân tích AHP', title_style))
    story.append(Spacer(1, 12))
    
    # Add results table
    data = [['Xếp hạng', 'Tên phương án', 'Điểm số', 'Tỷ lệ']]
    for result in results:
        data.append([
            str(result['rank']),
            result['name'],
            f"{result['score']:.4f}",
            f"{result['percentage']:.1f}%"
        ])
    
    table = Table(data, colWidths=[60, 200, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Add chart
    if chart_path:
        img = Image(chart_path)
        img.drawHeight = 4*inch
        img.drawWidth = 6*inch
        story.append(img)
    
    # Add timestamp
    story.append(Spacer(1, 20))
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph(f'Báo cáo được tạo lúc: {timestamp}', normal_style))
    
    # Build PDF
    doc.build(story)
    
    return buffer.getvalue()
