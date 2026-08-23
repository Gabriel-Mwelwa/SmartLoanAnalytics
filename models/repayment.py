from dataclasses import dataclass


@dataclass
class Repayment:
    repayment_id: int | None
    loan_id: int
    payment_date: str
    amount: float
    payment_method: str | None = None
    reference_number: str | None = None
