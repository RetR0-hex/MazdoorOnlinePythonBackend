"""Default configuration

Use env var to override
"""
import os
import datetime

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=float(os.getenv("JWT_ACCESS_EXPIRE_TIME_IN_MINUTES")))
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(minutes=float(os.getenv("JWT_REFRESH_TOKEN_TIME_IN_MINUTES")))
SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY = {
    "broker_url": os.getenv("CELERY_BROKER_URL"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND_URL"),
}
