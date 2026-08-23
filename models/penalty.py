from dataclasses import dataclass


@dataclass
class Penalty:
    penalty_id: int | None
    loan_id: int
    amount: float
    reason: str | None = None
    paid: bool = False
