-- PAIERO Payroll Application - Database Schema
-- SQLite Database Schema for Payroll Management System

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: employees
-- Master employee data
-- ============================================================================
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,          -- N° Mle (e.g., "001", "002")
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    position TEXT,                          -- Fonction
    hire_date DATE NOT NULL,               -- Date d'embauche
    contract_end_date DATE,                -- Fin Contrat
    seniority REAL,                        -- Ancienneté (in years)
    status_code TEXT,                      -- C0-C15 (single), M0-M20 (married)
    agency_code TEXT,                      -- Agence
    department_code TEXT,                  -- Département
    category TEXT,                         -- Cat 10 Ech B, etc.
    address TEXT,                          -- Adresse
    inps_number TEXT,                      -- N° INPS
    inps_allocation_number TEXT,           -- N° All. INPS
    bank_name TEXT,                        -- Nom Banque
    bank_account TEXT,                     -- N° Cpte Banque
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_status ON employees(status_code);
CREATE INDEX idx_employees_category ON employees(category);
CREATE INDEX idx_employees_active ON employees(is_active);

-- ============================================================================
-- TABLE: payroll_periods
-- Monthly payroll processing periods
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_periods (
    period_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    payment_date DATE,
    is_finalized BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period_start_date, period_end_date)
);

CREATE INDEX idx_periods_dates ON payroll_periods(period_start_date, period_end_date);
CREATE INDEX idx_periods_finalized ON payroll_periods(is_finalized);

-- ============================================================================
-- TABLE: payroll_records
-- Monthly salary calculations per employee
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    employee_id TEXT NOT NULL,

    -- Work tracking
    days_worked INTEGER DEFAULT 0,
    days_absent INTEGER DEFAULT 0,

    -- Base and allowances
    base_salary REAL DEFAULT 0,                    -- Sal de Base Maj.
    ind_spe_1973 REAL DEFAULT 0,                  -- Ind. Spé 1973
    ind_cher_vie_1974 REAL DEFAULT 0,             -- Ind. Cher Vie 1974
    ind_spe_1982 REAL DEFAULT 0,                  -- Ind. Spé 1982
    ind_sol_1991 REAL DEFAULT 0,                  -- Ind. Sol 1991
    ind_transport REAL DEFAULT 0,                  -- Ind. Trspt 10% Sal Base
    family_allowance REAL DEFAULT 0,               -- Allocation Charge de Famille
    recall_salary_increase REAL DEFAULT 0,         -- Rappel Aug. Sal.
    vehicle_allowance REAL DEFAULT 0,              -- Indemnité de Monture personnelle
    risk_premium REAL DEFAULT 0,                   -- Prime de Risque
    responsibility_allowance REAL DEFAULT 0,       -- Indemnité Responsabilité
    overtime_pay REAL DEFAULT 0,                   -- Sursalaire

    -- Calculated totals
    gross_salary REAL DEFAULT 0,                   -- Salaire Brut
    non_taxable_total REAL DEFAULT 0,              -- Total Ind. Non Imposable
    non_inps_amo_total REAL DEFAULT 0,             -- Total Non soumis INPS/AMO
    inps_amo_base REAL DEFAULT 0,                  -- Base INPS/AMO
    benefits_in_kind REAL DEFAULT 0,               -- Total Avant. en Nature
    taxable_gross_monthly REAL DEFAULT 0,          -- Salaire Brut Mensuel Imp.

    -- Employee deductions
    inps_employee REAL DEFAULT 0,                  -- INPS Part Sal. (3.6%)
    amo_employee REAL DEFAULT 0,                   -- AMO Part Sal. (3.06%)
    taxable_annual_base REAL DEFAULT 0,            -- Base Imp. Annuel
    family_charge_reduction_rate REAL DEFAULT 0,   -- Taux Réduction pour Charges Famille
    income_tax_net REAL DEFAULT 0,                 -- ITS Net

    -- Net calculations
    net_salary REAL DEFAULT 0,                     -- Salaire Net
    advances_loans_deduction REAL DEFAULT 0,       -- Avance/Prêt
    net_to_pay REAL DEFAULT 0,                     -- Net à Payer

    -- Employer costs
    inps_employer REAL DEFAULT 0,                  -- INPS Part Pat. (16.4%)
    amo_employer REAL DEFAULT 0,                   -- AMO Part Pat. (3.5%)
    tl_tax REAL DEFAULT 0,                         -- TL -1%
    tfp_tax REAL DEFAULT 0,                        -- TFP -2%
    atej_tax REAL DEFAULT 0,                       -- ATEJ -2%
    cfe_tax REAL DEFAULT 0,                        -- CFE -3.5%
    total_payroll_cost REAL DEFAULT 0,             -- Masse Salariale

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (period_id) REFERENCES payroll_periods(period_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    UNIQUE(period_id, employee_id)
);

CREATE INDEX idx_payroll_period ON payroll_records(period_id);
CREATE INDEX idx_payroll_employee ON payroll_records(employee_id);

-- ============================================================================
-- TABLE: loans_advances
-- Employee loans and salary advances
-- ============================================================================
CREATE TABLE IF NOT EXISTS loans_advances (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    loan_type TEXT CHECK(loan_type IN ('Prêt', 'Avance')),
    total_amount REAL NOT NULL,
    remaining_balance REAL NOT NULL,
    grant_date DATE NOT NULL,                      -- Date d'octroi prêt
    first_payment_date DATE,                       -- Date 1ère échéance
    end_date DATE,                                 -- Date Fin
    duration_months INTEGER,                       -- Durée
    monthly_payment REAL,                          -- Mensualité
    notes TEXT,                                    -- Notes/commentaires
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE INDEX idx_loans_employee ON loans_advances(employee_id);
CREATE INDEX idx_loans_active ON loans_advances(is_active);

-- ============================================================================
-- TABLE: loan_payments
-- Monthly loan payment schedule and tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    period_id INTEGER,                             -- NULL until linked to payroll period
    payment_date DATE NOT NULL,
    scheduled_amount REAL NOT NULL,
    actual_amount REAL DEFAULT 0,
    is_paid BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans_advances(loan_id),
    FOREIGN KEY (period_id) REFERENCES payroll_periods(period_id)
);

CREATE INDEX idx_payments_loan ON loan_payments(loan_id);
CREATE INDEX idx_payments_period ON loan_payments(period_id);
CREATE INDEX idx_payments_status ON loan_payments(is_paid);

-- ============================================================================
-- TABLE: salary_scale_ccfc
-- CCFC Convention Collective salary scale
-- ============================================================================
CREATE TABLE IF NOT EXISTS salary_scale_ccfc (
    scale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,                        -- Cat 1 Ech A, Cat 10 Ech B, etc.
    base_salary_1958 REAL,                        -- Sal/Base 1958/59
    ind_spe_1973 REAL,                            -- Ind. Spé 1973
    ind_cher_vie_1974 REAL,                       -- Ind. Cher Vie 1974
    maj_1976 REAL,                                -- Maj. 10% 1976
    maj_1978 REAL,                                -- Maj. 5% 1978
    maj_1980 REAL,                                -- Maj. 10% 1980
    ind_spe_1982 REAL,                            -- Ind. Spé 1982
    maj_3000_or_10pct REAL,                       -- Maj. 3000 ou 10% max
    ind_sol_1991 REAL,                            -- Ind. Sol 1991
    maj_pre_1994 REAL,                            -- Maj. 10% av-94
    maj_1994 REAL,
    maj_1997 REAL,
    maj_1998 REAL,
    maj_1999 REAL,
    maj_2008 REAL,
    maj_2009 REAL,
    total_gross REAL,                             -- Total Brut
    cumulative_maj REAL,                          -- Cumul maj
    adjusted_base_salary REAL,                    -- Sal de Base Maj.
    effective_date DATE,
    UNIQUE(category, effective_date)
);

CREATE INDEX idx_scale_category ON salary_scale_ccfc(category);

-- ============================================================================
-- TABLE: parameters
-- Configuration and lookup tables
-- ============================================================================
CREATE TABLE IF NOT EXISTS parameters (
    param_id INTEGER PRIMARY KEY AUTOINCREMENT,
    param_type TEXT NOT NULL,                      -- 'STATUS', 'TAX_BRACKET', 'DEPARTMENT', 'AGENCY', 'RATE'
    param_code TEXT NOT NULL,
    param_value TEXT,
    numeric_value REAL,
    description TEXT,
    effective_date DATE,
    UNIQUE(param_type, param_code)
);

CREATE INDEX idx_params_type ON parameters(param_type);
CREATE INDEX idx_params_code ON parameters(param_code);

-- ============================================================================
-- TABLE: users
-- System users with authentication and roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,                 -- Login username
    password_hash TEXT NOT NULL,                   -- Hashed password (bcrypt)
    full_name TEXT NOT NULL,                       -- User's full name
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Users update trigger
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;

-- ============================================================================
-- TABLE: user_permissions
-- Granular permissions for user access control
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_permissions (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    -- Employee permissions
    can_view_employees BOOLEAN DEFAULT 1,
    can_edit_employees BOOLEAN DEFAULT 0,
    can_delete_employees BOOLEAN DEFAULT 0,
    -- Payroll permissions
    can_view_payroll BOOLEAN DEFAULT 1,
    can_process_payroll BOOLEAN DEFAULT 0,
    can_finalize_payroll BOOLEAN DEFAULT 0,
    -- Loan permissions
    can_view_loans BOOLEAN DEFAULT 1,
    can_manage_loans BOOLEAN DEFAULT 0,
    -- Report permissions
    can_generate_reports BOOLEAN DEFAULT 1,
    can_export_data BOOLEAN DEFAULT 0,
    -- Parameter permissions
    can_view_parameters BOOLEAN DEFAULT 0,
    can_modify_parameters BOOLEAN DEFAULT 0,
    -- User management permissions (admin only)
    can_manage_users BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

CREATE INDEX idx_permissions_user ON user_permissions(user_id);

-- Permissions update trigger
CREATE TRIGGER IF NOT EXISTS update_permissions_timestamp
AFTER UPDATE ON user_permissions
FOR EACH ROW
BEGIN
    UPDATE user_permissions SET updated_at = CURRENT_TIMESTAMP WHERE permission_id = NEW.permission_id;
END;

-- ============================================================================
-- TABLE: tax_brackets
-- Progressive income tax rates
-- ============================================================================
CREATE TABLE IF NOT EXISTS tax_brackets (
    bracket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    min_income REAL NOT NULL,
    max_income REAL,                               -- NULL for highest bracket
    tax_rate REAL NOT NULL,
    cumulative_tax REAL DEFAULT 0,
    effective_date DATE NOT NULL
);

CREATE INDEX idx_tax_income ON tax_brackets(min_income, max_income);

-- ============================================================================
-- TABLE: audit_log
-- Change tracking for all operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT CHECK(action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values TEXT,                               -- JSON format
    new_values TEXT,                               -- JSON format
    user_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- ============================================================================
-- TRIGGERS for automatic timestamp updates
-- ============================================================================

-- Employees update trigger
CREATE TRIGGER IF NOT EXISTS update_employees_timestamp
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    UPDATE employees SET updated_at = CURRENT_TIMESTAMP WHERE employee_id = NEW.employee_id;
END;

-- Payroll periods update trigger
CREATE TRIGGER IF NOT EXISTS update_periods_timestamp
AFTER UPDATE ON payroll_periods
FOR EACH ROW
BEGIN
    UPDATE payroll_periods SET updated_at = CURRENT_TIMESTAMP WHERE period_id = NEW.period_id;
END;

-- Payroll records update trigger
CREATE TRIGGER IF NOT EXISTS update_payroll_timestamp
AFTER UPDATE ON payroll_records
FOR EACH ROW
BEGIN
    UPDATE payroll_records SET updated_at = CURRENT_TIMESTAMP WHERE record_id = NEW.record_id;
END;

-- Loans update trigger
CREATE TRIGGER IF NOT EXISTS update_loans_timestamp
AFTER UPDATE ON loans_advances
FOR EACH ROW
BEGIN
    UPDATE loans_advances SET updated_at = CURRENT_TIMESTAMP WHERE loan_id = NEW.loan_id;
END;

-- Loan payments update trigger
CREATE TRIGGER IF NOT EXISTS update_payments_timestamp
AFTER UPDATE ON loan_payments
FOR EACH ROW
BEGIN
    UPDATE loan_payments SET updated_at = CURRENT_TIMESTAMP WHERE payment_id = NEW.payment_id;
END;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
