from dataclasses import dataclass


@dataclass
class Loan:
    loan_id: int | None
    customer_id: int
    principal: float
    annual_interest_rate: float
    term_months: int
    application_date: str
    approval_date: str | None = None
    disbursement_date: str | None = None
    due_date: str | None = None
    status: str = 'Pending'
    eligibility_score: float | None = None
    purpose: str | None = None
