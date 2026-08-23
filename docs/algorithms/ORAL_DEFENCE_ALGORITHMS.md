# SmartLoan Algorithm Oral Defence Quick Sheet

## Eligibility Scoring
- File: `algorithms/eligibility_scoring.py`
- Time: O(1)
- Space: O(1)
- Inputs: income, requested amount, term, existing debt.
- Important: academic model, not real regulated credit scoring.

## Repayment Schedule
- File: `algorithms/repayment_schedule.py`
- Time: O(n)
- Space: O(n)
- n = loan term in months.
- Creates one schedule row per month.

## Risk Ranking
- File: `algorithms/risk_ranking.py`
- Score calculation per loan: O(1)
- Full manual ranking: O(n²)
- Space: O(n)
- Uses selection sort so the underlying logic is visible.
- Production improvement: Timsort/SQL/heap.

## Practice Changes
1. Change scoring weights.
2. Change the maximum term.
3. Show only first 3 installments.
4. Add another risk factor.
5. Return only top 5 high-risk loans.
6. Explain whether each modification changes Big O.
