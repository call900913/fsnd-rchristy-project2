from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Model

engine = create_engine('sqlite:///abc.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Hello", email="hello@there.com", password="abcdf", id=0)
session.add(User1)
session.commit()

user_id = session.query(User).filter_by(email="hello@there.com").one().id

models = {
    'Cars': ['Fiesta', 'Mustang', 'Taurus'],
    'SUVs': ['Escape', 'Edge', 'Explorer'],
    'Trucks': ['Ranger', 'F150', 'Super Duty'],
    'Hybrids': ['Fusion']
}

names = list(models.keys())

for i in range(len(names)):
    cat = Category(name=names[i], user_id=user_id)
    session.add(cat)
    session.commit()
    category_id = session.query(Category).filter_by(name=names[i]).one().id
    for j in range(len(models[names[i]])):
        newModel = Model(
            name=models[names[i]][j],
            user_id=user_id,
            category_id=category_id,
            description='')
        session.add(newModel)
        session.commit()
