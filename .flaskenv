FLASK_ENV=development
FLASK_APP=MazdoorOnline_API.app:create_app
SECRET_KEY=get_your_own_secret_Key
DATABASE_URI=sqlite:///MazdoorOnline_API.db
JWT_ACCESS_EXPIRE_TIME_IN_MINUTES=43200
JWT_REFRESH_TOKEN_TIME_IN_MINUTES=86400
CLOUDINARY_URL=get_your_own
CELERY_BROKER_URL=amqp://guest:guest@localhost/
CELERY_RESULT_BACKEND_URL=rpc://
