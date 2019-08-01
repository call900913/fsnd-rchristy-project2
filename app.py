""" Run this File to begin the app. """

import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask import flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Model

from decorators import login_required, initial_categories

from oauth2client import client

import httplib2

app = Flask(__name__)


engine = create_engine('sqlite:///abc.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db = DBSession()


@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def landing():
    """ handles the login page """
    if request.method == "POST":
        email = request.form.get("email")
        submitted_password = request.form.get("password")
        email_check = email.replace(' ', '')
        pw_check = submitted_password.replace(' ', '')
        if email_check == '' or pw_check == '':
            flash('Please enter a valid value for \
                the email and password fields.')
            return render_template('login.html')
        user = db.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, submitted_password):
                session['user_id'] = user.id
                return redirect(url_for('displayCategories'))
        else:
            return redirect(url_for('signUp'))
    else:
        return render_template('login.html')


@app.route('/logout', methods=["GET"])
def logout():
    """ log out the user """
    session.clear()
    return redirect(url_for('landing'))


@app.route('/signup', methods=["GET", "POST"])
def signUp():
    """ add a new user into the Database """
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        pw = request.form.get('password')
        pwc = request.form.get('passwordc')
        name_check = name.replace(' ', '')
        email_check = email.replace(' ', '')
        pw_check = pw.replace(' ', '')
        pwc_check = pwc.replace(' ', '')
        if \
          name_check == '' or email_check == '' or \
          pw_check == '' or pwc_check == '':
            flash('Please fill in all the fields.')
            return render_template('signup.html')
        if pw != pwc:
            flash('Please confirm the password by typing the same value \
            in both password fields.')
            return render_template('signup.html')
        password = generate_password_hash(pw)
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
    """ List the category """
    user_id = session['user_id']
    cats = db.query(Category).filter_by(user_id=user_id).all()
    return render_template('categories.html', cats=cats)


@app.route('/categories/addnew', methods=["GET", "POST"])
@login_required
def addNewCategory():
    """ Add a new category (C in CRUD) """
    if request.method == "POST":
        name = request.form.get('name')
        name_check = name.replace(' ', '')
        if name_check == '':
            flash('Please add a name for the category.')
            return render_template('addnewcategory.html')
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
    """ Edit a category (U in CRUD) """
    cat = db.query(Category).filter_by(id=category_id).one()
    if request.method == "POST":
        updatedCatName = request.form.get('name')
        name_check = updatedCatName.replace(' ', '')
        if name_check == '':
            return redirect(url_for('displayCategories'))
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
    """ Delete a category (D in CRUD) """
    db.delete(db.query(Category).filter_by(id=category_id).first())
    db.commit()
    return redirect(url_for('displayCategories'))


@app.route('/<int:category_id>/models', methods=["GET"])
@login_required
def showModels(category_id):
    """ Display the list of models in a category (R in CRUD) """
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
    """ Add a new model in a particular category (C in CRUD) """
    if request.method == "POST":
        name = request.form.get('name')
        user_id = session['user_id']
        description = request.form.get('description')
        name_check = name.replace(' ', '')
        if name_check == '':
            flash('Please add a name for the model.')
            return render_template('addnewmodel.html', category_id=category_id)
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
    """ Delete a model in a category (D in CRUD) """
    db.delete(db.query(Model).filter_by(id=model_id).first())
    db.commit()
    return redirect(url_for('showModels', category_id=category_id))


@app.route('/<int:category_id>/<int:model_id>/edit', methods=["GET", "POST"])
@login_required
def editModel(model_id, category_id):
    """ Edit a model in a category (U in CRUD) """
    mod = db.query(Model).filter_by(id=model_id).one()
    curDesc = mod.description
    if request.method == "POST":
        updatedModName = request.form.get('name')
        name_check = updatedModName.replace(' ', '')
        if name_check == '':
            return redirect(url_for('showModels', category_id=category_id))
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
            model_id=model_id,
            curDesc=curDesc)


#---------JSON API Endpoints---------#
@app.route('/categories/JSON')
def catJSON():
    """ Provide the JSON endpoint """
    categories = db.query(Category).filter_by(user_id=0).all()
    return jsonify(cats=[cat.serialize for cat in categories])


@app.route('/<int:category_id>/models/JSON')
def modJSON(category_id):
    """ JSON Endpoint for models in a category """
    models = db.query(Model).filter_by(category_id=category_id).all()
    return jsonify(mods=[mod.serialize for mod in models])
#---------JSON API Endpoints---------end of section---------#


#---------Oauth logins---------#
@app.route('/goog', methods=["POST"])
def googSignIn():
    """ This is the function to handle Google Sign-In """
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
    """ This is the function to handle Facebook Sign-In """
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
#---------Oauth logins--------end of section---------#

if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


# Addd some comments here.
