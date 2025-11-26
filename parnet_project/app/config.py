
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-parnet")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://usuario:password@localhost:5432/parnet"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
