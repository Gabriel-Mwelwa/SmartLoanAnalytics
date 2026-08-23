from dataclasses import dataclass


@dataclass
class User:
    user_id: int | None
    full_name: str
    username: str
    email: str
    role: str

    def get_permissions(self) -> set[str]:
        return {'read'}


@dataclass
class Administrator(User):
    def get_permissions(self) -> set[str]:
        return {'read','create','update','delete','manage_users','approve_loans','reports'}


@dataclass
class LoanOfficer(User):
    def get_permissions(self) -> set[str]:
        return {'read','create','update','manage_customers','manage_loans','record_repayment','reports'}
