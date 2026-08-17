"""
Greek version of the 4-page PDF research note. Uses DejaVu Sans (bundled with matplotlib)
registered as a Unicode font, since reportlab's built-in Helvetica cannot render Greek glyphs.
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

# --- Register a Unicode (Greek-capable) font; Helvetica cannot render Greek ---
FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
pdfmetrics.registerFont(TTFont('DejaVu', os.path.join(FONT_DIR, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Oblique', os.path.join(FONT_DIR, 'DejaVuSans-Oblique.ttf')))
# Map <b>/<i> tags to the bold/oblique variants when used inside 'DejaVu'-styled Paragraphs
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
                           textColor=NAVY, spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle('Body', fontName='DejaVu', fontSize=8.5, leading=12, textColor=INK,
                           alignment=TA_JUSTIFY, spaceAfter=5))
styles.add(ParagraphStyle('Caption', fontName='DejaVu', fontSize=7.5, leading=10.5,
                           textColor=SLATE, spaceAfter=8))
styles.add(ParagraphStyle('Disclaimer', fontName='DejaVu-Oblique', fontSize=7.5, leading=10.5,
                           textColor=SLATE))
styles.add(ParagraphStyle('BulletItem', parent=styles['Body'], leftIndent=10, bulletIndent=0, spaceAfter=3))
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
    canvas.drawString(20*mm, 7*mm, 'Δεν αποτελεί επενδυτική συμβουλή — προσωπική έρευνα, εκπαιδευτικοί σκοποί.')
    canvas.drawRightString(190*mm, 7*mm, f'Σελίδα {doc.page} από 4')
    canvas.restoreState()

def spacer(h=6):
    story.append(Spacer(1, h))

def table_from_rows(rows, col_widths, header=True):
    # Wrap every cell in a Paragraph so long Greek text wraps within the column instead of
    # overflowing into the next one (plain strings in reportlab Table do not auto-wrap).
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
# ΣΕΛΙΔΑ 1 — Τίτλος, περίληψη, βασικά μεγέθη
# =========================================================================
story.append(Paragraph('Μειώνει ο Χρυσός τον Κίνδυνο Καταστροφικής Πτώσης σε Χαρτοφυλάκιο Μεγάλου Ορίζοντα;', styles['ReportTitle']))
story.append(Paragraph('Δοκιμή Monte Carlo με πραγματικά ιστορικά δεδομένα για κατανομή 51/12.75/7.87/25/3.38 (μετοχές / small-cap value / μακροπρόθεσμα ομόλογα / χρυσός / βραχυπρόθεσμα ομόλογα), 1977–2023', styles['ReportSubtitle']))
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=10))

story.append(Paragraph('Περίληψη', styles['SectionHead']))
story.append(Paragraph(
    'Αυτό το σημείωμα ελέγχει άμεσα μια κοινή παραδοχή στη σύνθεση χαρτοφυλακίου, αντί να τη θεωρεί δεδομένη: ότι η '
    'προσθήκη χρυσού σε ένα χαρτοφυλάκιο με μεγάλη έκθεση σε μετοχές μειώνει ουσιωδώς την πιθανότητα καταστροφικής '
    'πτώσης σε μεγάλο επενδυτικό ορίζοντα. Χρησιμοποιώντας προσομοίωση Monte Carlo με block bootstrap πάνω σε '
    'πραγματικά ιστορικά μηνιαία δεδομένα από το 1977, η δοκιμασμένη κατανομή μειώνει την πιθανότητα εμφάνισης '
    'πτώσης ≥50% σε ορίζοντα 30 ετών από περίπου 11.5% (χωρίς χρυσό) σε περίπου 2.5–2.6% — μια πραγματική και '
    'ουσιαστική μείωση, αν και όχι τόσο ακραία όσο υποδείκνυε μια προγενέστερη εκτίμηση που στη συνέχεια διορθώθηκε. '
    'Η μείωση του κινδύνου ουράς είναι συγκεντρωμένη στην αρχή: το μεγαλύτερο μέρος του οφέλους αποδίδεται στις '
    'πρώτες 10 ποσοστιαίες μονάδες κατανομής σε χρυσό, μετά τις οποίες η σχέση ισοπεδώνεται.', styles['Body']))

story.append(Paragraph('Βασικά Μεγέθη', styles['SectionHead']))
metrics_rows = [
    ['Μέγεθος', 'Δοκιμασμένη Κατανομή (25% Χρυσός)', 'Χωρίς Χρυσό'],
    ['Π(πτώση ≥ 50% σε 30 έτη)', '≈ 2.5–2.6%', '≈ 11.5%'],
    ['Διάμεσο αποτέλεσμα 30ετίας (εφάπαξ)', '≈ 31.4–31.6x', '≈ 46.4x'],
    ['Δείκτης Sharpe', '≈ 0.95', '≈ 0.92'],
    ['Π(πτώση ≥ 30% σε 30 έτη)', '≈ 44–45%', '≈ 65%'],
]
story.append(table_from_rows(metrics_rows, [65*mm, 60*mm, 45*mm]))
story.append(Paragraph('Τα μεγέθη επιβεβαιώθηκαν σε 6+ ανεξάρτητα runs (100.000–1.000.000 προσομοιώσεις έκαστο), μεθοδολογία block bootstrap, πραγματικά ιστορικά μηνιαία δεδομένα 1977–2023.', styles['Caption']))

spacer(5)
story.append(Paragraph('Η Δοκιμασμένη Κατανομή', styles['SectionHead']))
alloc_rows = [
    ['Κατηγορία Περιουσιακού Στοιχείου', 'Βάρος'],
    ['Παγκόσμιες μετοχές', '51.00%'],
    ['US small-cap value μετοχές', '12.75%'],
    ['Μακροπρόθεσμα κρατικά ομόλογα', '7.87%'],
    ['Χρυσός', '25.00%'],
    ['Βραχυπρόθεσμα κρατικά ομόλογα', '3.38%'],
]
story.append(table_from_rows(alloc_rows, [110*mm, 60*mm]))

story.append(PageBreak())

# =========================================================================
# ΣΕΛΙΔΑ 2 — Μεθοδολογία + γράφημα σύγκρισης χρυσού
# =========================================================================
story.append(Paragraph('Μεθοδολογία', styles['SectionHead']))
story.append(Paragraph(
    '<b>Block Bootstrap Monte Carlo.</b> Αντί να υποθέτουμε ότι οι αποδόσεις ακολουθούν κανονική κατανομή, η μέθοδος '
    'αυτή δειγματοληπτεί πραγματικά ιστορικά μηνιαία τμήματα αποδόσεων (blocks 12 μηνών) και τα συνενώνει σε '
    'προσομοιωμένες πορείες 30 ετών. Αυτό διατηρεί την πραγματική χρονική αλληλουχία και τη συσσώρευση '
    'μεταβλητότητας — την τάση των κακών μηνών να συγκεντρώνονται μαζί — κάτι που ένα καθαρά παραμετρικό μοντέλο '
    'θα παρέβλεπε.', styles['Body']))
story.append(Paragraph(
    '<b>Δεδομένα.</b> Πραγματικές ιστορικές μηνιαίες αποδόσεις, 1977–2023 (559 μήνες), σε πέντε κατηγορίες '
    'περιουσιακών στοιχείων: παγκόσμιες μετοχές, US small-cap value μετοχές, μακροπρόθεσμα κρατικά ομόλογα, χρυσός '
    'και βραχυπρόθεσμα κρατικά ομόλογα.', styles['Body']))
story.append(Paragraph(
    '<b>Επικύρωση walk-forward.</b> Πέρα από την τυχαία δειγματοληψία bootstrap, η κατανομή δοκιμάστηκε και στα 199 '
    'πραγματικά, επικαλυπτόμενα παράθυρα 30ετίας που περιέχει το σύνολο δεδομένων — κάθε πραγματικό διάστημα 30 '
    'ετών που έχει συμβεί από το 1977 — για να επιβεβαιωθεί ότι το αποτέλεσμα δεν συγκεντρώνεται σε μία τυχερή '
    'περίοδο εκκίνησης.', styles['Body']))
story.append(Paragraph(
    '<b>Δοκιμή υπό συνθήκες (regime-conditional).</b> Το ιστορικό διαχωρίστηκε σε περιόδους αύξησης, μείωσης και '
    'σταθερότητας επιτοκίων (μέσω τάσης 10ετούς απόδοσης) για να ελεγχθεί αν η συνεισφορά του μακροπρόθεσμου '
    'ομολογιακού σκέλους εξαρτάται από το επικρατούν καθεστώς επιτοκίων.', styles['Body']))
story.append(Paragraph(
    '<b>Πειθαρχία επαλήθευσης.</b> Κάθε βασικό μέγεθος σε αυτό το σημείωμα αναπαρήχθη σε τουλάχιστον έξι ανεξάρτητα '
    'runs bootstrap με διαφορετικό αριθμό προσομοιώσεων (100.000 έως 1.000.000) πριν αναφερθεί, ειδικά ώστε να '
    'αποφευχθεί η παρουσίαση ενός μεμονωμένου run ως σταθερού ευρήματος.', styles['Body']))

spacer(4)
story.append(Paragraph('Απόδοση έναντι Κινδύνου Πτώσης ανά Κατανομή Χρυσού', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'gold_comparison.png'), width=160*mm, height=160*mm*(3.2/7.2)))
story.append(Paragraph(
    'Bootstrap εφάπαξ επένδυσης, 100.000 προσομοιώσεις ανά κατανομή, ίδια μεθοδολογία και δεδομένα σε όλο το '
    'σημείωμα. Η μείωση κινδύνου συγκεντρώνεται στις πρώτες 10 ποσοστιαίες μονάδες κατανομής σε χρυσό· πέρα από '
    'αυτό η σχέση είναι σχετικά επίπεδη και όχι αυστηρά μονότονη — το 20% χρυσός δοκιμάζεται οριακά καλύτερα από '
    'το 25% ως προς τον κίνδυνο ουράς σε αυτό το σύνολο δεδομένων. Η επιλογή της δοκιμασμένης κατανομής 25% '
    'στηρίζεται στο ότι έχει τον καλύτερο δείκτη Sharpe του εύρους που δοκιμάστηκε, όχι στον ισχυρισμό ότι '
    'περισσότερος χρυσός είναι πάντα καλύτερος.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# ΣΕΛΙΔΑ 3 — Κατανομή + fan chart
# =========================================================================
story.append(Paragraph('Κατανομή Προσομοιωμένων Αποτελεσμάτων', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'distribution_histogram.png'), width=165*mm, height=165*mm*(3.6/6.5)))
story.append(Paragraph(
    'Block bootstrap 50.000 προσομοιώσεων, με ενδεικτική μηνιαία συνεισφορά €150 (dollar-cost averaging), '
    'δοκιμασμένη κατανομή. Το διάμεσο αποτέλεσμα υπό αυτό το μοτίβο συνεισφοράς είναι χαμηλότερο από τα εφάπαξ '
    'μεγέθη παραπάνω εκ κατασκευής — το μεγαλύτερο μέρος του συνεισφερόμενου κεφαλαίου έχει λιγότερο χρόνο να '
    'ανατοκιστεί σε σχέση με ένα εφάπαξ ποσό επενδυμένο από την αρχή.', styles['Caption']))

spacer(4)
story.append(Paragraph('Προσομοιωμένες Πορείες Χαρτοφυλακίου, Ορίζοντας 30 Ετών', styles['SectionHead']))
story.append(Image(os.path.join(CHARTS, 'fan_chart.png'), width=165*mm, height=165*mm*(3.6/6.5)))
story.append(Paragraph(
    '300 μεμονωμένες προσομοιωμένες πορείες (λεπτές γραμμές, χαμηλή διαφάνεια ώστε η πυκνότητα να αποτελεί το '
    'σήμα), η διάμεση πορεία (έντονη γραμμή), και το εύρος 10ου–90ού εκατοστημορίου (σκιασμένη ζώνη). Ίδια '
    'κατανομή και υπόθεση συνεισφοράς όπως παραπάνω.', styles['Caption']))

story.append(PageBreak())

# =========================================================================
# ΣΕΛΙΔΑ 4 — Εύρημα ακεραιότητας δεδομένων, επίλυση ερωτήματος ομολόγων, περιορισμοί, συμπέρασμα
# =========================================================================
story.append(Paragraph('Ένα Εύρημα Ακεραιότητας Δεδομένων', styles['SectionHead']))
story.append(Paragraph(
    'Κατά την προετοιμασία αυτού του σημειώματος, εντοπίστηκε μια απόκλιση: μια προηγουμένως "επιβεβαιωμένη" '
    'εκτίμηση κινδύνου ουράς για αυτήν ακριβώς την κατανομή, υπολογισμένη με τον ίδιο κώδικα, δεν αναπαραγόταν με '
    'τα τρέχοντα δεδομένα. Η διάγνωση εντόπισε την αιτία σε ένα αρχείο δεδομένων που είχε αναδημιουργηθεί σιωπηλά '
    'μετά το run επιβεβαίωσης που το ανέφερε — η υποκείμενη σειρά αποδόσεων άλλαξε, αλλά η επιβεβαίωση δεν '
    'ξανατρέχτηκε πάνω στα διορθωμένα δεδομένα. Τα μεγέθη σε αυτό το σημείωμα είναι τα επανελεγμένα: αναπαρήχθησαν '
    'ανεξάρτητα σε έξι και πλέον runs πάνω στα δεδομένα που πράγματι υπάρχουν σήμερα, όχι μεταφερμένα από ένα run '
    'που δεν μπορούσε πλέον να αναπαραχθεί.', styles['Body']))
story.append(Paragraph(
    'Αυτό αναφέρεται εδώ σκόπιμα αντί να διορθωθεί σιωπηλά, διότι αποτελεί έναν γενικό τύπο σφάλματος που αξίζει '
    'να ονομαστεί ρητά: ένα αποτέλεσμα μπορεί να "παλιώσει" σιωπηλά όταν αλλάζουν τα δεδομένα που το τροφοδοτούν '
    'και η ανάλυση δεν ξανατρέχει. Η διορθωτική διαδικασία που υιοθετήθηκε στο εξής είναι η καταγραφή των αρχείων '
    'δεδομένων σε σύστημα ελέγχου εκδόσεων, ώστε μια τέτοια αλλαγή να παράγει ένα ορατό diff αντί για σιωπηλή '
    'απόκλιση.', styles['Body']))

spacer(4)
story.append(Paragraph('Ένα Επιλυμένο Ερώτημα: Είναι Καλύτερο ένα Μικρότερο Ομολογιακό Σκέλος;', styles['SectionHead']))
story.append(Paragraph(
    'Ένα προγενέστερο εύρημα υποδείκνυε ότι μια μικρότερη κατανομή σε ομόλογα (≈5% έναντι του δοκιμασμένου 15%) '
    'θα μπορούσε να υπερτερήσει αυτής της κατανομής ως προς το διάμεσο και το χειρότερο σενάριο αποτελέσματος. '
    'Επανελέγχοντας αυτή τη σύγκριση υπό ένα πλήρες φάσμα ρεαλιστικών συνθηκών — εφάπαξ επένδυση, ρεαλιστική '
    'μηνιαία συνεισφορά, μετά από έξοδα διαχείρισης και παρακράτηση φόρου, και υπό τον περιορισμό εκκίνησης μόνο '
    'από ιστορικά ακριβές αγορές — η εναλλακτική με το μικρότερο ομολογιακό σκέλος χάνει ως προς τον κίνδυνο '
    'πτώσης σε κάθε δοκιμή, και χάνει εντελώς ως προς το διάμεσο αποτέλεσμα μόλις εφαρμοστούν ρεαλιστικά κόστη.',
    styles['Body']))
bond_rows = [
    ['Δοκιμή', 'Δοκιμασμένη Κατανομή\n(15% ασφαλές σκέλος)', 'Εναλλακτική\n(5% ασφαλές σκέλος)'],
    ['Εφάπαξ, Π(πτώση ≥ 50%)', '2.60%', '3.95%'],
    ['Μηνιαία συνεισφορά, Π(πτώση ≥ 30%)', '17.11%', '27.36%'],
    ['Διάμεσο πολλαπλάσιο μετά από κόστη', '28.60x', '28.19x'],
    ['Υπό υψηλή αποτίμηση (CAPE), Π(πτώση ≥ 30%)', '21.44%', '31.91%'],
]
story.append(table_from_rows(bond_rows, [68*mm, 56*mm, 56*mm]))

spacer(3)
story.append(Paragraph('Περιορισμοί', styles['SectionHead']))
for txt in [
    'Οι προσομοιωμένες ιστορικές δοκιμές, συμπεριλαμβανομένων των μεθόδων block bootstrap, δεν μπορούν να συλλάβουν πραγματικά πρωτόγνωρα μελλοντικά καθεστώτα — μόνο το εύρος συμπεριφοράς που έχει ήδη παρατηρηθεί στην περίοδο δείγματος.',
    'Η σύγκριση κατανομής χρυσού χρησιμοποιεί μία σταθερή αναλογία μεταξύ των υπόλοιπων βαρών· μια πλήρης ταυτόχρονη βελτιστοποίηση όλων των βαρών δεν ξανατρέχτηκε πάνω στα διορθωμένα δεδομένα ως μέρος αυτού του σημειώματος.',
    'Οι υποθέσεις φόρων και εξόδων είναι ενδεικτικές και εξαρτώνται από τη φορολογική έδρα· τα αποτελέσματα διαφέρουν ανά επενδυτή.',
]:
    story.append(Paragraph('• ' + txt, styles['BulletItem']))

spacer(4)
story.append(Paragraph('Συμπέρασμα', styles['SectionHead']))
story.append(Paragraph(
    'Ο χρυσός προσφέρει πραγματική μείωση της πιθανότητας καταστροφικής πτώσης — περίπου 4–5 φορές στο δοκιμασμένο '
    'βάρος, κυρίως στις πρώτες 10 ποσοστιαίες μονάδες κατανομής. Εξίσου σημαντικό: ένα αυστηρό αποτέλεσμα είναι '
    'τόσο καλό όσο η τελευταία φορά που πράγματι επανελέγχθηκε πάνω σε πραγματικά δεδομένα.', styles['Body']))

spacer(3)
story.append(HRFlowable(width='100%', thickness=0.6, color=BORDER, spaceAfter=4))
story.append(Paragraph(
    'Προσωπικό ερευνητικό έργο για εκπαιδευτικούς σκοπούς — δεν αποτελεί επενδυτική, χρηματοοικονομική ή '
    'φορολογική συμβουλή. Τα προσομοιωμένα ιστορικά αποτελέσματα δεν εγγυώνται μελλοντικά αποτελέσματα. Πηγαίος '
    'κώδικας, δεδομένα και πλήρης μεθοδολογία δημοσιεύονται μαζί με αυτό το σημείωμα.', styles['Disclaimer']))

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                         leftMargin=20*mm, rightMargin=20*mm, topMargin=22*mm, bottomMargin=15*mm,
                         title='Σημείωμα Έρευνας Χαρτοφυλακίου', author='Ηλίας Προύντζος')
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f'Saved {OUT_PDF}')
