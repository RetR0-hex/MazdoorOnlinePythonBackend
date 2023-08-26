from MazdoorOnline_API.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("MazdoorOnline_API.tasks.example",)
