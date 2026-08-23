# SmartLoan Analytics — System Design Documentation

## 1. Problem Statement

Small lending organizations and community loan schemes may manage customer applications,
approvals, repayments, penalties and portfolio records manually or in disconnected files.
This can cause duplicate records, calculation errors, weak tracking of overdue loans,
difficulty producing management reports and limited visibility into portfolio performance.

SmartLoan Analytics is a Python desktop application designed to centralize customer and
loan data, automate common loan-management operations, validate data, analyze portfolio
performance and generate reports for decision making.

The system is an academic prototype. Its eligibility and risk calculations are transparent
rule-based algorithms for demonstrating Python programming and algorithmic thinking; they
are not regulated credit-scoring models.

## 2. System Objectives

The system should:

- provide secure user registration and authentication;
- support Administrator and Loan Officer/Librarian-style operational roles;
- manage customer records;
- manage loan applications and their lifecycle;
- record repayments and penalties;
- prevent invalid and duplicate data;
- calculate transparent eligibility scores;
- generate repayment schedules;
- identify and rank overdue loan risk;
- display analytical KPIs and charts;
- export PDF and CSV reports;
- record important events in logs and audit trails.

## 3. Functional Requirements

### FR-01 User Registration
The system shall allow authorized users to create user accounts.

### FR-02 Authentication
The system shall allow registered users to log in using a username and password.

### FR-03 Password Protection
The system shall store password hashes rather than plain-text passwords.

### FR-04 Role-Based Access
The system shall restrict privileged functions according to user role.

### FR-05 Customer Management
The system shall create, view, update, search and delete customer records where business
rules permit deletion.

### FR-06 Loan Application
The system shall create loan applications linked to valid customers.

### FR-07 Loan Validation
The system shall validate principal, interest rate, term, customer status and required fields.

### FR-08 Eligibility Scoring
The system shall calculate a transparent eligibility score for loan applications.

### FR-09 Loan Decision
Authorized users shall approve or reject pending loan applications.

### FR-10 Loan Disbursement
Authorized users shall record disbursement of approved loans.

### FR-11 Repayment Management
The system shall record repayments and prevent payments above the outstanding balance.

### FR-12 Overdue Detection
The system shall identify loans whose due date has passed while money remains outstanding.

### FR-13 Penalty Management
The system shall record and track penalties associated with overdue loans.

### FR-14 Search, Sort and Filter
Users shall be able to locate operational records using search/filter functions.

### FR-15 Analytics
The system shall calculate KPIs, summary statistics, trends and rankings.

### FR-16 Visualization
The system shall generate Matplotlib charts for selected analytical results.

### FR-17 Risk Ranking
The system shall rank loan risk using an explainable project algorithm.

### FR-18 Reporting
The system shall export management information to PDF and CSV.

### FR-19 Logging
The application shall log system events, errors and important actions.

### FR-20 Audit Trail
The system shall maintain auditable records of relevant user actions.

### FR-21 Logout
Authenticated users shall be able to end their session safely.

## 4. Non-Functional Requirements

### NFR-01 Usability
The Tkinter interface should use clear labels, menus, forms and messages suitable for users
with basic computer skills.

### NFR-02 Reliability
Database operations should preserve valid data and expected application state.

### NFR-03 Security
Passwords must be hashed. Privileged functions must check authorization. User-facing errors
should not expose sensitive internal database details.

### NFR-04 Performance
Normal operations over the assignment dataset of 650 loans should respond within a practical
desktop-interaction time on a standard computer.

### NFR-05 Maintainability
The codebase should use modules, classes, functions, docstrings and meaningful names.

### NFR-06 Portability
The application should run on a computer with a compatible Python installation and required
packages.

### NFR-07 Data Integrity
Primary keys, foreign keys, uniqueness rules and application validation should reduce
duplicate, missing and inconsistent records.

### NFR-08 Auditability
Important actions and failures should be traceable through logs and audit records.

### NFR-09 Recoverability
Expected user errors should not crash the complete application.

### NFR-10 Extensibility
The layered/modular design should allow future additions such as richer amortization,
notifications or organization-specific lending rules.

## 5. System Architecture

SmartLoan Analytics follows a layered modular architecture.

### Presentation Layer
Tkinter windows collect user input and display customers, loans, analytics and reports.

### Business Logic Layer
Authentication, customer management, loan management, repayment management and validation
implement application rules.

### Algorithm Layer
Eligibility scoring, repayment scheduling and risk ranking contain transparent algorithmic
logic.

### Analytics and Reporting Layer
Pandas/analytical queries, Matplotlib and ReportLab transform operational data into
management information.

### Data Access Layer
SQLite connections and SQL queries store and retrieve persistent records.

### Persistence Layer
`smartloan.db` stores users, customers, loans, repayments, penalties and audit logs.

## 6. Major System Modules

| Module | Responsibility |
|---|---|
| authentication.py | Registration, login, password hashing, permissions |
| customer_management.py | Customer CRUD and validation |
| loan_management.py | Applications, approval, rejection, disbursement |
| repayment_management.py | Repayments, balances and penalties |
| analytics.py | KPIs, trends, rankings and recommendations |
| reports.py | PDF/CSV export |
| eligibility_scoring.py | Eligibility algorithm |
| repayment_schedule.py | Installment schedule algorithm |
| risk_ranking.py | Risk-scoring and manual ranking algorithm |
| validation.py | Reusable input-validation rules |
| logger.py | Rotating application logging |
| database.py | SQLite initialization and connections |

## 7. Data Design

The core entities are:

- USERS
- CUSTOMERS
- LOANS
- REPAYMENTS
- PENALTIES
- AUDIT_LOGS

A customer may have many loans. A loan may have many repayments and penalties. A user may
create many audit-log entries.

## 8. Security Design

Passwords are hashed before storage. Role permissions are checked before restricted
operations. Input validation rejects malformed values. SQL operations use parameterized
queries. Expected errors are converted to safer user-facing messages while technical details
are retained in logs where appropriate.

## 9. Validation Design

The application validates missing values, incorrect formats and duplicate records. Additional
loan-domain rules include positive loan amounts, interest rates between 0 and 100, valid loan
terms, valid repayment references, non-future repayment dates, active customer requirements
and repayment amounts not exceeding outstanding balances.

## 10. Analytics Design

The analytics module provides total customers, loan counts by status, approval rate,
portfolio amounts, repayments, penalties, monthly trends, top-customer ranking and overdue
risk ranking.

Bar charts are appropriate for categorical comparisons. Line charts are used for changes
over time. Horizontal ranking charts support comparison of customers or portfolio values.

## 11. Reporting Design

Management reports combine KPIs, summary statistics, charts, risk information and
recommendations. PDF supports professional human-readable presentation while CSV supports
further spreadsheet analysis.

## 12. Algorithm Design

The three core algorithms are:

1. Eligibility scoring — O(1) time and O(1) space.
2. Repayment schedule generation — O(n) time and O(n) space.
3. Risk ranking using manual selection sort — O(n²) time and O(n) space.

Detailed analysis is provided in `docs/algorithms/ALGORITHM_COMPLEXITY_ANALYSIS.md`.

## 13. Exception and Logging Design

A custom exception hierarchy separates expected validation/application failures from
unexpected technical failures. A centralized handler logs errors and converts them into
safe messages. Rotating logs reduce uncontrolled log-file growth.

## 14. Design Assumptions

- The application is a single-computer academic desktop prototype.
- SQLite is sufficient for the assignment dataset.
- Loan calculations use simplified academic rules.
- Synthetic data is used for privacy and reproducibility.
- Internet connectivity is not required for normal system operation.

## 15. Design Limitations

The system is not a multi-branch production banking platform. It does not integrate with a
credit bureau or mobile-money API. The eligibility model is simplified. SQLite is intended
for local/small-scale use rather than high-concurrency enterprise deployment.

## 16. Future Improvements

Future versions could add client-server deployment, stronger identity management,
organization-specific affordability policies, encrypted backups, notifications, payment
gateway integration, reducing-balance amortization and authorized anonymized institutional
datasets.
