"""
Generates the 4-page PDF research note. Equity-research-note style: header block, executive
summary, methodology, findings with tables and charts, a case study on the data-integrity issue
found while preparing this report, limitations, and conclusion.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)
from reportlab.platypus.flowables import KeepTogether

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
CHARTS = os.path.join(RESULTS, 'charts')
OUT_PDF = os.path.join(HERE, '..', 'Portfolio_Drawdown_Research_Note.pdf')

NAVY = colors.HexColor('#1F3A5F')
SLATE = colors.HexColor('#6B7280')
GOLD = colors.HexColor('#B08D57')
LIGHT = colors.HexColor('#F3F2EF')
INK = colors.HexColor('#111827')
BORDER = colors.HexColor('#D1D5DB')

styles = getSampleStyleSheet()

styles.add(ParagraphStyle('ReportTitle', fontName='Helvetica-Bold', fontSize=16, leading=19,
                           textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle('ReportSubtitle', fontName='Helvetica', fontSize=9.5, leading=13,
                           textColor=SLATE, spaceAfter=10))
styles.add(ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=11.5, leading=14,
                           textColor=NAVY, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=INK,
                           alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle('BodyBold', parent=styles['Body'], fontName='Helvetica-Bold'))
styles.add(ParagraphStyle('Caption', fontName='Helvetica', fontSize=7.5, leading=10,
                           textColor=SLATE, spaceAfter=8))
styles.add(ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))
styles.add(ParagraphStyle('TableCell', fontName='Helvetica', fontSize=8.5, textColor=INK))
styles.add(ParagraphStyle('Disclaimer', fontName='Helvetica-Oblique', fontSize=7.5, leading=10,
                           textColor=SLATE))
styles.add(ParagraphStyle('BulletItem', parent=styles['Body'], leftIndent=10, bulletIndent=0, spaceAfter=5))

story = []

def header_footer(canvas, doc):
    canvas.saveState()
    # Header rule
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.4)
    canvas.line(20*mm, 283*mm, 190*mm, 283*mm)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(20*mm, 285*mm, 'PORTFOLIO RESEARCH NOTE')
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(190*mm, 285*mm, 'August 2026')
    # Footer
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(20*mm, 15*mm, 190*mm, 15*mm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(SLATE)
    canvas.drawString(20*mm, 11*mm, 'Not financial advice — personal research, educational purposes only.')
    canvas.drawRightString(190*mm, 11*mm, f'Page {doc.page} of 4')
    canvas.restoreState()

def spacer(h=6):
    story.append(Spacer(1, h))

def table_from_rows(rows, col_widths, header=True):
    t = Table(rows, colWidths=col_widths)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, BORDER),
        ('TEXTCOLOR', (0, 0), (-1, -1), INK),
    ]
    if header:
        style += [
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style))
    return t

# =========================================================================
# PAGE 1 — Title, executive summary, key metrics
# =========================================================================
story.append(Paragraph('Does Gold Reduce Catastrophic Drawdown Risk in a Long-Horizon Portfolio?', styles['ReportTitle']))
story.append(Paragraph('A real-history Monte Carlo test of a 51/12.75/7.87/25/3.38 (equities / small-cap value / long bonds / gold / short bonds) allocation, 1977–2023', styles['ReportSubtitle']))
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=10))

story.append(Paragraph('Executive Summary', styles['SectionHead']))
story.append(Paragraph(
    'This note tests a common claim in portfolio construction directly, rather than assuming it: that adding gold to a '
    'stock-heavy allocation meaningfully reduces the probability of a catastrophic drawdown over a long investment '
    'horizon. Using a block-bootstrap Monte Carlo approach against real historical monthly returns back to 1977, the '
    'tested allocation reduces the probability of ever experiencing a 50%+ drawdown over 30 years from approximately '
    '11.5% (no gold) to approximately 2.5–2.6% — a real and material reduction, though not as extreme as an earlier, '
    'since-corrected estimate suggested. The reduction in tail risk is front-loaded: most of the benefit is captured '
    'in the first 10 percentage points of gold allocation, after which the relationship flattens.', styles['Body']))

story.append(Paragraph('Key Metrics', styles['SectionHead']))
metrics_rows = [
    ['Metric', 'Tested Allocation (25% Gold)', 'No-Gold Comparator'],
    ['P(drawdown ≥ 50% over 30yr)', '≈ 2.5–2.6%', '≈ 11.5%'],
    ['Median 30-year outcome (lump-sum multiple)', '≈ 31.4–31.6x', '≈ 46.4x'],
    ['Sharpe ratio', '≈ 0.95', '≈ 0.92'],
    ['P(drawdown ≥ 30% over 30yr)', '≈ 44–45%', '≈ 65%'],
]
story.append(table_from_rows(metrics_rows, [70*mm, 55*mm, 45*mm]))
story.append(Paragraph('Figures verified across 6+ independent bootstrap runs (100,000–1,000,000 trials each), block-bootstrap methodology, real historical monthly return data 1977–2023.', styles['Caption']))

spacer(8)
story.append(Paragraph('The Allocation Tested', styles['SectionHead']))
alloc_rows = [
    ['Asset Class', 'Weight'],
    ['Global equities', '51.00%'],
    ['US small-cap value', '12.75%'],
    ['Long-duration government bonds', '7.87%'],
    ['Gold', '25.00%'],
    ['Short-term government bonds', '3.38%'],
]
story.append(table_from_rows(alloc_rows, [110*mm, 60*mm]))

story.append(PageBreak())

# =========================================================================
# PAGE 2 — Methodology + gold allocation chart
# =========================================================================
story.append(Paragraph('Methodology', styles['SectionHead']))
story.append(Paragraph(
    '<b>Block bootstrap Monte Carlo.</b> Rather than assuming returns are normally distributed, this approach '
    'resamples real historical monthly-return blocks (12-month blocks) and stitches them into simulated 30-year '
    'paths. This preserves real sequencing and volatility clustering — the tendency of bad months to cluster '
    'together — that a purely parametric model would miss.', styles['Body']))
story.append(Paragraph(
    '<b>Data.</b> Real historical monthly returns, 1977–2023 (559 months), across five asset classes: global '
    'equities, US small-cap value, long-duration government bonds, gold, and short-term government bonds.', styles['Body']))
story.append(Paragraph(
    '<b>Walk-forward validation.</b> In addition to random bootstrap resampling, the allocation was tested against '
    'all 199 real, overlapping 30-year windows the dataset contains — every actual 30-year stretch that has '
    'occurred since 1977 — to confirm the result is not concentrated in a single fortunate starting period.', styles['Body']))
story.append(Paragraph(
    '<b>Regime-conditional testing.</b> History was split into rate-hiking, rate-cutting, and flat interest-rate '
    'regimes (via 10-year yield trend) to test whether the long-duration bond sleeve’s contribution depends on '
    'the prevailing rate environment.', styles['Body']))
story.append(Paragraph(
    '<b>Verification discipline.</b> Every headline figure in this note was reproduced across at least six '
    'independent bootstrap runs at varying trial counts (100,000 to 1,000,000 trials) before being reported, '
    'specifically to avoid presenting a single-run result as a stable finding.', styles['Body']))

spacer(6)
story.append(Paragraph('Return vs. Drawdown Risk Across Gold Allocations', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'gold_comparison.png'), width=160*mm, height=160*mm*(3.2/7.2)))
story.append(Paragraph(
    '100,000-trial lump-sum bootstrap per allocation, identical methodology and data throughout. The risk reduction '
    'is concentrated in the first 10 percentage points of gold allocation; beyond that the relationship is roughly '
    'flat and not strictly monotonic — 20% gold tests marginally better than 25% on tail risk in this dataset. '
    'The case for the tested 25% allocation rests on it carrying the best Sharpe ratio of the range tested, not on '
    'a claim that more gold is unconditionally better.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# PAGE 3 — Distribution + fan chart
# =========================================================================
story.append(Paragraph('Distribution of Simulated Outcomes', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'distribution_histogram.png'), width=165*mm, height=165*mm*(3.6/6.5)))
story.append(Paragraph(
    '50,000-trial block-bootstrap, dollar-cost-averaged €150/month contribution (illustrative), tested '
    'allocation. Median outcome under this contribution pattern is lower than the lump-sum figures above by '
    'construction — most contributed capital has less time to compound than a lump sum invested at time zero.',
    styles['Caption']))

spacer(4)
story.append(Paragraph('Simulated Portfolio Paths, 30-Year Horizon', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'fan_chart.png'), width=165*mm, height=165*mm*(3.6/6.5)))
story.append(Paragraph(
    '300 individual simulated paths (thin lines, low opacity so density reads as the signal), the median path '
    '(bold), and the 10th–90th percentile range (shaded band). Same allocation and contribution assumption as '
    'above.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# PAGE 4 — Data integrity case study, bond-sleeve resolution, limitations, conclusion
# =========================================================================
story.append(Paragraph('A Data-Integrity Finding', styles['SectionHead']))
story.append(Paragraph(
    'While preparing this note, a discrepancy surfaced: a previously "confirmed" tail-risk estimate for this exact '
    'allocation, computed against the same codebase, did not reproduce against current data. Diagnosis traced the '
    'cause to a data file that had been silently regenerated after the confirmation run that cited it — the '
    'underlying return series changed, but the confirmation was never re-executed against the corrected data. The '
    'figures in this note are the re-verified ones: reproduced independently across six-plus runs against the data '
    'that actually exists today, not carried forward from a run that could no longer be reproduced.', styles['Body']))
story.append(Paragraph(
    'This is reported here deliberately rather than quietly corrected, because it is a general failure mode worth '
    'naming: a result can go stale silently when the data feeding it changes and the analysis is not re-run. The '
    'process fix adopted going forward is version-controlling the underlying data files, so a change like this '
    'produces a visible diff instead of a silent drift.', styles['Body']))

spacer(4)
story.append(Paragraph('A Resolved Question: Is a Smaller Bond Sleeve Better?', styles['SectionHead']))
story.append(Paragraph(
    'An earlier finding suggested a smaller bond allocation (≈5% vs. the tested 15%) could outperform this '
    'allocation on median and worst-case outcome. Re-testing that comparison under a full realism gauntlet — '
    'lump-sum, realistic dollar-cost-averaged contributions, after fund fees and withholding tax, and conditioned on '
    'starting only from historically expensive markets — the smaller-bond-sleeve alternative loses on drawdown '
    'risk in every single test, and loses outright on median outcome once realistic costs are applied.', styles['Body']))
bond_rows = [
    ['Test', 'Tested Allocation\n(15% safety sleeve)', 'Alternative\n(5% safety sleeve)'],
    ['Lump-sum, P(drawdown ≥ 50%)', '2.60%', '3.95%'],
    ['DCA, P(drawdown ≥ 30%)', '17.11%', '27.36%'],
    ['Post-fee/tax median multiple', '28.60x', '28.19x'],
    ['CAPE-conditioned, P(drawdown ≥ 30%)', '21.44%', '31.91%'],
]
story.append(table_from_rows(bond_rows, [70*mm, 55*mm, 55*mm]))

spacer(6)
story.append(Paragraph('Limitations', styles['SectionHead']))
for txt in [
    'Simulated historical backtests, including block bootstrap methods, cannot capture genuinely unprecedented future regimes — only the range of behavior already observed in the sample period.',
    'The gold-allocation comparison uses a single fixed ratio between other sleeve weights; a full joint optimization across all weights simultaneously was not re-run against corrected data as part of this note.',
    'Tax and fee assumptions are illustrative and jurisdiction-specific; results will vary by investor.',
]:
    story.append(Paragraph('• ' + txt, styles['BulletItem']))

spacer(4)
story.append(Paragraph('Conclusion', styles['SectionHead']))
story.append(Paragraph(
    'Gold provides a real, material reduction in catastrophic-drawdown probability for a long-horizon equity-heavy '
    'portfolio — roughly a 4–5x reduction at the tested weight, concentrated mostly in the first 10 '
    'percentage points of allocation. The broader lesson of this exercise may matter as much as the specific number: '
    'a rigorously-produced result is only as good as the last time it was actually re-verified against real data.',
    styles['Body']))

spacer(10)
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=6))
story.append(Paragraph(
    'This is a personal research project produced for educational purposes and does not constitute financial, '
    'investment, or tax advice. Simulated historical outcomes do not guarantee future results. Source code, data, '
    'and full methodology are published alongside this note.', styles['Disclaimer']))

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                         leftMargin=20*mm, rightMargin=20*mm, topMargin=26*mm, bottomMargin=20*mm,
                         title='Portfolio Drawdown Research Note', author='Ilias Prountzos')
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f'Saved {OUT_PDF}')
