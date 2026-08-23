from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'
REPORT_DIR = BASE_DIR / 'reports'
CHART_DIR = BASE_DIR / 'charts'

DATABASE_PATH = DATA_DIR / 'smartloan.db'
LOG_FILE = LOG_DIR / 'smartloan.log'

APP_NAME = 'SmartLoan Analytics'
APP_VERSION = '0.1.0'
DEFAULT_ANNUAL_INTEREST_RATE = 18.0
DEFAULT_PENALTY_RATE = 2.0
MAX_LOAN_TERM_MONTHS = 60
MIN_LOAN_AMOUNT = 100.0
