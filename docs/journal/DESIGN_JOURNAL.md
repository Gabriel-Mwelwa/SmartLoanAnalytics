# SmartLoan Analytics — Six-Week Design Journal

**Group Members**

- CHOLA CHILUFYA — 2410856
- Sibamba Mumbula — 2410781
- EUNICE KUNDA — 2410776
- Caroline Musonda — 2300908
- Gabriel Mwelwa — 2410761
- Mumba Adrian — 2611537


## Purpose

This journal records the development process, problems encountered, alternatives considered,
reasons for decisions and lessons learned. Students should personalize the entries with the
actual dates and responsibilities from their Git history before final submission.

## Week 1 — Problem Selection, Requirements and Foundation

### Work Completed
The group selected a Loan Management System because it provides a realistic data-management
problem without requiring an excessively complicated user interface. The assignment requirements
were converted into phases. The initial project structure, configuration, SQLite database,
logging foundation and domain models were established.

### Problems Encountered
The assignment contained many requirements beyond simple CRUD. The group needed to ensure that
analytics, algorithms, reporting, testing, UML and a 500-record dataset were considered from the
beginning.

### Alternatives Considered
A web application and a larger enterprise database were considered. Tkinter and SQLite were
selected because the assignment requires Python rather than a specific web technology and the
solution is a desktop prototype.

### Why the Chosen Solution Was Selected
Tkinter reduces deployment complexity and SQLite provides persistent relational storage without
requiring a separate server.

### Lessons Learned
A good project structure should be established before writing many features. Requirements should
be mapped to implementation phases.

## Week 2 — Authentication, Roles and Customer Management

### Work Completed
User registration, login, password hashing and role-based permissions were implemented.
Customer-management functions were added with validation and database persistence.

### Problems Encountered
Plain-text passwords would violate good security practice. Duplicate usernames, emails and
customer identifiers also needed to be controlled.

### Alternatives Considered
Storing passwords directly was rejected. A single unrestricted user role was also rejected
because the assignment explicitly requires different roles.

### Why the Chosen Solution Was Selected
Password hashing reduces exposure if database contents are viewed. Role-based access demonstrates
authorization and supports separation of responsibilities.

### Lessons Learned
Authentication answers "who is the user?" while authorization answers "what may the user do?"
Both are necessary.

## Week 3 — Loan Lifecycle and Repayments

### Work Completed
Loan applications, eligibility scoring, approval/rejection, disbursement, repayment recording,
overdue handling and penalties were developed.

### Problems Encountered
Loan states had to follow logical transitions. Repayments could not simply be inserted without
checking the loan state and outstanding amount.

### Alternatives Considered
Allowing free editing of loan status was considered simpler but was rejected because it could
produce inconsistent records.

### Why the Chosen Solution Was Selected
Business rules were placed in management modules so the GUI could not be the only protection
against invalid operations.

### Lessons Learned
Validation should exist close to business logic, not only in interface widgets.

## Week 4 — Analytics, Charts and Reporting

### Work Completed
The analytics dashboard was implemented with KPIs, trends, rankings and Matplotlib charts.
Management PDF and CSV reporting was added.

### Problems Encountered
Different visualizations communicate different kinds of information. The group also had to avoid
duplicating analytical calculations in every report.

### Alternatives Considered
Pie charts were considered for many outputs, but bar and line charts were selected where they
communicate comparisons and time trends more clearly.

### Why the Chosen Solution Was Selected
Central analytics functions can be reused by the GUI and reports, reducing duplicated logic.

### Lessons Learned
Visualization should be chosen according to the analytical question, not simply because a chart
looks attractive.

## Week 5 — Validation, Testing and Dataset

### Work Completed
Advanced validation, centralized exception handling, rotating logging and automated tests were
expanded. A reproducible synthetic generator created 220 customers and 650 loan records with
repayments and penalties.

### Problems Encountered
Synthetic overdue dates initially required careful ordering so that application, approval,
disbursement and due dates remained logically consistent.

### Alternatives Considered
Using real borrower data was considered unnecessary and created privacy concerns. Manually typing
500 records was rejected because it would be slow and difficult to reproduce.

### Why the Chosen Solution Was Selected
A fixed-seed generator provides reproducible data while avoiding disclosure of real financial
information.

### Lessons Learned
Synthetic data still requires validation. Generated records must obey the same business logic as
manually entered records.

## Week 6 — Algorithms, Complexity, Design and Final Documentation

### Work Completed
The group formally analyzed eligibility scoring, repayment scheduling and risk ranking. Big O
time and space complexity were documented. Architecture, use-case, class, activity, system-flow
and ER diagrams were prepared. The technical report, journal and user manual were consolidated.

### Problems Encountered
Python has built-in sorting, but simply calling it would provide weak evidence of understanding
the underlying algorithm.

### Alternatives Considered
Built-in sorting was compared with a manual selection-sort implementation.

### Why the Chosen Solution Was Selected
Selection sort is not the fastest production choice, but its O(n²) nested-loop logic is easy to
demonstrate and satisfies the assignment's emphasis on algorithmic reasoning. A production
improvement is documented.

### Lessons Learned
A system is not complete when the code runs. Students must be able to explain design choices,
complexity, limitations, tests and Git history.

# Final Reflection

The project developed from a basic database foundation into a complete data-management and
analytics prototype. Incremental development made debugging easier because features were tested
as they were introduced.

The most important lesson is that software engineering involves more than writing code. Data
quality, security, algorithms, documentation, testing, maintainability, ethics and the ability
to explain decisions all contribute to software quality.

# Git Evidence Section

Before submission, paste the group's actual Git commit history here or capture screenshots.
Do not invent commits that were never made.

Recommended evidence should show at least 15 meaningful incremental commits and a final tagged
release.

# Individual Contribution Section

Before submission, each student should write a short accurate statement of what they personally
implemented, tested, documented or presented. This is important for the oral defence.
