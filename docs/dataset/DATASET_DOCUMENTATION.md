# SmartLoan Analytics — Dataset Documentation

## Dataset Name
SmartLoan Synthetic Loan Portfolio Dataset

## Purpose
This dataset supports the SmartLoan Analytics BICT Python Programming Assignment.
It provides enough realistic loan records to demonstrate data management, eligibility
scoring, repayment analysis, overdue-risk ranking, visualization and reporting.

## Dataset Size
The Phase 8 generator creates:

- 220 customer records
- 650 loan records
- repayment records for disbursed/completed/overdue loans
- penalty records for overdue loans

The 650 loan records exceed the assignment minimum of 500 records.

## Source of Data
The dataset is self-generated synthetic data. It was not copied from a bank, microfinance
institution, university, credit bureau or real customer database.

The generator is stored in:

    tools/generate_dataset.py

A fixed random seed is used so the dataset can be reproduced consistently for testing,
Git history, demonstrations and oral defence.

## Data Generation Process
The group first identified fields needed by the SmartLoan system, including customer
profile, employment, income, loan amount, interest rate, term, dates, status, eligibility
score, repayments and penalties.

The generator creates synthetic customers, assigns realistic income ranges by employment
type and then generates loan applications over roughly one year.

Eligibility scores are calculated using the project's transparent rule-based eligibility
algorithm. Loan statuses are distributed across Pending, Approved, Rejected, Disbursed,
Completed and Overdue categories.

Repayments are generated only for relevant loan states. Completed loans are fully repaid,
Disbursed loans have partial repayments and Overdue loans may have partial repayments plus
penalties.

## Main CSV Fields
| Field | Description |
|---|---|
| loan_id | Unique loan identifier |
| customer_code | Synthetic customer code |
| customer_name | Synthetic customer name |
| employment_status | Employment category |
| monthly_income | Synthetic monthly income |
| principal | Loan principal |
| annual_interest_rate | Annual interest rate |
| term_months | Loan term |
| application_date | Loan application date |
| approval_date | Approval date where applicable |
| disbursement_date | Disbursement date where applicable |
| due_date | Final due date where applicable |
| status | Loan status |
| eligibility_score | Rule-based eligibility score |
| purpose | Loan purpose |
| total_repaid | Total repayments received |
| outstanding_penalties | Unpaid penalties |

## Ethical Considerations
The dataset is synthetic and intended only for academic software development.

It does not contain real customer identities, NRC numbers, phone numbers, bank-account
details, credit histories or confidential financial information.

Synthetic data reduces privacy and confidentiality risks while still allowing students
to demonstrate loan-management and analytics functionality.

The eligibility score is an academic rule-based model only. It must not be presented as
a real credit-scoring or lending-decision model.

## Data Quality Controls
1. Customer codes are unique.
2. Synthetic National IDs are unique.
3. Loans reference valid customers.
4. Loan amounts and interest rates use realistic bounded values.
5. Approval dates follow application dates.
6. Disbursement dates follow approval dates.
7. Due dates follow disbursement dates.
8. Completed loans are fully repaid.
9. Overdue loans have due dates before the current date.
10. Repayment reference numbers are unique.
11. Penalties are linked only to loan records.
12. A fixed random seed makes the dataset reproducible.

## Limitations
First, synthetic data cannot perfectly reproduce the lending patterns of a real
microfinance or financial institution.

Second, the eligibility algorithm is simplified and does not use actual credit-bureau
information, collateral, verified employment or regulated affordability tests.

Third, simple-interest calculations are used for the academic prototype rather than every
possible real-world amortization method.

Fourth, the dataset covers approximately one year and therefore does not provide long-term
multi-year portfolio behaviour.

## Future Improvements
Future work could use properly authorized and anonymized organizational data, include
multi-year history, support richer installment schedules and add more realistic repayment
behaviour.

## Reproducing the Dataset
From the project root run:

    python -m tools.generate_dataset

This regenerates the synthetic customers, loans, repayments and penalties and exports:

    data/loan_dataset_650_records.csv

User accounts are preserved.
