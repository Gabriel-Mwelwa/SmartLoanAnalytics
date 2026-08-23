from dataclasses import dataclass


@dataclass
class Customer:
    customer_id: int | None
    customer_code: str
    full_name: str
    national_id: str | None
    phone: str | None
    email: str | None
    address: str | None
    employment_status: str | None
    monthly_income: float
    status: str = 'Active'

    @property
    def is_active(self) -> bool:
        return self.status == 'Active'
