# Project: Book Catalog

This project is for the Nanodegree Full Stack Development. For my project I created a RESTful web application using the Python framework Flask that features a third-party OAuth authentication login system. This application provides a list of authors as categories. Each category or author contains a book or a series of books written by that author. CRUD operations allow the user to create, read, update, and delete books and authors.

**Install Prerequisites**

1. Python 2.7
2. vagrant
3. flask
4. sqlalchemy
5. Oauth 2.0

**Resources Used** 

1. https://developers.google.com/books/ - a key is required to access their API

**Running Code**
1. Clone the project from (https://github.com/mm101006/Library)

2. Open up a terminal, navigate to the folder where the Vagrantfile resides, and in terminal type in: vagrant up

3. Then type in: vagrant ssh

4. Then type in: cd /vagrant

5. Then type in: cd ItemCatalog

6. Then type in: python BookCatalog.py

7. In a browser type in http://localhost:5000/login

**Site Navigation**

1. http://localhost:5000/login -- user is able to login in from here
2. http://localhost:5000/index -- user can view all authors within database
3. http://localhost:5000/index/<int:author_id>/books/ -- user can view all books by that author
4. http://localhost:5000/index/books -- user can view all books within database
5. http://localhost:5000/index/<int:author_id>/books/<int:book_id>/ -- user can view a particular book
6. http://localhost:5000/index/<int:author_id>/books/edit/<int:book_id>/ -- user can edit that book
7. http://localhost:5000/index/user/books -- user can view all of their books
8. http://localhost:5000/index/user/authors -- user can view all of their authors
9. http://localhost:5000/index -- if user is not logged in, user can still view all authors and books within database 

**Other**
If you decide to delete the database and want to create a new database:
1. In the database folder, comment line 14 in books.py
2. Same folder, uncomment lines 88 and 89 in databaseSchema.py
3. in your vagrant terminal (see instructions above to get it started) navigate to the Database folder
4. Then type in: books.py
5. Once done running, undo what you did for step 1 and 2. 
