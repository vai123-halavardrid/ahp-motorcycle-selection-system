from datetime import datetime
from . import mongo

def insert_alternative(data):
    """Insert a new alternative into the database"""
    try:
        data['created_at'] = datetime.utcnow()
        result = mongo.db.alternatives.insert_one(data)
        return result.inserted_id
    except Exception as e:
        raise Exception(f"MongoDB insert error: {str(e)}")

def insert_criteria_comparison(data):
    """Insert criteria comparison matrix and results"""
    try:
        data['created_at'] = datetime.utcnow()
        result = mongo.db.criteria_comparisons.insert_one(data)
        return result.inserted_id
    except Exception as e:
        raise Exception(f"MongoDB insert error: {str(e)}")

def insert_alternative_comparison(data):
    """Insert alternative comparison matrix for a specific criterion"""
    try:
        data['created_at'] = datetime.utcnow()
        result = mongo.db.alternative_comparisons.insert_one(data)
        return result.inserted_id
    except Exception as e:
        raise Exception(f"MongoDB insert error: {str(e)}")

def insert_final_result(data):
    """Insert final AHP results"""
    try:
        data['created_at'] = datetime.utcnow()
        result = mongo.db.final_results.insert_one(data)
        return result.inserted_id
    except Exception as e:
        raise Exception(f"MongoDB insert error: {str(e)}")

def get_alternatives():
    """Retrieve all alternatives"""
    try:
        return list(mongo.db.alternatives.find())
    except Exception as e:
        raise Exception(f"MongoDB query error: {str(e)}")

def get_criteria_comparison():
    """Retrieve the latest criteria comparison"""
    try:
        return mongo.db.criteria_comparisons.find_one(
            sort=[('created_at', -1)]
        )
    except Exception as e:
        raise Exception(f"MongoDB query error: {str(e)}")

def get_alternative_comparisons():
    """Retrieve all alternative comparisons"""
    try:
        return list(mongo.db.alternative_comparisons.find())
    except Exception as e:
        raise Exception(f"MongoDB query error: {str(e)}")

def get_final_result():
    """Retrieve the latest final result"""
    try:
        return mongo.db.final_results.find_one(
            sort=[('created_at', -1)]
        )
    except Exception as e:
        raise Exception(f"MongoDB query error: {str(e)}")

def clear_session_data():
    """Clear all session data from database"""
    try:
        mongo.db.alternatives.delete_many({})
        mongo.db.criteria_comparisons.delete_many({})
        mongo.db.alternative_comparisons.delete_many({})
        mongo.db.final_results.delete_many({})
    except Exception as e:
        raise Exception(f"MongoDB delete error: {str(e)}")
