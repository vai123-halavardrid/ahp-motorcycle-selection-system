from datetime import datetime

class MemoryStorage:
    def __init__(self):
        self.alternatives = []
        self.criteria_comparisons = []
        self.alternative_comparisons = []
        self.final_results = []

    def insert_alternative(self, data):
        """Insert a new alternative"""
        data['created_at'] = datetime.utcnow()
        self.alternatives.append(data)
        return len(self.alternatives) - 1  # Return ID

    def insert_criteria_comparison(self, data):
        """Insert criteria comparison matrix and results"""
        data['created_at'] = datetime.utcnow()
        self.criteria_comparisons.append(data)
        return len(self.criteria_comparisons) - 1

    def insert_alternative_comparison(self, data):
        """Insert alternative comparison matrix for a specific criterion"""
        data['created_at'] = datetime.utcnow()
        self.alternative_comparisons.append(data)
        return len(self.alternative_comparisons) - 1

    def insert_final_result(self, data):
        """Insert final AHP results"""
        data['created_at'] = datetime.utcnow()
        self.final_results.append(data)
        return len(self.final_results) - 1

    def get_alternatives(self):
        """Retrieve all alternatives"""
        return self.alternatives

    def get_criteria_comparison(self):
        """Retrieve the latest criteria comparison"""
        if not self.criteria_comparisons:
            return None
        return self.criteria_comparisons[-1]

    def get_alternative_comparisons(self):
        """Retrieve all alternative comparisons"""
        return self.alternative_comparisons

    def get_final_result(self):
        """Retrieve the latest final result"""
        if not self.final_results:
            return None
        return self.final_results[-1]

    def clear_session_data(self):
        """Clear all session data"""
        self.alternatives = []
        self.criteria_comparisons = []
        self.alternative_comparisons = []
        self.final_results = []

# Create a global instance
storage = MemoryStorage()
