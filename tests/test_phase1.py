from algorithms.eligibility_scoring import calculate_basic_eligibility_score
from algorithms.repayment_schedule import simple_monthly_payment
from algorithms.risk_ranking import basic_risk_score
from database import initialize_database
from config import DATABASE_PATH


def test_database_initializes():
    initialize_database()
    assert DATABASE_PATH.exists()


def test_basic_eligibility_score_range():
    score = calculate_basic_eligibility_score(5000, 10000)
    assert 0 <= score <= 100


def test_simple_monthly_payment():
    assert simple_monthly_payment(12000, 12) == 1000.0


def test_basic_risk_score_non_negative():
    assert basic_risk_score(-5, -100) == 0.0
