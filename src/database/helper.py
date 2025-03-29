import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from graph.schema import Decision, AnalystSignal
from .setup import DB_PATH
from util.logger import logger

class DeepFundDB:
    def __init__(self):
        self.db_path = DB_PATH

    def _get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # access columns by name
        return conn

    def get_config_id_by_name(self, exp_name: str) -> Optional[str]:
        """Get config id by experiment name."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM config WHERE exp_name = ?', (exp_name,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row['id']
            return None
        except Exception as e:
            logger.error(f"Config not found: {e}")
            return None

    def create_config(self, config) -> Optional[str]:
        """Create a new config entry."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            config_id = str(uuid.uuid4())
            has_planner = not config.get('workflow_analysts', None)
            cursor.execute('''
                INSERT INTO config (id, exp_name, updated_at, has_planner, llm_model, llm_provider)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                config_id,
                config.exp_name,
                datetime.now().isoformat(),
                has_planner,
                config.llm_model,
                config.llm_provider
            ))
            
            conn.commit()
            conn.close()
            return config_id
        except Exception as e:
            logger.error(f"Error creating config: {e}")
            return None

    def get_latest_portfolio(self, config_id: str) -> Optional[Dict]:
        """Get the latest portfolio for a config."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM portfolio 
                WHERE config_id = ? 
                ORDER BY updated_at DESC 
                LIMIT 1
            ''', (config_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'cashflow': row['cashflow'],
                    'positions': json.loads(row['positions'])
                }
            return None
        except Exception as e:
            logger.error(f"Portfolio not found: {e}")
            return None

    def create_portfolio(self, config_id: str, cashflow: float) -> Optional[str]:
        """Create a new portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            portfolio_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO portfolio (id, config_id, updated_at, cashflow, total_assets, positions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                portfolio_id,
                config_id,
                datetime.now().isoformat(),
                cashflow,
                cashflow,
                json.dumps({})
            ))
            
            conn.commit()
            conn.close()
            return portfolio_id
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            return None

    def update_portfolio(self, config_id: str, portfolio: Dict) -> bool:
        """update portfolio incrementally."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            total_assets = portfolio['cashflow'] + sum(position['value'] for position in portfolio['positions'].values())
            
            cursor.execute('''
                INSERT INTO portfolio (id, config_id, updated_at, cashflow, total_assets, positions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                portfolio['id'],
                config_id,
                datetime.now().isoformat(),
                portfolio['cashflow'],
                total_assets,
                json.dumps(portfolio['positions'])
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
            return False 
        
    def save_decision(self, portfolio_id: str, ticker: str, prompt: str, decision: Decision):
        """Save a new decision."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            decision_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO decision (id, portfolio_id, updated_at, ticker, llm_prompt, 
                                   action, shares, price, justification)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_id,
                portfolio_id,
                datetime.now().isoformat(),
                ticker,
                prompt,
                str(decision.action),
                decision.shares,
                decision.price,
                decision.justification
            ))
            
            conn.commit()
            conn.close()
            return decision_id
        except Exception as e:
            logger.error(f"Error saving decision: {e}")
            return None

    def save_signal(self, portfolio_id: str, analyst: str, ticker: str, prompt: str, signal: AnalystSignal):
        """Save a new signal."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            signal_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO signal (id, portfolio_id, updated_at, ticker, llm_prompt,
                                  analyst, signal, justification)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_id,
                portfolio_id,
                datetime.now().isoformat(),
                ticker,
                prompt,
                analyst,
                str(signal.signal),
                signal.justification
            ))
            
            conn.commit()
            conn.close()
            return signal_id
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            return None

    def get_portfolio_decisions(self, portfolio_id: str) -> List[Dict]:
        """Get all decisions for a portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM decision 
                WHERE portfolio_id = ?
                ORDER BY updated_at DESC
            ''', (portfolio_id,))
            
            decisions = []
            for row in cursor.fetchall():
                decisions.append({
                    'id': row['id'],
                    'portfolio_id': row['portfolio_id'],
                    'updated_at': row['updated_at'],
                    'ticker': row['ticker'],
                    'llm_prompt': row['llm_prompt'],
                    'action': row['action'],
                    'shares': row['shares'],
                    'price': row['price'],
                    'justification': row['justification']
                })
            
            conn.close()
            return decisions
        except Exception as e:
            print(f"Error getting portfolio decisions: {e}")
            return []

## init global instance
db = DeepFundDB()