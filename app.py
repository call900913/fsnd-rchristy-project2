import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask import flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Model

from oauth2client import client

from decorators import login_required, initial_categories

import httplib2

app = Flask(__name__)


engine = create_engine('sqlite:///abc.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db = DBSession()


@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def landing():
    if request.method == "POST":
        email = request.form.get("email")
        submitted_password = request.form.get("password")
        user = db.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, submitted_password):
                session['user_id'] = user.id
                return redirect(url_for('displayCategories'))
        else:
            # flash('Try again')
            return redirect(url_for('signUp'))
    else:
        return render_template('login.html')


@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('landing'))


@app.route('/signup', methods=["GET", "POST"])
def signUp():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))
        newUser = User(name=name, email=email, password=password)
        db.add(newUser)
        db.commit()
        user = db.query(User).filter_by(email=email).first()
        session['user_id'] = user.id
        initial_categories(Category, Model, db, session['user_id'])
        return redirect(url_for('displayCategories'))
    else:
        return render_template('signup.html')


@app.route('/categories')
@login_required
def displayCategories():
    user_id = session['user_id']
    cats = db.query(Category).filter_by(user_id=user_id).all()
    return render_template('categories.html', cats=cats)


@app.route('/categories/addnew', methods=["GET", "POST"])
@login_required
def addNewCategory():
    if request.method == "POST":
        name = request.form.get('name')
        user_id = session['user_id']
        newCategory = Category(name=name, user_id=user_id)
        db.add(newCategory)
        db.commit()
        return redirect(url_for('displayCategories'))
    else:
        return render_template('addnewcategory.html')


@app.route('/<int:category_id>/edit', methods=["GET", "POST"])
@login_required
def editCategory(category_id):
    cat = db.query(Category).filter_by(id=category_id).one()
    if request.method == "POST":
        updatedCatName = request.form.get('name')
        cat.name = updatedCatName
        return redirect(url_for('displayCategories'))
    else:
        catName = cat.name
        return render_template(
            'editcategory.html',
            category_id=category_id,
            catName=catName)


@app.route('/<int:category_id>/delete', methods=["GET"])
@login_required
def deleteCategory(category_id):
    db.delete(db.query(Category).filter_by(id=category_id).first())
    db.commit()
    return redirect(url_for('displayCategories'))


@app.route('/<int:category_id>/models', methods=["GET"])
@login_required
def showModels(category_id):
    models = db.query(Model).filter_by(category_id=category_id).all()
    catName = db.query(Category).filter_by(id=category_id).one().name
    return render_template(
        'models.html',
        category_id=category_id,
        catName=catName,
        models=models)


@app.route('/<int:category_id>/models/addnew', methods=["GET", "POST"])
@login_required
def addNewModel(category_id):
    if request.method == "POST":
        name = request.form.get('name')
        user_id = session['user_id']
        description = request.form.get('description')
        newModel = Model(
            name=name, description=description,
            user_id=user_id, category_id=category_id)
        db.add(newModel)
        db.commit()
        return redirect(url_for('showModels', category_id=category_id))
    else:
        return render_template('addnewmodel.html', category_id=category_id)


@app.route('/<int:category_id>/<int:model_id>/delete', methods=["GET"])
@login_required
def deleteModel(model_id, category_id):
    db.delete(db.query(Model).filter_by(id=model_id).first())
    db.commit()
    return redirect(url_for('showModels', category_id=category_id))


@app.route('/<int:category_id>/<int:model_id>/edit', methods=["GET", "POST"])
@login_required
def editModel(model_id, category_id):
    mod = db.query(Model).filter_by(id=model_id).one()
    if request.method == "POST":
        updatedModName = request.form.get('name')
        mod.name = updatedModName
        updatedDesc = request.form.get('description')
        mod.description = updatedDesc
        return redirect(url_for('showModels', category_id=category_id))
    else:
        modName = mod.name
        return render_template(
            'editmodel.html',
            category_id=category_id,
            modName=modName,
            model_id=model_id)


@app.route('/categories/JSON')
def catJSON():
    categories = db.query(Category).filter_by(user_id=0).all()
    return jsonify(cats=[cat.serialize for cat in categories])


@app.route('/goog', methods=["POST"])
def googSignIn():
    if not request.headers.get('X-Requested-With'):
        abort(403)
    CLIENT_SECRET = 'client_secret.json'

    auth_code = request.data

    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        auth_code
    )

    credentials.authorize(httplib2.Http())

    email = credentials.id_token['email']
    user = db.query(User).filter_by(email=email).first()

    if not user:
        name = credentials.id_token['name']
        password = generate_password_hash(credentials.id_token['sub'])
        newUser = User(name=name, email=email, password=password)
        db.add(newUser)
        db.commit()
        newuser = db.query(User).filter_by(email=email).first()
        session['user_id'] = newuser.id
    else:
        session['user_id'] = user.id
    return redirect(url_for('displayCategories'))


@app.route('/fbconnect', methods=["POST"])
def fbSignIn():
    if not request.headers.get('X-Requested-With'):
        abort(403)

    access_token = request.data
    url = 'https://graph.facebook.com/v4.0/me?access_token=%s&fields=id,\
        name,email' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    email = data['email']
    user = db.query(User).filter_by(email=email).first()

    if not user:
        name = data['name']
        password = generate_password_hash(data['id'])
        newUser = User(name=name, email=email, password=password)
        db.add(newUser)
        db.commit()
        newuser = db.query(User).filter_by(email=email).first()
        session['user_id'] = newuser.id
    else:
        session['user_id'] = user.id
    return redirect(url_for('displayCategories'))


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
