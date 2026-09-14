#!/usr/bin/env python3
"""Build a wholly fictional tri-merge credit report, as text and as a PDF.

Every client report in dev/fixtures is real family or client data and must
never reach a browser window, a screenshot, or anything that leaves this
machine. This file exists so the live site can be driven end to end without
one: TAYLOR RIVERA does not exist, the account numbers are invented, and the
SSN is the 000-prefixed block the SSA has never issued.

It is built to exercise the paths worth seeing on screen:
  * a late grid the three bureaus report differently   -> late_grid_mismatch
  * a date of last activity four months apart          -> date_last_activity_mismatch
  * a closed account still showing a monthly payment   -> monthly_payment_on_closed
  * a bankruptcy public record with no court named     -> bankruptcy_court_not_reported
  * an account nobody would recognise, for the
    identity-theft "never mine" path                   -> idtheft_block

Usage:  python3 dev/make_demo_report.py  [outdir]
"""
import io, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '/Users/daveivery/Documents/Claude/Projects/MGC/dev/demo'
NAME = 'Taylor Rivera'
DATE = 'August 31, 2026'
FOOT = 'Aug 31, 2026 Three Bureau Credit Report powered by Equifax Page %d of 12'

L = []
def w(*rows):
    for r in rows:
        L.append(r)

w('powered by', 'Three Bureau Credit Report', NAME, DATE,
  'Three Bureau Credit Report', '%s | %s' % (NAME, DATE))

# ---- table of contents (entries carry trailing page numbers; parser skips it)
w('1. Report Summary 1',
  '2. Revolving Accounts 2',
  '2.1 Harbor Point Card 2',
  '2.2 Cedarline Bank Visa 4',
  '3. Installment Accounts 6',
  '3.1 Northgate Auto Finance 6',
  '4. Other Accounts 8',
  '4.1 Sterling Peak Lending 8',
  '8. Personal Information 9',
  '9. Inquiries 10',
  '10. Public Records 11',
  '11. Collections 12')

# ---- 1. Report Summary
w('1. Report Summary',
  'Review this summary for a quick view of key information contained in your credit file.',
  'Credit Score and Rating',
  'Equifax Accounts Summary',
  'Equifax Experian TransUnion',
  'Report Date August 31, 2026 August 31, 2026 August 31, 2026',
  'Credit Score 562 548 571',
  'Total Accounts 4 4 4',
  FOOT % 1)

def account(num, title, rows, payment_rows, comments=None):
    w('%s %s' % (num, title))
    w('Payment History',
      'Equifax', 'Experian', 'TransUnion',
      'Payment Summary',
      'Equifax Experian TransUnion')
    for r in payment_rows:
        w(r)
    w('Account Details',
      'View the detailed information about this account.',
      'Equifax Experian TransUnion')
    for r in rows:
        w(r)
    if comments:
        w('Comments Contact')
        for c in comments:
            w(c + ' -')

# ---- 2.1  the late grid the bureaus cannot agree on
account('2.1', 'Harbor Point Card',
  ['Account Type Revolving Revolving Revolving',
   'Account Status Late 60 Days Late 60 Days Late 60 Days',
   'Date Opened Mar 14, 2019 Mar 14, 2019 Mar 14, 2019',
   'Date Of Last Activity Apr 02, 2026 Jul 28, 2026 Apr 02, 2026',
   'Date Reported Aug 01, 2026 Aug 01, 2026 Aug 01, 2026',
   'Date Of First Delinquency Nov 01, 2024 Nov 01, 2024 Nov 01, 2024',
   'Credit Limit $1,500 $1,500 $1,500',
   'High Credit $1,480 $1,480 $1,480',
   'Reported Balance $1,412 $1,412 $1,412',
   'Amount Past Due $180 $180 $180',
   'Monthly Payment $45 $45 $45',
   '30 Days Past Due 3 3 3',
   '60 Days Past Due 1 2 1',
   '90 Days Past Due 0 0 0',
   '120 Days Past Due 0 0 0'],
  ['Reported Yes Yes Yes',
   'Account Number xxxxxxxxxxxx 4417 xxxxxxx 4417 xxxxxxxxxxxx 4417',
   'Account Status Late 60 Days Late 60 Days Late 60 Days'])
w(FOOT % 2)

# ---- 2.2  closed, and still reporting a monthly payment
account('2.2', 'Cedarline Bank Visa (CLOSED)',
  ['Account Type Revolving Revolving Revolving',
   'Account Status Closed Closed Closed',
   'Date Opened Jun 09, 2016 Jun 09, 2016 Jun 09, 2016',
   'Date Of Last Activity Feb 01, 2025 Feb 01, 2025 Feb 01, 2025',
   'Date Reported Aug 01, 2026 Aug 01, 2026 Aug 01, 2026',
   'Credit Limit $3,000 $3,000 $3,000',
   'High Credit $2,940 $2,940 $2,940',
   'Reported Balance $0 $0 $0',
   'Amount Past Due $0 $0 $0',
   'Monthly Payment $75 $75 $75',
   '30 Days Past Due 0 0 0',
   '60 Days Past Due 0 0 0',
   '90 Days Past Due 0 0 0'],
  ['Reported Yes Yes Yes',
   'Account Number xxxxxxxxxxxx 8820 xxxxxxx 8820 xxxxxxxxxxxx 8820',
   'Account Status Closed Closed Closed'],
  ['Account closed by consumer'])
w(FOOT % 4)

# ---- 3.1  an ordinary, healthy installment account
account('3.1', 'Northgate Auto Finance',
  ['Account Type Installment Installment Installment',
   'Account Status Pays as agreed Pays as agreed Pays as agreed',
   'Date Opened Jan 22, 2023 Jan 22, 2023 Jan 22, 2023',
   'Date Of Last Activity Aug 01, 2026 Aug 01, 2026 Aug 01, 2026',
   'Date Reported Aug 01, 2026 Aug 01, 2026 Aug 01, 2026',
   'Credit Limit N/A N/A N/A',
   'High Credit $24,500 $24,500 $24,500',
   'Reported Balance $11,208 $11,208 $11,208',
   'Amount Past Due $0 $0 $0',
   'Monthly Payment $412 $412 $412',
   '30 Days Past Due 0 0 0',
   '60 Days Past Due 0 0 0',
   '90 Days Past Due 0 0 0'],
  ['Reported Yes Yes Yes',
   'Account Number xxxxxxxxxxxx 1195 xxxxxxx 1195 xxxxxxxxxxxx 1195',
   'Account Status Pays as agreed Pays as agreed Pays as agreed'])
w(FOOT % 6)

# ---- 4.1  the one to mark "never mine"
account('4.1', 'Sterling Peak Lending',
  ['Account Type Installment Installment Installment',
   'Account Status Charge-off Charge-off Charge-off',
   'Date Opened Feb 11, 2025 Feb 11, 2025 Feb 11, 2025',
   'Date Of Last Activity May 01, 2025 May 01, 2025 May 01, 2025',
   'Date Reported Aug 01, 2026 Aug 01, 2026 Aug 01, 2026',
   'Date Of First Delinquency Mar 01, 2025 Mar 01, 2025 Mar 01, 2025',
   'Credit Limit N/A N/A N/A',
   'High Credit $4,900 $4,900 $4,900',
   'Reported Balance $4,900 $4,900 $4,900',
   'Amount Past Due $4,900 $4,900 $4,900',
   'Monthly Payment $0 $0 $0',
   '30 Days Past Due 1 1 1',
   '60 Days Past Due 1 1 1',
   '90 Days Past Due 1 1 1'],
  ['Reported Yes Yes Yes',
   'Account Number xxxxxxxxxxxx 7731 xxxxxxx 7731 xxxxxxxxxxxx 7731',
   'Account Status Charge-off Charge-off Charge-off'],
  ['Charged off as bad debt'])
w(FOOT % 8)

# ---- 8. Personal Information
w('8. Personal Information',
  'Equifax Experian TransUnion',
  'Name Taylor Rivera Taylor Rivera Taylor Rivera',
  'Date of Birth Mar 1988 Mar 1988 Mar 1988',
  'Current Address 44 Palmetto Way 44 Palmetto Way 44 Palmetto Way',
  'Sarasota, FL 34236 Sarasota, FL 34236 Sarasota, FL 34236',
  FOOT % 9)

# ---- 9. Inquiries
w('9. Inquiries',
  'TransUnion',
  'Date Company Address',
  'Jun 12, 2026 STERLING PEAK LENDING 900 CANAL ST',
  'NEW ORLEANS, LA 70112',
  'Feb 03, 2026 NORTHGATE AUTO FIN 12 MARKET ST',
  'TAMPA, FL 33602',
  FOOT % 10)

# ---- 10. Public Records: a bankruptcy with the Court column empty
w('10. Public Records',
  'A public record is a legal document issued by local or federal government.',
  'Bankruptcies',
  'Bankruptcies are a legal status granted by a state or federal court that indicates you are',
  'unable to pay off outstanding debt.',
  'Experian',
  'Judgments',
  'Judgments are a legal status granted by a small claims court.',
  'You currently have no Judgments on your credit file.',
  'Liens',
  'A lien is a legal claim on an asset.',
  'You currently have no Liens on your credit file.',
  'Date Filed Reference',
  'Number',
  'Status Court Liability Exempt Amount Asset Amount',
  'Feb 18, 2024 2402884 Discharged N/A N/A N/A N/A',
  FOOT % 11)

# ---- 11. Collections
w('11. Collections',
  'Collections are accounts with outstanding debt sold by a creditor to a collections agency.',
  'TransUnion',
  'Date Reported: Aug 01, 2026',
  'Agency Client: STERLING PEAK LENDING',
  'Date Assigned Mar 01, 2026',
  'Original Amount Owed N/A',
  'Amount $4,900',
  'Status Date Aug 01, 2026',
  'Balance Date Aug 01, 2026',
  'Purge Date N/A',
  'Account Designator Code INDIVIDUAL_ACCOUNT',
  'Account Number xxxxxxxxxxxx 7731',
  FOOT % 12)

os.makedirs(OUT, exist_ok=True)
txt = '\n'.join(L) + '\n'
io.open(os.path.join(OUT, 'taylor_rivera.txt'), 'w', encoding='utf-8').write(txt)
print('text  %d lines -> %s/taylor_rivera.txt' % (len(L), OUT))

# ---- the same lines as a PDF, one drawn line per text line, so pdf.js
# ---- reconstructs exactly what the text file contains.
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError:
    print('reportlab not installed — skipping PDF (pip3 install reportlab)')
    sys.exit(0)

path = os.path.join(OUT, 'taylor_rivera.pdf')
c = canvas.Canvas(path, pagesize=letter)
width, height = letter
y = height - 48
c.setFont('Helvetica', 8)
for line in L:
    if y < 48:
        c.showPage()
        c.setFont('Helvetica', 8)
        y = height - 48
    c.drawString(40, y, line[:150])
    y -= 11
c.showPage()
c.save()
print('pdf   -> %s' % path)
