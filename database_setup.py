import sys
from sqlalchemy import Column, ForeignKey, Integer, String

# this one we'll use n the configuration and class code
from sqlalchemy.ext.declarative import declarative_base

# create foreign key relationships -- used when we write the mapper
from sqlalchemy.orm import relationship

# used in the config code at the end of the file
from sqlalchemy import create_engine

# helps us get setup when we beign to write our class code
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(128), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)

engine = create_engine('sqlite:///abc.db')
Base.metadata.create_all(engine)
