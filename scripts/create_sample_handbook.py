"""
scripts/create_sample_handbook.py — Generates a sample official MANIT academic regulations PDF.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "data" / "raw" / "manit_academic_regulations.pdf"

def generate_pdf():
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("MAULANA AZAD NATIONAL INSTITUTE OF TECHNOLOGY, BHOPAL", title_style))
    elements.append(Paragraph("ACADEMIC REGULATIONS & ORDINANCES (B.TECH / B.PLAN)", h1_style))
    elements.append(Spacer(1, 10))
    
    # Section 1: Attendance
    elements.append(Paragraph("Section 1: Attendance Requirements", h1_style))
    elements.append(Paragraph(
        "1.1 Minimum Attendance: Every student must maintain a minimum attendance of 75% in each registered course (lectures, tutorials, and practicals) to be eligible to appear in the End-Semester Examination.",
        body_style
    ))
    elements.append(Paragraph(
        "1.2 Condonation of Shortage: A shortage of attendance up to 10% (i.e. between 65% and 75%) may be condoned by the Director / Dean (Academic) on genuine medical grounds or sanctioned institutional representation (sports/cultural/conferences), supported by valid medical certificates and recommendations from the Head of the Department.",
        body_style
    ))
    elements.append(Paragraph(
        "1.3 Disqualification: Students with attendance below 65% under any circumstances will not be allowed to appear in the End-Semester Examination and shall be awarded an 'F' grade or 'Debarred' (DE) in that course.",
        body_style
    ))
    elements.append(Spacer(1, 10))
    
    # Section 2: Credit System & Degree Requirements
    elements.append(Paragraph("Section 2: Credit System & Graduation Requirements", h1_style))
    elements.append(Paragraph(
        "2.1 Total Credits Required: A regular student admitted to the four-year B.Tech program must successfully earn a minimum of 160 to 170 credits (as prescribed by the specific engineering department) to qualify for the award of the B.Tech Degree.",
        body_style
    ))
    elements.append(Paragraph(
        "2.2 Duration: The normal duration of the B.Tech program is 8 semesters (4 years). The maximum permissible duration to clear all academic requirements is 12 semesters (6 years).",
        body_style
    ))
    elements.append(Paragraph(
        "2.3 Minimum CGPA for Graduation: A student must obtain a minimum Cumulative Grade Point Average (CGPA) of 5.0 at the end of the final semester to be eligible for the degree.",
        body_style
    ))
    elements.append(Spacer(1, 10))
    
    # Section 3: Grading System
    elements.append(Paragraph("Section 3: Grading System and Performance Evaluation", h1_style))
    elements.append(Paragraph(
        "3.1 10-Point Scale: The institute follows a 10-point letter grading system. The grades and corresponding grade points are shown below:",
        body_style
    ))
    
    table_data = [
        ["Grade", "Grade Point", "Description"],
        ["A+", "10", "Outstanding"],
        ["A", "9", "Excellent"],
        ["B+", "8", "Very Good"],
        ["B", "7", "Good"],
        ["C+", "6", "Fair / Above Average"],
        ["C", "5", "Average"],
        ["D", "4", "Marginal / Pass"],
        ["F", "0", "Fail / Backlog"],
    ]
    t = Table(table_data, colWidths=[80, 90, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))
    
    # Section 4: Backlog and CGPA
    elements.append(Paragraph("Section 4: Backlog Policy and CGPA Calculation", h1_style))
    elements.append(Paragraph(
        "4.1 Clearing Backlogs: If a student secures an 'F' grade in any core course, it is treated as a backlog. The student must re-appear in the backlog examination during the subsequent semester or during the Summer Supplementary Term.",
        body_style
    ))
    elements.append(Paragraph(
        "4.2 Impact on CGPA: An 'F' grade contributes 0 grade points to the SGPA/CGPA calculation. When the backlog course is cleared, the new grade replaces the 'F' grade in the calculation of the Cumulative Grade Point Average (CGPA), but the backlog attempt remains documented in the permanent grade sheet.",
        body_style
    ))
    elements.append(Paragraph(
        "4.3 Honors Criteria: To graduate with B.Tech (Honors), a candidate must earn an additional 18-20 credits through designated honors courses and maintain a minimum CGPA of 8.5 without any backlog history throughout the entire duration of the program.",
        body_style
    ))
    elements.append(Spacer(1, 10))
    
    # Section 5: Hostel Rules
    elements.append(Paragraph("Section 5: Hostel Regulations and Curfew Policies", h1_style))
    elements.append(Paragraph(
        "5.1 Curfew Timings: All residential students must return to their respective hostels by the designated curfew hour. For First Year Hostels, entry closes strictly at 9:00 PM. For Senior Hostels, the curfew is 10:00 PM on weekdays and 10:30 PM on weekends.",
        body_style
    ))
    elements.append(Paragraph(
        "5.2 Night Out / Leave: Any student intending to stay out overnight must submit an online leave application approved by the Hostel Warden and verified with parental consent prior to departure.",
        body_style
    ))
    elements.append(Paragraph(
        "5.3 Disciplinary Conduct: Ragging in any form inside campus or hostels is strictly prohibited under the Supreme Court of India guidelines and will result in immediate suspension and criminal proceedings.",
        body_style
    ))
    
    doc.build(elements)
    print(f"Sample handbook created at: {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_pdf()
