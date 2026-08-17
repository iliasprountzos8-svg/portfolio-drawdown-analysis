"""
Greek version. Plain, simple language, first person, no em dashes. Matches the simplified
English version (generate_report_pdf.py) after the data-integrity and bond-sleeve sections
were cut.
"""
import os
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
CHARTS = os.path.join(RESULTS, 'charts_gr')
OUT_PDF = os.path.join(HERE, '..', 'Portfolio_Drawdown_Research_Note_GR.pdf')

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
pdfmetrics.registerFont(TTFont('DejaVu', os.path.join(FONT_DIR, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Oblique', os.path.join(FONT_DIR, 'DejaVuSans-Oblique.ttf')))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold',
                               italic='DejaVu-Oblique', boldItalic='DejaVu-Bold')

NAVY = colors.HexColor('#1F3A5F')
SLATE = colors.HexColor('#6B7280')
GOLD = colors.HexColor('#B08D57')
INK = colors.HexColor('#111827')
BORDER = colors.HexColor('#D1D5DB')

styles = getSampleStyleSheet()

styles.add(ParagraphStyle('ReportTitle', fontName='DejaVu-Bold', fontSize=16, leading=20,
                           textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle('ReportSubtitle', fontName='DejaVu', fontSize=9.5, leading=13,
                           textColor=SLATE, spaceAfter=10))
styles.add(ParagraphStyle('SectionHead', fontName='DejaVu-Bold', fontSize=11.5, leading=14,
                           textColor=NAVY, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle('Body', fontName='DejaVu', fontSize=9, leading=13, textColor=INK,
                           alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle('Caption', fontName='DejaVu', fontSize=7.5, leading=10.5,
                           textColor=SLATE, spaceAfter=8))
styles.add(ParagraphStyle('Disclaimer', fontName='DejaVu-Oblique', fontSize=7.5, leading=10.5,
                           textColor=SLATE))
styles.add(ParagraphStyle('BulletItem', parent=styles['Body'], leftIndent=10, bulletIndent=0, spaceAfter=4))
styles.add(ParagraphStyle('CellHeader', fontName='DejaVu-Bold', fontSize=8, leading=10, textColor=colors.white))
styles.add(ParagraphStyle('CellBody', fontName='DejaVu', fontSize=8, leading=10.5, textColor=INK))

story = []

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.4)
    canvas.line(20*mm, 283*mm, 190*mm, 283*mm)
    canvas.setFont('DejaVu-Bold', 7.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(20*mm, 285*mm, 'ΣΗΜΕΙΩΜΑ ΕΡΕΥΝΑΣ ΧΑΡΤΟΦΥΛΑΚΙΟΥ')
    canvas.setFont('DejaVu', 7.5)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(190*mm, 285*mm, 'Αύγουστος 2026')
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(20*mm, 11*mm, 190*mm, 11*mm)
    canvas.setFont('DejaVu', 7)
    canvas.setFillColor(SLATE)
    canvas.drawString(20*mm, 7*mm, 'Δεν αποτελεί επενδυτική συμβουλή. Προσωπική έρευνα, μόνο για εκπαιδευτικούς σκοπούς.')
    canvas.drawRightString(190*mm, 7*mm, f'Σελίδα {doc.page}')
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
# ΣΕΛΙΔΑ 1
# =========================================================================
story.append(Paragraph('Μειώνει ο Χρυσός τον Κίνδυνο για Μια Μεγάλη Πτώση σε Χαρτοφυλάκιο Μεγάλης Διάρκειας;', styles['ReportTitle']))
story.append(Paragraph('Δοκιμή μιας κατανομής 51/12.75/7.87/25/3.38 (μετοχές, small-cap value, μακροπρόθεσμα ομόλογα, χρυσός, βραχυπρόθεσμα ομόλογα) με πραγματικά δεδομένα αγοράς, 1977 έως 2023', styles['ReportSubtitle']))
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=10))

story.append(Paragraph('Περίληψη', styles['SectionHead']))
story.append(Paragraph(
    'Πολύς κόσμος λέει ότι ο χρυσός προστατεύει ένα χαρτοφυλάκιο από μια μεγάλη πτώση, αλλά ήθελα να το ελέγξω '
    'πραγματικά αντί να το θεωρήσω δεδομένο. Έφτιαξα μια προσομοίωση Monte Carlo με πραγματικά ιστορικά μηνιαία '
    'δεδομένα από το 1977, και δοκίμασα ένα χαρτοφυλάκιο με 51% παγκόσμιες μετοχές, 12.75% small-cap value μετοχές, '
    '7.87% μακροπρόθεσμα ομόλογα, 25% χρυσό και 3.38% βραχυπρόθεσμα ομόλογα, σε ορίζοντα 30 ετών. Η προσθήκη χρυσού '
    'ρίχνει την πιθανότητα να χάσεις 50% ή περισσότερο από το χαρτοφυλάκιο, από περίπου 11.5% (χωρίς χρυσό) σε '
    'περίπου 2.6%. Το μεγαλύτερο μέρος αυτής της βελτίωσης έρχεται από τις πρώτες 10 ποσοστιαίες μονάδες χρυσού. '
    'Μετά από αυτό, περισσότερος χρυσός δεν βοηθάει πολύ παραπάνω.', styles['Body']))

story.append(Paragraph('Βασικοί Αριθμοί', styles['SectionHead']))
metrics_rows = [
    ['Μέγεθος', 'Με 25% Χρυσό', 'Χωρίς Χρυσό'],
    ['Πιθανότητα να χάσεις 50%+ (30 έτη)', '2.5 έως 2.6%', '11.5%'],
    ['Διάμεσο αποτέλεσμα μετά από 30 έτη (εφάπαξ)', '31.4 έως 31.6x', '46.4x'],
    ['Δείκτης Sharpe', '0.95', '0.92'],
    ['Πιθανότητα να χάσεις 30%+ (30 έτη)', '44 έως 45%', '65%'],
]
story.append(table_from_rows(metrics_rows, [80*mm, 55*mm, 35*mm]))
story.append(Paragraph('Οι αριθμοί ελέγχθηκαν σε 6+ ξεχωριστά runs (100.000 έως 1.000.000 προσομοιώσεις το καθένα), με πραγματικά μηνιαία δεδομένα από το 1977 έως το 2023.', styles['Caption']))

spacer(5)
story.append(Paragraph('Το Χαρτοφυλάκιο που Δοκίμασα', styles['SectionHead']))
alloc_rows = [
    ['Περιουσιακό Στοιχείο', 'Βάρος'],
    ['Παγκόσμιες μετοχές', '51.00%'],
    ['US small-cap value μετοχές', '12.75%'],
    ['Μακροπρόθεσμα κρατικά ομόλογα', '7.87%'],
    ['Χρυσός', '25.00%'],
    ['Βραχυπρόθεσμα κρατικά ομόλογα', '3.38%'],
]
story.append(table_from_rows(alloc_rows, [110*mm, 60*mm]))

story.append(PageBreak())

# =========================================================================
# ΣΕΛΙΔΑ 2
# =========================================================================
story.append(Paragraph('Πώς το Δοκίμασα', styles['SectionHead']))
story.append(Paragraph(
    '<b>Block bootstrap.</b> Αντί να μαντεύω πώς θα είναι οι μελλοντικές αποδόσεις, παίρνω πραγματικές ιστορικές '
    'μηνιαίες αποδόσεις και τις ενώνω τυχαία σε κομμάτια (blocks 12 μηνών) για να φτιάξω χιλιάδες πιθανά σενάρια '
    '30 ετών. Έτσι κρατάω πραγματικά μοτίβα στα δεδομένα, όπως το να συγκεντρώνονται μαζί οι κακοί μήνες, κάτι που '
    'μια απλή στατιστική εικασία θα το έχανε.', styles['Body']))
story.append(Paragraph(
    '<b>Δεδομένα.</b> Πραγματικές μηνιαίες αποδόσεις από το 1977 έως το 2023 (559 μήνες), για πέντε κατηγορίες: '
    'παγκόσμιες μετοχές, US small-cap value μετοχές, μακροπρόθεσμα κρατικά ομόλογα, χρυσός και βραχυπρόθεσμα '
    'κρατικά ομόλογα.', styles['Body']))
story.append(Paragraph(
    '<b>Έλεγχος walk-forward.</b> Δοκίμασα το χαρτοφυλάκιο και σε κάθε πραγματική περίοδο 30 ετών που έχει πράγματι '
    'συμβεί από το 1977 (199 περιόδους), όχι μόνο σε τυχαίες προσομοιώσεις. Έτσι σιγουρεύομαι ότι το αποτέλεσμα '
    'δεν είναι απλώς τύχη από ένα σημείο εκκίνησης.', styles['Body']))
story.append(Paragraph(
    '<b>Έλεγχος επιτοκίων.</b> Χώρισα το ιστορικό σε περιόδους που τα επιτόκια ανέβαιναν, κατέβαιναν ή έμεναν '
    'σταθερά, για να δω αν τα μακροπρόθεσμα ομόλογα βοηθούν ανεξάρτητα από το τι κάνουν τα επιτόκια.', styles['Body']))
story.append(Paragraph(
    '<b>Διπλός έλεγχος.</b> Πριν εμπιστευτώ οποιονδήποτε αριθμό, τον έτρεξα ανεξάρτητα τουλάχιστον έξι φορές '
    '(100.000 έως 1.000.000 προσομοιώσεις η κάθε μία), ώστε να μην αναφέρω ένα τυχερό run σαν να ήταν η πραγματική '
    'απάντηση.', styles['Body']))

spacer(3)
story.append(Paragraph('Απόδοση έναντι Κινδύνου ανά Βάρος Χρυσού', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'gold_comparison.png'), width=155*mm, height=155*mm*(3.2/7.2)))
story.append(Paragraph(
    'Προσομοίωση εφάπαξ επένδυσης, 100.000 προσομοιώσεις ανά κατανομή, ίδια μέθοδος και δεδομένα παντού. Το '
    'μεγαλύτερο μέρος της μείωσης κινδύνου γίνεται στις πρώτες 10 ποσοστιαίες μονάδες χρυσού. Μετά από αυτό '
    'ισοπεδώνεται και δεν είναι απόλυτα σταθερό (το 20% χρυσός δοκιμάζεται λίγο καλύτερα από το 25% εδώ). Δοκίμασα '
    'το 25% γιατί έχει τον καλύτερο δείκτη Sharpe από όσα έλεγξα, όχι επειδή περισσότερος χρυσός είναι πάντα '
    'καλύτερος.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# ΣΕΛΙΔΑ 3
# =========================================================================
story.append(Paragraph('Πώς Μοιάζουν τα Αποτελέσματα', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'distribution_histogram.png'), width=112*mm, height=112*mm*(3.6/6.5)))
story.append(Paragraph(
    'Προσομοίωση 50.000 δοκιμών, με ενδεικτική μηνιαία συνεισφορά €150. Το διάμεσο αποτέλεσμα εδώ είναι χαμηλότερο '
    'από τους εφάπαξ αριθμούς παραπάνω, κάτι λογικό: τα χρήματα που μπαίνουν αργότερα έχουν λιγότερο χρόνο να '
    'μεγαλώσουν σε σχέση με ένα εφάπαξ ποσό από την αρχή.', styles['Caption']))

spacer(2)
story.append(Paragraph('Προσομοιωμένες Πορείες Χαρτοφυλακίου, 30 Έτη', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'fan_chart.png'), width=112*mm, height=112*mm*(3.6/6.5)))
story.append(Paragraph(
    '300 μεμονωμένες προσομοιωμένες πορείες σαν λεπτές γραμμές, η διάμεση πορεία με έντονη γραμμή, και το εύρος '
    'μεταξύ 10ου και 90ού εκατοστημορίου σκιασμένο. Ίδιο χαρτοφυλάκιο και συνεισφορά όπως παραπάνω.', styles['Caption']))

spacer(3)
story.append(Paragraph('Τι Δεν Καλύπτει Αυτό', styles['SectionHead']))
for txt in [
    'Αυτή είναι μια προσομοίωση βασισμένη στο παρελθόν. Δεν μπορεί να προβλέψει κάτι που δεν έχει ξανασυμβεί, μόνο να το δοκιμάσει πάνω σε ό,τι έχει ήδη συμβεί.',
    'Κράτησα σταθερή την αναλογία των υπόλοιπων περιουσιακών στοιχείων ενώ δοκίμαζα διαφορετικά βάρη χρυσού. Δεν ξαναβελτιστοποίησα όλα τα βάρη ταυτόχρονα.',
    'Οι φόροι και τα έξοδα είναι εκτιμήσεις και εξαρτώνται από τη χώρα σου. Τα πραγματικά αποτελέσματα διαφέρουν ανά άτομο.',
]:
    story.append(Paragraph('- ' + txt, styles['BulletItem']))

spacer(3)
story.append(Paragraph('Συμπέρασμα', styles['SectionHead']))
story.append(Paragraph(
    'Ο χρυσός πράγματι μειώνει σημαντικά τον κίνδυνο μιας πολύ κακής πτώσης σε ένα χαρτοφυλάκιο μεγάλης διάρκειας '
    'με έμφαση σε μετοχές, περίπου 4 έως 5 φορές μείωση στο βάρος που δοκίμασα. Το μεγαλύτερο μέρος αυτού του '
    'οφέλους έρχεται μόνο από τις πρώτες 10 ποσοστιαίες μονάδες.', styles['Body']))

spacer(3)
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=4))
story.append(Paragraph(
    'Προσωπικό ερευνητικό έργο για εκπαιδευτικούς σκοπούς, δεν αποτελεί επενδυτική συμβουλή. Τα προσομοιωμένα '
    'αποτελέσματα δεν εγγυώνται τίποτα για το μέλλον. Ο κώδικας, τα δεδομένα και η πλήρης μέθοδος δημοσιεύονται '
    'μαζί με αυτό το σημείωμα.', styles['Disclaimer']))

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                         leftMargin=20*mm, rightMargin=20*mm, topMargin=19*mm, bottomMargin=11*mm,
                         title='Σημείωμα Έρευνας Χαρτοφυλακίου', author='Ηλίας Προύντζος')
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f'Saved {OUT_PDF}')
