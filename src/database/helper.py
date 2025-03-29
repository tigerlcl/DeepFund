import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .setup import DB_PATH

class DatabaseHelper:
    def __init__(self):
        self.db_path = DB_PATH

    def _get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_portfolio(self, name: str, cashflow: float, total_assets: float, 
                      positions: Dict, llm_model: Optional[str] = None, 
                      llm_provider: Optional[str] = None) -> Optional[str]:
        """Save a new portfolio."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            portfolio_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO portfolio (id, name, updated_at, cashflow, total_assets, positions, llm_model, llm_provider)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                portfolio_id,
                name,
                datetime.now().isoformat(),
                cashflow,
                total_assets,
                json.dumps(positions),
                llm_model,
                llm_provider
            ))
            
            conn.commit()
            conn.close()
            return portfolio_id
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            return None

    def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Get a portfolio by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM portfolio WHERE id = ?', (portfolio_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'updated_at': row['updated_at'],
                    'cashflow': row['cashflow'],
                    'total_assets': row['total_assets'],
                    'positions': json.loads(row['positions']),
                    'llm_model': row['llm_model'],
                    'llm_provider': row['llm_provider']
                }
            return None
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return None

    def save_decision(self, portfolio_id: str, ticker: str, action: str, 
                     shares: int, llm_prompt: Optional[str] = None,
                     price: Optional[float] = None, 
                     justification: Optional[str] = None) -> Optional[str]:
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
                llm_prompt,
                action,
                shares,
                price,
                justification
            ))
            
            conn.commit()
            conn.close()
            return decision_id
        except Exception as e:
            print(f"Error saving decision: {e}")
            return None

    def save_signal(self, decision_id: str, ticker: str, signal: str,
                   llm_prompt: Optional[str] = None,
                   justification: Optional[str] = None) -> Optional[str]:
        """Save a new signal."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            signal_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO signal (id, decision_id, updated_at, ticker, llm_prompt,
                                  signal, justification)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_id,
                decision_id,
                datetime.now().isoformat(),
                ticker,
                llm_prompt,
                signal,
                justification
            ))
            
            conn.commit()
            conn.close()
            return signal_id
        except Exception as e:
            print(f"Error saving signal: {e}")
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

    def get_decision_signals(self, decision_id: str) -> List[Dict]:
        """Get all signals for a decision."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM signal 
                WHERE decision_id = ?
                ORDER BY updated_at DESC
            ''', (decision_id,))
            
            signals = []
            for row in cursor.fetchall():
                signals.append({
                    'id': row['id'],
                    'decision_id': row['decision_id'],
                    'updated_at': row['updated_at'],
                    'ticker': row['ticker'],
                    'llm_prompt': row['llm_prompt'],
                    'signal': row['signal'],
                    'justification': row['justification']
                })
            
            conn.close()
            return signals
        except Exception as e:
            print(f"Error getting decision signals: {e}")
            return []

    def log_agent_activity(self, portfolio_id: int, agent_type: str, agent_name: str, 
                          ticker: str, activity_data: Dict, execution_id: Optional[str] = None) -> bool:
        """Log an agent activity (signal or action)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate execution_id if not provided
            if not execution_id:
                execution_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO agent_activity 
                (execution_id, portfolio_id, agent_type, agent_name, ticker, activity_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                execution_id,
                portfolio_id,
                agent_type,
                agent_name,
                ticker,
                json.dumps(activity_data)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging agent activity: {e}")
            return False

    def get_activities_by_execution(self, execution_id: str) -> List[Dict]:
        """Get all activities for a specific execution."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM agent_activity 
                WHERE execution_id = ?
                ORDER BY activity_time
            ''', (execution_id,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'activity_id': row['activity_id'],
                    'execution_id': row['execution_id'],
                    'portfolio_id': row['portfolio_id'],
                    'activity_time': row['activity_time'],
                    'agent_type': row['agent_type'],
                    'agent_name': row['agent_name'],
                    'ticker': row['ticker'],
                    'activity_data': json.loads(row['activity_data'])
                })
            
            conn.close()
            return activities
        except Exception as e:
            print(f"Error getting activities by execution: {e}")
            return []

    def get_portfolio_history(self, portfolio_id: int, 
                            start_time: Optional[str] = None, 
                            end_time: Optional[str] = None) -> List[Dict]:
        """Get portfolio history within a time range."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM portfolio WHERE portfolio_id = ?"
            params = [portfolio_id]
            
            if start_time:
                query += " AND snapshot_time >= ?"
                params.append(start_time)
            if end_time:
                query += " AND snapshot_time <= ?"
                params.append(end_time)
                
            query += " ORDER BY snapshot_time"
            
            cursor.execute(query, params)
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'portfolio_id': row['portfolio_id'],
                    'snapshot_time': row['snapshot_time'],
                    'cashflow': row['cashflow'],
                    'positions': json.loads(row['positions']),
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                })
            
            conn.close()
            return history
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return [] 