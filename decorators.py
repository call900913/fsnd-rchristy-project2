"""
In this Module are helper functions to aid the rest of the app,
    including the @login_required decorator which
    checks whether the user is logged in before entering a certain page.
"""

from functools import wraps
from flask import redirect, session


def login_required(f):
    """
    Wrapper function for @login_required in app.py
    Code is taken from:
    https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def initial_categories(Category, Model, db, user_id):
    """ loads stock categories for the new user """
    models = {
        'Cars': ['Fiesta', 'Mustang', 'Taurus'],
        'SUVs': ['Escape', 'Edge', 'Explorer'],
        'Trucks': ['Ranger', 'F150', 'Super Duty'],
        'Hybrids': ['Fusion']
    }
    names = ['Cars', 'SUVs', 'Trucks', 'Hybrids']
    for name in names:
        cat = Category(name=name, user_id=user_id)
        db.add(cat)
        db.commit()
    categories = db.query(Category).filter_by(user_id=user_id).all()
    for category in categories:
        for name in models[category.name]:
            newModel = Model(
                name=name,
                user_id=user_id,
                category_id=category.id,
                description='')
            db.add(newModel)
            db.commit()
