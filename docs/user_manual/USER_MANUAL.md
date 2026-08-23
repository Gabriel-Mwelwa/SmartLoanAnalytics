# SmartLoan Analytics — User Manual

**Group Members**

- CHOLA CHILUFYA — 2410856
- Sibamba Mumbula — 2410781
- EUNICE KUNDA — 2410776
- Caroline Musonda — 2300908
- Gabriel Mwelwa — 2410761
- Mumba Adrian — 2611537


## 1. Introduction

SmartLoan Analytics is a Python desktop application for managing customers, loans, repayments,
analytics and reports. This manual explains installation, startup and normal system use.

## 2. Requirements

Install a compatible Python 3 environment. Install the project dependencies using the supplied
requirements file.

From the project folder run:

```bash
python -m pip install -r requirements.txt
```

## 3. Running the Application

Open a terminal in the `SmartLoanAnalytics` project folder and run:

```bash
python main.py
```

The application initializes the SQLite database and opens the login screen.

## 4. Login

Enter a valid username and password and select Login. Invalid credentials are rejected and the
attempt is logged.

If registration is enabled for the current workflow, create an account using valid details and
a strong password. Passwords require at least eight characters with uppercase, lowercase and a
number.

## 5. Dashboard

After successful authentication the role-aware dashboard provides access to permitted functions.
Available areas include customer management, loans, repayments, analytics and reports.
Administrator-only functions are restricted according to permissions.

## 6. Customer Management

Use Customer Management to create or maintain customer records.

When creating a customer:

1. Enter the customer code.
2. Enter the full name.
3. Enter identification/contact details where required.
4. Select or enter employment information.
5. Enter monthly income.
6. Confirm the customer status.
7. Save the record.

The system rejects invalid or duplicate values according to its validation rules.

Use the search/filter controls to locate existing customers. Select a record before editing or
performing another record-specific operation.

## 7. Loan Applications

To create a loan application:

1. Select a valid active customer.
2. Enter the requested principal.
3. Enter the annual interest rate.
4. Enter the loan term in months.
5. Enter the purpose where required.
6. Submit the application.

The system validates the input and calculates the project's eligibility score. The score is an
academic decision-support indicator and not a real regulated credit score.

## 8. Loan Approval and Rejection

Authorized users can review pending applications and perform permitted decision actions.

An approved loan can proceed to disbursement. A rejected loan remains in the historical record
with its rejected status.

## 9. Disbursement

Select an approved loan and use the relevant disbursement action. The system records the
disbursement information and prepares the loan for repayment processing.

## 10. Repayments

To record a repayment:

1. Select an eligible disbursed or overdue loan.
2. Enter the payment amount.
3. Enter the payment date.
4. Select the payment method.
5. Enter a unique reference number.
6. Save the repayment.

The system prevents negative/zero payments, invalid dates, duplicate references and payments
above the outstanding balance.

## 11. Overdue Loans and Penalties

Loans that remain unpaid after the relevant due date can be identified as overdue. Penalty
records can be associated with overdue loans according to the prototype's rules.

## 12. Analytics Dashboard

Open Analytics to view portfolio indicators and visualizations.

The dashboard can display information such as:

- total customers;
- total loans;
- pending/approved/rejected/disbursed/completed/overdue loans;
- approval rate;
- approved principal;
- repayments collected;
- outstanding portfolio;
- outstanding penalties;
- monthly application trends;
- monthly repayment trends;
- top customers;
- overdue-risk rankings.

## 13. Reports

Open Reports to generate:

- Management PDF
- Management CSV
- Loan Records CSV
- Repayment Records CSV

Generated reports are stored in the project's report directories. The PDF includes analytical
summaries, charts, rankings and management recommendations.

## 14. Dataset Regeneration

The packaged academic dataset can be regenerated from the project root using:

```bash
python -m tools.generate_dataset
```

This recreates the synthetic operational dataset and exports the loan CSV. Do not run this on a
database containing information you intend to preserve without understanding the generator's
reset behaviour.

## 15. Algorithm Benchmark

For an illustrative demonstration of algorithm timing, run:

```bash
python -m tools.benchmark_algorithms
```

Timing results depend on the computer. Big O complexity should be explained from the algorithm
structure rather than from one timing measurement.

## 16. Running Automated Tests

From the project root run:

```bash
python -m pytest -q
```

A successful run should complete without failed tests. The exact number may increase as the
project is extended.

## 17. Logs

Application logs are stored under the project's log directory. Logs are useful when diagnosing
errors or demonstrating that system events are recorded.

## 18. Common Problems

### Python command is not recognized
Install Python and ensure it is available in the operating-system PATH, or use the Python
launcher available on the computer.

### ModuleNotFoundError
Run:

```bash
python -m pip install -r requirements.txt
```

from the correct project directory.

### Database error
Close duplicate application instances, verify file/folder permissions and inspect the
application log.

### Report cannot be created
Verify that ReportLab and Matplotlib are installed and that the reports folder is writable.

### Login fails
Check the username/password carefully. Do not bypass authentication by directly modifying the
database.

## 19. Safe Shutdown

Use Logout to end the current session. Close the application normally rather than terminating
Python while a database operation is being performed.

## 20. Backup

For an academic demonstration, make a copy of the project folder and database before performing
major experiments or regeneration. Git should be used for source-code history, but database
backup is a separate concern.

## 21. Important Academic Note

Every group member should practice running the application, locating the important modules,
explaining all three algorithms, changing a small validation/business rule, running the tests
and identifying important Git commits.

The oral defence evaluates understanding, not only whether the submitted application runs.
