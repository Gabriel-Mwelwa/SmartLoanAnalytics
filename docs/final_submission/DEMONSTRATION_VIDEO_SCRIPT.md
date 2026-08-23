# 10–15 Minute Demonstration Video Script

## 0:00–1:00 — Introduction
Presenter 1:
"Good day. We are presenting SmartLoan Analytics, an Intelligent Loan Management and Analytics
System developed in Python for our BICT Python Programming Assignment."

Display title and group names:
CHOLA CHILUFYA — 2410856
Sibamba Mumbula — 2410781
EUNICE KUNDA — 2410776
Caroline Musonda — 2300908
Gabriel Mwelwa — 2410761
Mumba Adrian — 2611537

Explain the problem in approximately 30 seconds.

## 1:00–2:00 — Project Structure and Technologies
Presenter 2:
Show the project folders and briefly identify `main.py`, modules, algorithms, database, tests,
data and documentation.

State that Tkinter provides the GUI, SQLite stores data, Matplotlib creates charts, ReportLab
creates PDF reports and pytest supports automated testing.

## 2:00–3:00 — Dataset
Presenter 3:
Open `data/loan_dataset_650_records.csv`.
Explain that the dataset is synthetic, contains 650 loan records and protects real customer
privacy.

Show `tools/generate_dataset.py` and explain the fixed random seed.

## 3:00–5:30 — Main Application
Presenter 1:
Run:

    python main.py

Demonstrate login and dashboard.

Presenter 2:
Open Customer Management. Search for a customer and explain create/update/validation.

Presenter 3:
Open Loan Management. Demonstrate or explain a pending loan, eligibility score, approval and
disbursement lifecycle.

Presenter 4:
Show repayment recording and explain protection against invalid amounts/references.

## 5:30–7:30 — Analytics and Reports
Presenter 5:
Open Analytics. Explain KPIs and at least two charts.

Explain:
- bar chart for categorical comparison;
- line chart for time trends.

Presenter 6:
Generate/open a PDF or CSV report and explain management recommendations.

## 7:30–10:00 — Algorithms
Presenter 1 — Eligibility:
Open `algorithms/eligibility_scoring.py`.
Explain O(1) because a fixed number of operations is performed.

Presenter 2 — Repayment:
Open `algorithms/repayment_schedule.py`.
Point to the loop over `term_months`.
Explain O(n) time and O(n) space.

Presenter 3 — Risk:
Open `algorithms/risk_ranking.py`.
Point to nested selection-sort loops.
Explain O(n²), and state that production could use O(n log n) sorting.

## 10:00–11:30 — Validation, Logging and Testing
Presenter 4:
Show validation code and one invalid-input example.

Presenter 5:
Show the log file/audit concept.

Presenter 6:
Run:

    python -m pytest -q

Show that the complete automated test suite passes.

## 11:30–13:00 — Design and Limitations
Show architecture and ERD.

Explain three limitations:
1. desktop/local architecture;
2. simplified academic scoring;
3. synthetic dataset.

Explain two or three future improvements.

## 13:00–14:00 — Conclusion
Presenter 1:
Summarize how the project satisfies authentication, CRUD, validation, OOP, algorithms,
analytics, reporting, testing, logging and documentation requirements.

## Recording Rules
- All group members must appear.
- Do not only read slides.
- Each member should explain code they understand.
- Record the running system, not only screenshots.
- Keep the final recording between 10 and 15 minutes.
