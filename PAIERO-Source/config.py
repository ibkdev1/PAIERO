"""
PAIERO Application Configuration
"""

import os
import sys
from pathlib import Path

# Application Information
APP_NAME = "PAIERO"
APP_VERSION = "1.0.0"
APP_TITLE = "Système de Gestion de Paie PAIERO"
APP_SUBTITLE = "Logiciel Professionnel de Gestion de Paie"
COMPANY_NAME = "ABDC"


def get_data_dir():
    """
    Get application data directory based on platform

    Returns:
        str: Path to application data directory
    """
    if sys.platform == 'darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support')
    elif sys.platform == 'win32':  # Windows
        base_dir = os.path.expanduser('~/AppData/Local')
    else:  # Linux and others
        base_dir = os.path.expanduser('~/.local/share')

    data_dir = os.path.join(base_dir, APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# Database Configuration
DATABASE_NAME = "paiero.db"
DATABASE_PATH = os.path.join(get_data_dir(), DATABASE_NAME)

# Backup Configuration
BACKUP_DIR = os.path.join(get_data_dir(), "backups")
BACKUP_RETENTION_DAYS = 30

# Payroll Calculation Rates
INPS_EMPLOYEE_RATE = 0.036  # 3.6%
INPS_EMPLOYER_RATE = 0.164  # 16.4%
AMO_EMPLOYEE_RATE = 0.0306  # 3.06%
AMO_EMPLOYER_RATE = 0.035   # 3.5%
TL_RATE = 0.01              # 1% - Labor tax
TFP_RATE = 0.02             # 2% - Professional training
ATEJ_RATE = 0.02            # 2% - Young workers employment
CFE_RATE = 0.035            # 3.5% - Business tax

# Transport allowance
TRANSPORT_ALLOWANCE_RATE = 0.10  # 10% of base salary

# UI Configuration
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 820
WINDOW_DEFAULT_WIDTH = 1440
WINDOW_DEFAULT_HEIGHT = 920

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATE_DISPLAY_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Number formatting
CURRENCY_SYMBOL = "CFA"
DECIMAL_PLACES = 2

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "paiero.log"

# CSV Import/Export
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ","

# Reports
REPORTS_DIR = os.path.join(get_data_dir(), "reports_output")
PDF_PAGE_SIZE = "A4"

# Create necessary directories
def initialize_directories():
    """Create application directories if they don't exist"""
    dirs = [BACKUP_DIR, REPORTS_DIR]
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


# Application-wide settings
class Settings:
    """Application settings singleton"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.database_path = DATABASE_PATH
            self.backup_dir = BACKUP_DIR
            self.reports_dir = REPORTS_DIR
            self.initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
