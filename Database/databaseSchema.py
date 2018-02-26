from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Boolean, Numeric, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    fullName = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'fullName': self.fullName
        }

    def __init__(self, fullName, user_id):
        self.fullName = fullName
        self.user_id = user_id


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=True)
    subtitle = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    idAuthor = Column(Integer, ForeignKey('author.id'))
    description = Column(String(250), nullable=False)
    publishedDate = Column(Integer, nullable=False)
    pages = Column(Integer, nullable=False)
    webReaderLink = Column(VARCHAR(250), nullable=False)
    category = Column(String(250), nullable=False)
    image = Column(VARCHAR(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'author': self.author,
            'idAuthor': self.idAuthor,
            'description': self.description,
            'publishedDate': self.publishedDate,
            'pages': self.pages,
            'webReaderLink': self.webReaderLink,
            'category': self.category,
            'image': self.image
        }

    def __init__(self, title, subtitle, author, idAuthor, description, publishedDate, pages, webReaderLink, category, image, user_id):  # noqa
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.idAuthor = idAuthor
        self.description = description
        self.publishedDate = publishedDate
        self.pages = pages
        self.webReaderLink = webReaderLink
        self.category = category
        self.image = image
        self.user_id = user_id


# uncomment this if you are rerunning the database
# otherwise if just retrieving information leave commented
engine = create_engine('sqlite:///myLibrary.db')
Base.metadata.create_all(engine)
