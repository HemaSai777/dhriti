import os
from pathlib import Path
import fitz  # PyMuPDF

demo_dir = Path(r'C:\Users\munik\.gemini\antigravity\scratch\sahaya\demo_upload_files')
demo_dir.mkdir(parents=True, exist_ok=True)

docs = [
    {
        'name': 'PMFBY_Post_Harvest_Loss_and_Cyclonic_Rains_2025',
        'title': 'PMFBY Post-Harvest Loss and Cyclonic Rains Operational Protocol 2025',
        'content': """[PAGE 1]
MINISTRY OF AGRICULTURE AND FARMERS WELFARE
PRADHAN MANTRI FASAL BIMA YOJANA (PMFBY)
SPECIAL OPERATIONAL CIRCULAR - POST-HARVEST RISK COVERAGE 2025

Section 12: Scope and Eligibility for Post-Harvest Losses
Clause 12.1: Perils Covered
Post-harvest risk coverage is available throughout the country against specified localized perils, namely cyclonic rains, unseasonal showers, and post-harvest inundation.

Clause 12.2: Mandatory Harvesting Condition
Coverage is strictly available only for those crops that are kept in 'cut and spread' or bundled condition in the agricultural field itself for drying after harvesting. Produce stored in farmer courtyards, godowns, threshing floors, or under tarpaulins is excluded from post-harvest coverage.

[PAGE 2]
Clause 12.4: Period of Risk Coverage
The post-harvest risk coverage period shall be valid for a maximum period of 14 days from harvesting of the insured crop. Any loss occurring after 14 days from harvesting shall not be compensable under PMFBY.

Clause 12.6: Mandatory Intimation and Survey
The affected farmer must notify the insurance company, local agricultural office, or PACS within 72 hours of damage. An appointed surveyor must conduct the field loss assessment within 48 hours of intimation, and 100% of approved claim compensation shall be disbursed directly to the farmer's DBT bank account within 15 days of survey completion.
"""
    },
    {
        'name': 'Cooperative_Societies_Election_Rules_and_Quorum_2025',
        'title': 'Model Cooperative Societies Election Rules and Quorum Framework 2025',
        'content': """[PAGE 1]
MINISTRY OF COOPERATION, GOVERNMENT OF INDIA
MODEL COOPERATIVE SOCIETIES (ELECTION & GOVERNANCE) RULES 2025

Chapter V: General Meetings and Election Notifications
Rule 21: Notice Period for Annual General Meetings
Every Primary Agricultural Credit Society (PACS) shall convene its Annual General Meeting (AGM) by giving at least 14 clear days notice in writing to all registered voting members. The notice must specify the date, time, venue, and agenda items.

Rule 24: Voting Procedure and Secret Ballot
All elections to the Managing Committee shall be conducted strictly by secret ballot supervised by a Returning Officer appointed by the District Cooperative Election Authority. No open voting or voting by proxy is permissible under any circumstances.

[PAGE 2]
Rule 26: Minimum Voter Eligibility and Patronage
A member shall be eligible to exercise voting rights in the election of the Managing Committee only if:
a) The member has been an active member of the Society for at least 12 continuous months.
b) The member has conducted minimum patronage transactions of at least Rs. 2,500 (through credit, fertilizer, or crop procurement) with the Society during the preceding financial year.
c) The member is not a willful defaulter on any PACS loan installment for more than 90 days on the date of publication of the electoral roll.

Rule 28: Term of Committee and Election Deadlines
The tenure of the Managing Committee shall be exactly five years from the date of election. The election process for constituting the next Managing Committee must be concluded at least 30 calendar days prior to the expiration of the incumbent committee term.
"""
    },
    {
        'name': 'Agriculture_Infrastructure_Fund_AIF_Guidelines_2025',
        'title': 'Agriculture Infrastructure Fund (AIF) Central Scheme Norms 2025',
        'content': """[PAGE 1]
DEPARTMENT OF AGRICULTURE AND FARMERS WELFARE
AGRICULTURE INFRASTRUCTURE FUND (AIF) GUIDELINES 2025

Chapter II: Objectives, Eligible Projects, and Beneficiaries
Norm 4: Eligible Post-Harvest Management Projects
Under AIF, medium-to-long term debt financing is provided for investment in viable projects for post-harvest management infrastructure and community farming assets, including:
1. Modern Cold Storage and Cold Chain facilities.
2. Warehouses, Silos, and Pack-houses.
3. Sorting, Grading, and Primary Processing units.
4. E-marketing platforms tied to e-NAM and assaying labs.

Eligible beneficiaries include Primary Agricultural Credit Societies (PACS), Marketing Cooperative Societies, Farmer Producer Organizations (FPOs), Self Help Groups (SHGs), and individual Agri-entrepreneurs.

[PAGE 2]
Chapter IV: Financial Incentives, Interest Subvention, and Moratorium
Norm 7: Interest Subvention Structure
All loans disbursed under this financing facility shall have an interest subvention of 3.0% per annum up to a loan limit of Rs. 2.00 Crore (Rupees Two Crore). In case of loans sanctioned to PACS, the interest subvention is directly passed on to reduce borrowing rates to below 4% per annum.

Norm 9: Maximum Duration of Subvention
The interest subvention benefit is available for a maximum period of 7 years from the date of first loan disbursement.

Norm 11: Credit Guarantee Coverage
Credit guarantee coverage under the Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE) scheme is available for loans up to Rs. 2.00 Crore. The guarantee fee shall be paid entirely by the Central Government without burdening the borrowing PACS or farmer.
"""
    },
    {
        'name': 'Fertilizer_DBT_Subsidy_and_POS_Aadhaar_Norms_2025',
        'title': 'Fertilizer DBT Subsidy Distribution and POS Machine Norms 2025',
        'content': """[PAGE 1]
MINISTRY OF CHEMICALS AND FERTILIZERS
DEPARTMENT OF FERTILIZERS - DBT OPERATIONAL DIRECTIVE 2025

Section 3: Mandatory Aadhaar Authentication via POS
1. No subsidized chemical fertilizer (Urea, DAP, MOP, NPK) shall be sold by any PACS, Cooperative Marketing Federation, or retail dealer without real-time biometric/Aadhaar authentication on the electronic Point of Sale (e-POS) terminal.
2. The DBT subsidy is credited directly to manufacturing/importing companies only after the successful digital sale transaction is registered on the integrated Fertilizer Management System (iFMS).

Section 5: Monthly Purchase Quotas and Landholding Checks
A maximum purchase ceiling of 100 bags (50 kg each) of subsidized Urea per calendar month is enforced per individual farmer. Any purchase exceeding 100 bags requires prior written verification and countersignature from the Block Agricultural Officer (BAO) confirming genuine cropping acreage requirements.

[PAGE 2]
Section 8: Prohibition of Digital Surcharges
No PACS or fertilizer distributor shall levy any convenience fee, swipe charge, or surcharge on farmers paying via UPI, RuPay cards, or AEPS. The retail price printed on the fertilizer bag is inclusive of all taxes and delivery charges.

Section 10: Mandatory Issue of Printed Cash Receipt
Every PACS salesperson must issue a computer-generated bilingual POS receipt to the purchaser. The receipt must clearly state:
a) The Maximum Retail Price (MRP) paid by the farmer.
b) The exact Central Government subsidy amount absorbed per bag (e.g., Rs. 2,150 per bag of Urea).
c) Buyer Aadhaar last 4 digits and transaction reference number.
Any refusal to issue a printed receipt shall attract immediate suspension of the retail license under the Fertilizer Control Order (FCO).
"""
    },
    {
        'name': 'State_Cooperative_Ombudsman_Appeals_and_Penalties_2025',
        'title': 'State Cooperative Ombudsman Authority Powers and Appeals Manual 2025',
        'content': """[PAGE 1]
STATUTORY COOPERATIVE DISPUTE RESOLUTION MANUAL
STATE COOPERATIVE OMBUDSMAN AUTHORITY 2025

Chapter IV: Jurisdiction and Powers of the Cooperative Ombudsman
Section 18: Subject Matter Jurisdiction
The Cooperative Ombudsman shall have exclusive statutory jurisdiction to investigate and adjudicate complaints regarding:
1. Arbitrary refusal or delayed admission into PACS membership.
2. Financial irregularities, embezzlement, or uncredited passbook deposits exceeding Rs. 50,000.
3. Wrongful denial or deduction of crop insurance claims and interest subvention benefits.
4. Malicious rejection of agricultural credit without written speaking orders.

Section 20: Limitation Period for Appeals
Any aggrieved farmer or society member must file an appeal before the Ombudsman within 60 calendar days from the date of the Society's rejection order, or within 90 days if the Society has failed to communicate any resolution.

[PAGE 2]
Section 23: Punitive Damages and Personal Penalties
Where the Ombudsman concludes that an officer, secretary, or committee member has acted with willful negligence, corrupt intent, or malicious delay:
a) The Ombudsman may award compensatory damages up to Rs. 25,000 payable to the complainant from the Society reserve.
b) The Ombudsman may recommend immediate recovery of such amount from the personal emoluments of the guilty officer.
c) In severe cases of persistent non-compliance, the Ombudsman can direct the Registrar of Cooperative Societies to initiate disqualification under Section 36 of the Act.

Section 25: Enforceability and Binding Nature of Orders
Every order passed by the Cooperative Ombudsman shall be final and binding on the Cooperative Society. The Society Managing Committee must implement the award and report compliance within 30 calendar days from receipt of the certified order.
"""
    }
]

for d in docs:
    # 1. Write TXT
    txt_path = demo_dir / f"{d['name']}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(d['content'])
    print(f"Created TXT: {txt_path.name}")

    # 2. Write PDF with PyMuPDF
    pdf_path = demo_dir / f"{d['name']}.pdf"
    pdf_doc = fitz.open()
    pages_text = d['content'].split('[PAGE ')
    for p in pages_text:
        if not p.strip():
            continue
        lines = p.strip().split('\n')
        page_body = '\n'.join(lines[1:]) if lines[0].strip().endswith(']') else '\n'.join(lines)
        page = pdf_doc.new_page(width=595, height=842)
        rect = fitz.Rect(50, 50, 545, 800)
        page.insert_textbox(rect, page_body, fontsize=11, fontname='helv', color=(0.1, 0.15, 0.2))
    pdf_doc.save(str(pdf_path))
    pdf_doc.close()
    print(f"Created PDF: {pdf_path.name}")

print("All 5 demo files generated successfully in demo_upload_files!")
