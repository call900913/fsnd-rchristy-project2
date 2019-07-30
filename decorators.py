from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    # https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def initial_categories(Category, Model, db, user_id):
    models = {
        'Cars': ['Fiesta', 'Mustang', 'Taurus'],
        'SUVs': ['Escape', 'Edge', 'Explorer'],
        'Trucks': ['Ranger', 'F150', 'Super Duty'],
        'Hybrids': ['Fusion']
    }
    names = ['Cars', 'SUVs', 'Trucks', 'Hybrids']
    for i in range(len(names)):
        cat = Category(name=names[i], user_id=user_id)
        db.add(cat)
        db.commit()
    categories = db.query(Category).filter_by(user_id=user_id).all()
    for category in categories:
        for i in range(len(models[category.name])):
            newModel = Model(
                name=models[category.name][i],
                user_id=user_id,
                category_id=category.id,
                description='')
            db.add(newModel)
            db.commit()
