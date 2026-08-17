"""
Generates the PDF research note. Plain, simple language, written in first person, no em dashes.
Shorter than the original draft since two sections were cut.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
CHARTS = os.path.join(RESULTS, 'charts')
OUT_PDF = os.path.join(HERE, '..', 'Portfolio_Drawdown_Research_Note.pdf')

NAVY = colors.HexColor('#1F3A5F')
SLATE = colors.HexColor('#6B7280')
GOLD = colors.HexColor('#B08D57')
INK = colors.HexColor('#111827')
BORDER = colors.HexColor('#D1D5DB')

styles = getSampleStyleSheet()

styles.add(ParagraphStyle('ReportTitle', fontName='Helvetica-Bold', fontSize=16, leading=19,
                           textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle('ReportSubtitle', fontName='Helvetica', fontSize=9.5, leading=13,
                           textColor=SLATE, spaceAfter=10))
styles.add(ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=11.5, leading=14,
                           textColor=NAVY, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=INK,
                           alignment=TA_JUSTIFY, spaceAfter=7))
styles.add(ParagraphStyle('Caption', fontName='Helvetica', fontSize=7.5, leading=10,
                           textColor=SLATE, spaceAfter=8))
styles.add(ParagraphStyle('Disclaimer', fontName='Helvetica-Oblique', fontSize=7.5, leading=10,
                           textColor=SLATE))
styles.add(ParagraphStyle('BulletItem', parent=styles['Body'], leftIndent=10, bulletIndent=0, spaceAfter=5))
styles.add(ParagraphStyle('CellHeader', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=colors.white))
styles.add(ParagraphStyle('CellBody', fontName='Helvetica', fontSize=8.5, leading=10.5, textColor=INK))

story = []

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.4)
    canvas.line(20*mm, 283*mm, 190*mm, 283*mm)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(20*mm, 285*mm, 'PORTFOLIO RESEARCH NOTE')
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(190*mm, 285*mm, 'August 2026')
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(20*mm, 11*mm, 190*mm, 11*mm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(SLATE)
    canvas.drawString(20*mm, 7*mm, 'Not financial advice. Personal research, for education only.')
    canvas.drawRightString(190*mm, 7*mm, f'Page {doc.page}')
    canvas.restoreState()

def spacer(h=6):
    story.append(Spacer(1, h))

def table_from_rows(rows, col_widths, header=True):
    wrapped = []
    for r_i, row in enumerate(rows):
        is_header = header and r_i == 0
        style = styles['CellHeader'] if is_header else styles['CellBody']
        wrapped.append([Paragraph(str(cell).replace('\n', '<br/>'), style) for cell in row])
    t = Table(wrapped, colWidths=col_widths)
    tstyle = [
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    if header:
        tstyle.append(('BACKGROUND', (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(tstyle))
    return t

# =========================================================================
# PAGE 1
# =========================================================================
story.append(Paragraph('Does Gold Reduce the Risk of a Big Crash in a Long-Term Portfolio?', styles['ReportTitle']))
story.append(Paragraph('A test of a 51/12.75/7.87/25/3.38 allocation (stocks, small-cap value, long bonds, gold, short bonds) using real market data, 1977 to 2023', styles['ReportSubtitle']))
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=10))

story.append(Paragraph('Summary', styles['SectionHead']))
story.append(Paragraph(
    'People often say gold protects a portfolio from a bad crash, but I wanted to actually check that instead of '
    'assuming it. I built a Monte Carlo simulation using real historical monthly returns going back to 1977, and '
    'tested a portfolio made of 51% global stocks, 12.75% small-cap value stocks, 7.87% long-term bonds, 25% gold, '
    'and 3.38% short-term bonds over a 30-year period. Adding gold drops the chance of ever losing 50% or more of '
    'the portfolio from about 11.5% (no gold) to about 2.6%. Most of that improvement comes from the first 10 '
    'percentage points of gold. After that, adding more gold does not help much more.', styles['Body']))

story.append(Paragraph('Key Numbers', styles['SectionHead']))
metrics_rows = [
    ['Metric', 'With 25% Gold', 'No Gold'],
    ['Chance of losing 50% or more (30yr)', '2.5 to 2.6%', '11.5%'],
    ['Median result after 30yr (lump sum)', '31.4 to 31.6x', '46.4x'],
    ['Sharpe ratio', '0.95', '0.92'],
    ['Chance of losing 30% or more (30yr)', '44 to 45%', '65%'],
]
story.append(table_from_rows(metrics_rows, [80*mm, 55*mm, 35*mm]))
story.append(Paragraph('These numbers were checked across 6+ separate simulation runs (100,000 to 1,000,000 trials each), using real monthly return data from 1977 to 2023.', styles['Caption']))

spacer(6)
story.append(Paragraph('The Portfolio I Tested', styles['SectionHead']))
alloc_rows = [
    ['Asset', 'Weight'],
    ['Global stocks', '51.00%'],
    ['US small-cap value stocks', '12.75%'],
    ['Long-term government bonds', '7.87%'],
    ['Gold', '25.00%'],
    ['Short-term government bonds', '3.38%'],
]
story.append(table_from_rows(alloc_rows, [110*mm, 60*mm]))

story.append(PageBreak())

# =========================================================================
# PAGE 2
# =========================================================================
story.append(Paragraph('How I Tested This', styles['SectionHead']))
story.append(Paragraph(
    '<b>Block bootstrap.</b> Instead of guessing what future returns might look like, I take real historical '
    'monthly returns and randomly stitch chunks of them together (12-month blocks) to build thousands of possible '
    '30-year futures. This keeps real patterns in the data, like bad months clustering together, that a simple '
    'statistical guess would miss.', styles['Body']))
story.append(Paragraph(
    '<b>Data.</b> Real monthly returns from 1977 to 2023 (559 months), for five asset types: global stocks, US '
    'small-cap value stocks, long-term government bonds, gold, and short-term government bonds.', styles['Body']))
story.append(Paragraph(
    '<b>Walk-forward check.</b> I also tested the portfolio against every real 30-year period that has actually '
    'happened since 1977 (199 of them), not just random simulations. This makes sure the result is not just luck '
    'from one starting point.', styles['Body']))
story.append(Paragraph(
    '<b>Interest rate check.</b> I split history into periods when rates were rising, falling, or flat, to see if '
    'the long-term bonds still help no matter what rates are doing.', styles['Body']))
story.append(Paragraph(
    '<b>Double-checking.</b> Before trusting any number, I ran it independently at least six times (100,000 to '
    '1,000,000 trials each), so I was not reporting one lucky run as if it were the real answer.', styles['Body']))

spacer(4)
story.append(Paragraph('Return vs. Risk by Gold Weight', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'gold_comparison.png'), width=160*mm, height=160*mm*(3.2/7.2)))
story.append(Paragraph(
    'Lump-sum simulation, 100,000 trials per allocation, same method and data throughout. Most of the risk '
    'reduction happens in the first 10 percentage points of gold. After that it flattens out and is not perfectly '
    'consistent (20% gold actually tests slightly better than 25% here). I still tested 25% because it has the '
    'best Sharpe ratio of the range I checked, not because more gold is always better.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# PAGE 3
# =========================================================================
story.append(Paragraph('What the Outcomes Look Like', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'distribution_histogram.png'), width=122*mm, height=122*mm*(3.6/6.5)))
story.append(Paragraph(
    '50,000-trial simulation, using a €150/month contribution as an example. The median result here is lower than '
    'the lump-sum numbers above, which makes sense: money contributed later has less time to grow than a lump sum '
    'invested at the start.', styles['Caption']))

spacer(2)
story.append(Paragraph('Simulated Portfolio Paths Over 30 Years', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'fan_chart.png'), width=122*mm, height=122*mm*(3.6/6.5)))
story.append(Paragraph(
    '300 individual simulated paths shown as thin lines, the median path in bold, and the range between the 10th '
    'and 90th percentile shaded. Same portfolio and contribution as above.', styles['Caption']))

spacer(3)
story.append(Paragraph('What This Does Not Cover', styles['SectionHead']))
for txt in [
    'This is a simulation based on the past. It cannot predict something that has never happened before, only test against what already has.',
    'I kept the ratio between the other assets fixed while testing different gold weights. I did not re-optimize every weight at once.',
    'Taxes and fees are estimates and depend on where you live. Real results will differ per person.',
]:
    story.append(Paragraph('- ' + txt, styles['BulletItem']))

spacer(3)
story.append(Paragraph('Conclusion', styles['SectionHead']))
story.append(Paragraph(
    'Gold does meaningfully lower the risk of a really bad crash in a long-term, stock-heavy portfolio, roughly a '
    '4 to 5x reduction at the weight I tested. Most of that benefit comes from just the first 10 percentage points.',
    styles['Body']))

spacer(4)
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=4))
story.append(Paragraph(
    'Personal research project for education purposes, not financial or investment advice. Simulated results do '
    'not guarantee anything about the future. Code, data, and full method are published alongside this note.',
    styles['Disclaimer']))

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                         leftMargin=20*mm, rightMargin=20*mm, topMargin=19*mm, bottomMargin=11*mm,
                         title='Portfolio Drawdown Research Note', author='Ilias Prountzos')
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f'Saved {OUT_PDF}')
