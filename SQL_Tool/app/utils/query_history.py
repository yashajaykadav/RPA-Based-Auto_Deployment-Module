import os
import pickle
from datetime import datetime

class QueryHistoryManager:
    HISTORY_FILE = "query_history.pkl"
    MAX_HISTORY_ENTRIES = 50

    def __init__(self):
        self.query_history = []
        self.load_history()

    def add_query(self, query):
        """Add query to history"""
        self.query_history.append((datetime.now(), query))
        if len(self.query_history) > self.MAX_HISTORY_ENTRIES:
            self.query_history.pop(0)
        self.save_history()

    def load_history(self):
        """Load query history from file"""
        # History loading logic from original
        pass

    def save_history(self):
        """Save query history to file"""
        # History saving logic from original
        pass

    def get_history(self):
        """Get query history"""
        return self.query_history
