
from flask_sqlalchemy import SQLAlchemy

class _DBSingleton:
    _instance = None
    db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_DBSingleton, cls).__new__(cls)
            cls._instance.db = SQLAlchemy()
        return cls._instance


def get_db():
    singleton = _DBSingleton()
    return singleton.db
