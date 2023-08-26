import click
from flask.cli import with_appcontext


@click.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from MazdoorOnline_API.extensions import db
    from MazdoorOnline_API.models import User, Category

    click.echo("create user")
    user = User(full_name="admin", email="admin@mail.com", phone_number="+000000000000", password="admin", role=0, active=True)
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")
    click.echo("populating categories")
    categories_detail = [{"name": "Plumber", "rate": 450},
                         {"name": "Carpenter", "rate": 600},
                         {"name": "Electrician", "rate": 300},
                         {"name": "Mechanic", "rate": 400},
                         {"name": "Masonry", "rate": 300},
                         {"name": "Painter", "rate": 300},
                         {"name": "Interior Designer", "rate": 800},
                         {"name": "Welder", "rate": 700},
                         ]

    for cat_detail in categories_detail:
        category = Category(name=cat_detail["name"], base_rate_per_hour=cat_detail["rate"], base_rate_per_km=15)
        db.session.add(category)

    db.session.commit()
    click.echo("categories created")
