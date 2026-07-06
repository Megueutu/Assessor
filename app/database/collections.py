from app.core.database import mongo_conn

class Collections:
    SESSIONS = mongo_conn.get_collection("sessions")
    USERS = mongo_conn.get_collection("users")