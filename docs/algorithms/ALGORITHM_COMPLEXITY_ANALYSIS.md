# SmartLoan Analytics — Algorithms and Computational Complexity Analysis

## Purpose

The assignment requires at least three original algorithms and formal analysis of their
operation, time complexity, space complexity, efficiency and possible improvements.

SmartLoan Analytics uses three algorithms that directly support the loan-management problem:

1. Loan Eligibility Scoring
2. Repayment Schedule Generation
3. Loan Risk Ranking

The algorithms are intentionally transparent so every student can explain and modify them
during the oral defence.

---

# Algorithm 1 — Loan Eligibility Scoring

## Problem Solved

Before a loan is approved, the system needs a simple way to estimate whether the requested
amount appears affordable relative to a customer's monthly income, existing debt and loan term.

This algorithm is an academic rule-based score and is **not** presented as a real bank,
credit-bureau or regulated lending model.

## Inputs

- monthly income
- requested loan amount
- term in months
- existing debt

## Output

A score between 0 and 100.

Higher scores indicate stronger eligibility under the project rules.

## Pseudocode

```text
ELIGIBILITY_SCORE(income, amount, term, debt)

    IF income <= 0 OR amount <= 0 OR term <= 0
        RETURN 0
    END IF

    amount_ratio ← amount / income
    debt_ratio ← MAX(0, debt) / income

    score ← 100

    score ← score - MIN(55, amount_ratio × 8)
    score ← score - MIN(30, debt_ratio × 20)

    IF term > 36
        score ← score - 10
    ELSE IF term > 24
        score ← score - 5
    END IF

    IF score < 0
        score ← 0
    END IF

    IF score > 100
        score ← 100
    END IF

    RETURN score
```

## Example

Monthly income = K10,000  
Requested loan = K5,000  
Existing debt = K2,000  
Term = 12 months

Amount ratio = 5,000 / 10,000 = 0.5  
Debt ratio = 2,000 / 10,000 = 0.2

The algorithm subtracts bounded penalties from 100 and returns the resulting score.

## Time Complexity

The algorithm performs a fixed number of arithmetic and comparison operations.

It does not loop through customers, loans or repayments.

Therefore:

`Time Complexity = O(1)`

## Space Complexity

Only a small fixed set of scalar variables is used:

`Space Complexity = O(1)`

## Efficiency

The algorithm is extremely fast and remains constant-time even if the database grows from
hundreds to millions of records, provided the four input values are already available.

## Improvements

A real system could include:

- verified income history,
- debt-service ratio,
- credit-bureau information,
- collateral,
- employment stability,
- repayment history,
- institution-specific affordability rules.

Those changes would improve business realism, not necessarily the algorithm's Big O class.

---

# Algorithm 2 — Repayment Schedule Generation

## Problem Solved

After a loan is approved, the system must produce installment information showing how much is
due for each month and how the outstanding amount changes over the repayment term.

SmartLoan Analytics uses simple interest for the academic prototype.

## Inputs

- principal
- annual interest rate
- loan term in months

## Outputs

A list containing one repayment row per month:

- installment number,
- amount due,
- remaining amount after payment.

## Pseudocode

```text
BUILD_REPAYMENT_SCHEDULE(principal, annual_rate, term_months)

    years ← term_months / 12
    interest ← principal × (annual_rate / 100) × years
    total_payable ← principal + interest

    monthly_payment ← total_payable / term_months
    remaining ← total_payable

    schedule ← empty list

    FOR month ← 1 TO term_months

        IF month < term_months
            payment ← monthly_payment
        ELSE
            payment ← remaining
        END IF

        remaining ← MAX(0, remaining - payment)

        ADD (
            month,
            payment,
            remaining
        ) TO schedule

    END FOR

    RETURN schedule
```

## Time Complexity

Let:

`n = number of repayment months`

The loop executes exactly once for every repayment month.

Therefore:

`Time Complexity = O(n)`

For a 12-month loan, the loop executes 12 times.  
For a 36-month loan, it executes 36 times.

## Space Complexity

The returned schedule contains one entry for each month:

`Space Complexity = O(n)`

## Efficiency

The algorithm scales linearly. Doubling the loan term approximately doubles the number of
schedule rows generated.

For the project maximum of 60 months, this is very efficient.

## Improvements

Future versions could implement:

- reducing-balance amortization,
- exact calendar due dates,
- grace periods,
- weekly or fortnightly schedules,
- early-payment recalculation,
- variable interest rates.

---

# Algorithm 3 — Loan Risk Ranking

## Problem Solved

Management needs to identify which overdue loans should receive attention first.

The system first calculates a risk score using:

- overdue days,
- outstanding balance,
- missed-payment count.

It then ranks loans from highest risk to lowest risk.

## Inputs

A list of `n` loan-risk records.

Each record contains:

- overdue days,
- outstanding balance,
- missed-payment count.

## Output

A list ranked from highest to lowest risk.

## Risk Score Formula

The academic risk score is:

`Risk Score = (Overdue Days × 2) + (Outstanding Balance / 1000) + (Missed Payments × 10)`

## Pseudocode

```text
RANK_LOANS_BY_RISK(records)

    ranked ← empty list

    FOR each record IN records

        risk_score ←
            MAX(0, overdue_days) × 2
            + MAX(0, outstanding_balance) / 1000
            + MAX(0, missed_payments) × 10

        copy record into ranked
        store risk_score

    END FOR

    FOR i ← 0 TO length(ranked) - 1

        highest ← i

        FOR j ← i + 1 TO length(ranked) - 1

            IF ranked[j].risk_score > ranked[highest].risk_score
                highest ← j
            END IF

        END FOR

        SWAP ranked[i] WITH ranked[highest]

    END FOR

    RETURN ranked
```

## Time Complexity — Scoring Phase

Each of `n` records is visited once:

`O(n)`

Each risk score itself is O(1).

## Time Complexity — Ranking Phase

The project deliberately implements selection sort.

The approximate comparison count is:

`n(n - 1) / 2`

Therefore:

`O(n²)`

## Overall Time Complexity

`O(n + n²)`

The quadratic term dominates:

`Overall Time Complexity = O(n²)`

## Space Complexity

A working copy containing `n` ranked records is created:

`Space Complexity = O(n)`

## Why Use Manual Selection Sort?

Python's built-in sorting is faster, but the assignment asks students to demonstrate
algorithmic thinking rather than only call built-in functions.

Selection sort makes the comparison and swapping logic easy to see, explain and modify.

## Improvements

For a larger production dataset:

- Python Timsort could rank in O(n log n).
- SQL `ORDER BY` could let the database rank results.
- A heap could efficiently return only the highest-risk `k` loans.
- Risk scores could be cached when portfolio data changes.

---

# Complexity Summary

| Algorithm | Input Size | Time Complexity | Space Complexity |
|---|---:|---:|---:|
| Eligibility scoring | Fixed customer/loan inputs | O(1) | O(1) |
| Repayment schedule | n repayment months | O(n) | O(n) |
| Loan risk ranking | n loans | O(n²) | O(n) |

---

# Scaling Discussion

If the number of inputs to eligibility scoring changes only in value, not quantity, the
number of operations remains fixed.

If the repayment term doubles from 12 months to 24 months, schedule generation performs
approximately twice as many iterations.

If the number of loans in risk ranking doubles, the selection-sort phase can require
approximately four times as many comparisons. This demonstrates why quadratic algorithms
are less suitable for very large datasets.

---

# Why These Algorithms Were Selected

The algorithms represent three different complexity patterns:

- eligibility scoring demonstrates constant time O(1),
- repayment schedule generation demonstrates linear time O(n),
- risk ranking demonstrates quadratic time O(n²).

They are also directly connected to the SmartLoan problem domain instead of being unrelated
textbook algorithms.

---

# Performance Discussion with the Assignment Dataset

The packaged dataset contains 650 loan records.

Eligibility scoring remains constant-time for each application.

A repayment schedule has at most 60 iterations under the project's configured loan-term
limit.

The risk-ranking algorithm remains practical for hundreds of records, but its O(n²) selection
sort would become less attractive if a real institution had tens or hundreds of thousands
of loans.

This is why the report proposes O(n log n) or database-based alternatives for production.

---

# Oral Defence Questions

## Eligibility

**Question:** Why is eligibility scoring O(1)?  
**Answer:** It performs the same fixed number of calculations regardless of database size.

**Question:** Is this a real credit score?  
**Answer:** No. It is an academic rule-based score for demonstrating algorithmic logic and
must not be presented as a regulated lending model.

## Repayment Schedule

**Question:** Why is the schedule O(n)?  
**Answer:** The algorithm creates exactly one schedule entry for every repayment month.

**Question:** Why is space also O(n)?  
**Answer:** Because the returned schedule stores n monthly entries.

## Risk Ranking

**Question:** Why is ranking O(n²)?  
**Answer:** Selection sort uses nested comparisons over the loan list.

**Question:** Why not use sorted()?  
**Answer:** The assignment asks us to demonstrate original algorithm logic. In a real system,
we would use Python's more efficient sort or database ordering.

**Question:** What happens if the number of loans doubles?  
**Answer:** The quadratic ranking phase can take roughly four times as many comparisons.

---

# Live Modification Practice

Students should practice:

- changing the eligibility threshold/penalty weights;
- adding a maximum eligibility-score deduction;
- changing a 12-month schedule to a 6-month schedule;
- returning only the first three installments;
- adding `missed_payment_count` weight to the risk formula;
- reversing the risk ranking;
- returning only the top five risky loans.

---

# Academic Integrity Note

The group should understand each formula, loop and condition. If AI assistance is declared,
students should explain that they verified the algorithms by reading the code, testing sample
inputs, running pytest and confirming expected outputs manually.
