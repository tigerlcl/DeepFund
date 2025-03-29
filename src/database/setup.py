import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure database directory exists
DB_PATH = os.getenv("DB_PATH")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_database():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create portfolio table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        has_planner BOOLEAN NOT NULL DEFAULT FALSE,
        cashflow DECIMAL(15,2) NOT NULL,
        total_assets DECIMAL(15,2) NOT NULL,
        positions JSON NOT NULL,
        llm_model VARCHAR(50),
        llm_provider VARCHAR(50)
    )
    ''')

    # Create decision table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS decision (
        id VARCHAR(36) PRIMARY KEY,
        portfolio_id VARCHAR(36) NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ticker VARCHAR(10) NOT NULL,
        llm_prompt TEXT,
        action VARCHAR(10) NOT NULL,
        shares INTEGER NOT NULL,
        price DECIMAL(15,2),
        justification TEXT,
        FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
    )
    ''')

    # Create signal table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signal (
        id VARCHAR(36) PRIMARY KEY,
        decision_id VARCHAR(36) NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ticker VARCHAR(10) NOT NULL,
        llm_prompt TEXT,
        signal VARCHAR(10) NOT NULL,
        justification TEXT,
        FOREIGN KEY (decision_id) REFERENCES decision(id)
    )
    ''')

    # Create indices for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_updated ON portfolio(updated_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision_portfolio ON decision(portfolio_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision_updated ON decision(updated_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_decision ON signal(decision_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_updated ON signal(updated_at)')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print(f"Database initialized at {DB_PATH}") 