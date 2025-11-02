"""
Persistent storage for AI trading decisions
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger


class DecisionStore:
    """Store AI decisions persistently in a JSON file"""
    
    def __init__(self, filepath: str = "logs/decisions.json"):
        self.filepath = filepath
        self.decisions: List[Dict[str, Any]] = []
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self):
        """Ensure the directory exists"""
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load(self):
        """Load decisions from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.decisions = json.load(f)
                logger.info(f"Loaded {len(self.decisions)} decisions from {self.filepath}")
            except Exception as e:
                logger.error(f"Error loading decisions: {e}")
                self.decisions = []
        else:
            self.decisions = []
    
    def _save(self):
        """Save decisions to file"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.decisions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving decisions: {e}")
    
    def add_decision(self, decision: Dict[str, Any], market_data: Dict[str, Any], portfolio_state: Dict[str, Any]):
        """Add a new decision"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "market_snapshot": {
                "price": market_data.get('ticker', {}).get('lastPrice'),
                "change_24h": market_data.get('ticker', {}).get('priceChangePercent')
            },
            "portfolio_snapshot": {
                "positions": portfolio_state.get('positions', [])
            }
        }
        
        self.decisions.append(entry)
        
        # Keep only last 1000 decisions
        if len(self.decisions) > 1000:
            self.decisions = self.decisions[-1000:]
        
        self._save()
    
    def get_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent decisions"""
        return self.decisions[-limit:]
    
    def get_all_decisions(self) -> List[Dict[str, Any]]:
        """Get all decisions"""
        return self.decisions

