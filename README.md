# SmartLoan Analytics

## Project Title
Design and Development of an Intelligent Loan Management and Analytics System Using Python

## Phase 1
Version 0.1.0 implements the project structure, configuration, SQLite database, logging, starter OOP models, validation utilities, starter algorithms, and a runnable Tkinter desktop window.

## Group Members
- Chola Chilufya — 2410856
- Sibamba Mumbula — 2410781
- Eunice Kunda — 2410776
- Caroline Musonda — 2300908
- Gabriel Mwelwa — 2410761

> The assignment statement says groups of five. Confirm with the lecturer that six members are permitted.

## How to Run

```bash
python -m pip install -r requirements.txt
python main.py
```

## Database Tables
- users
- customers
- loans
- repayments
- penalties
- audit_logs

## Phase Roadmap
1. Foundation
2. Authentication and role-based access control
3. Customer management
4. Loan applications, approval, disbursement and repayments
5. Analytics and Matplotlib
6. PDF/CSV reports and recommendations
7. Validation, exception handling, logging and testing
8. 500+ record dataset
9. Algorithms and Big O analysis
10. UML/system design documentation
11. Technical report, journal and user manual
12. Presentation, video and oral defence preparation


## Phase 2 — Authentication and RBAC
Version 0.2.0 adds:
- User registration
- Salted PBKDF2 password hashing
- Login and session handling
- Administrator and Loan Officer roles
- Role-based permissions
- Authentication audit events
- Login/registration GUI
- Role-aware dashboard

The first registered account becomes Administrator automatically.


## Phase 3 — Customer Management
Version 0.3.0 adds:
- Customer registration
- View/update/delete
- Search, sort and filter
- Duplicate customer-code and National ID protection
- Employment and monthly-income validation
- Active/Suspended customer status
- Customer audit logging
- Customer Management Tkinter window
- Automated customer tests


## Phase 4 — Loans, Repayments and Overdue Management
Version 0.4.0 adds:
- Loan applications
- Eligibility scoring
- Administrator approval and rejection
- Loan disbursement and due dates
- Outstanding-balance calculation
- Repayment recording
- Duplicate repayment-reference protection
- Loan completion when fully repaid
- Overdue-loan detection
- Overdue penalty calculation and creation
- Loan and repayment Tkinter windows
- Expanded automated tests


## Phase 5 — Analytics Dashboard and Matplotlib
Version 0.5.0 adds:
- Loan/customer KPIs
- Approval-rate calculation
- Outstanding-portfolio calculation
- Repayment and penalty metrics
- Monthly loan-application trend
- Monthly repayment trend
- Loan status distribution
- Top-customer ranking
- Overdue risk ranking
- Summary statistics with Pandas
- Management recommendations
- Four Matplotlib charts
- Analytics dashboard GUI
- Automated analytics tests


## Phase 6 — Reporting and Management Recommendations
Version 0.6.0 adds:
- Professional management PDF reporting
- Management-summary CSV export
- Detailed loan-record CSV export
- Detailed repayment-record CSV export
- KPI and summary-statistics reporting
- Loan status and customer rankings
- Overdue-risk reporting
- Embedded Matplotlib charts in the PDF
- Evidence-based management recommendations
- Visualization justification
- Report audit logging
- Reports GUI integration
- Automated reporting tests


## Phase 7 — Software Quality
Version 0.7.0 adds:
- Advanced reusable validation
- Centralized safe exception handling
- Rotating system logging
- GUI callback error protection
- Administrator audit-log service
- Stronger authentication validation
- Loan/repayment validation hardening
- Phase 7 testing documentation
- Expanded automated quality tests


## Phase 8 — Synthetic Dataset
Version 0.8.0 adds:
- Reproducible synthetic-data generator
- 220 customers
- 650 loan records
- Repayment and penalty data
- CSV submission dataset
- Dataset source/process documentation
- Ethical considerations
- Data-quality controls
- Dataset limitations and future improvements
- Automated dataset tests

Generate the dataset with:

```bash
python -m tools.generate_dataset
```


## Phase 9 — Algorithms and Computational Complexity
Version 0.9.0 formally documents the three original SmartLoan algorithms:
- Loan eligibility scoring — O(1)
- Repayment schedule generation — O(n)
- Loan risk ranking using manual selection sort — O(n²)

See:
- `docs/algorithms/ALGORITHM_COMPLEXITY_ANALYSIS.md`
- `docs/algorithms/ORAL_DEFENCE_ALGORITHMS.md`

Run:

```bash
python -m tools.benchmark_algorithms
```

for illustrative timing demonstrations.


## Phase 10 — System Design Documentation
Version 0.10.0 adds complete design documentation:
- Problem statement and objectives
- Functional requirements
- Non-functional requirements
- Layered system architecture
- Use Case Diagram
- Class Diagram
- Loan Processing Activity Diagram
- Overall System Flowchart
- ER Diagram
- Security, validation, analytics and reporting design
- Design assumptions, limitations and future improvements
- Oral-defence preparation

See `docs/design/`.


## Phase 11 — Technical Documentation
Version 0.11.0 adds:
- Full technical report draft
- Six-week design journal
- Complete user manual
- Documentation submission checklist
- Limitations and future improvements
- Dataset ethics and methodology discussion
- Testing/performance/security discussion
- Oral-defence preparation reminders

See `docs/report`, `docs/journal`, and `docs/user_manual`.


## Phase 12 — Final Submission and Defence
Version 1.0.0 adds:
- Expanded 4,000–6,000-word-range technical report
- 18-slide presentation content
- 10–15 minute demonstration video script
- Oral-defence master guide
- Live coding/debugging exercises
- Git finalization and release-tag guide
- Academic integrity declaration template
- Final rubric-based submission checklist
- Suggested group defence allocation

See `docs/final_submission/`.
