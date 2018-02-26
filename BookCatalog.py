from flask import Flask, render_template, session, request, url_for
from flask import redirect, jsonify, flash, make_response

from sqlalchemy import asc

from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import sys
import random
import string
import json
import httplib2
import requests
import bleach

sys.path.append("/vagrant/catalog/Database")

from databaseSchema import Base, Book, Author, User  # noqa

from books import engine, DBSession, session  # noqa
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalog"


@app.route('/')
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token))  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the
        server token exchange we have to split the token
        first on commas and select the first index
        which gives us the key : value for the server access token
        then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it
        can be used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0' % token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;
                    border-radius: 150px;
                    -webkit-border-radius: 150px;
                    -moz-border-radius: 150px;"> '''

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
           % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    console.log(request.args.get('state'));
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    if login_session['username'] == '':
        login_session['username'] = data['email']
    # See if a user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1><span>Welcome: </br>'
    output += login_session['username']
    output += '!</h1></span>'
    flash("Welcome, %s" % login_session['username'])
    return output

# ------------------------Create User ------------


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token user.',
                                            400))
        response.headers['Content-Type'] = 'application/json'
    return response

# -------------------- Show Section -----------------------


@app.route('/index/')
def showAuthors():
    authors = session.query(Author)
    listAuthorId = []
    for author in authors:
        listAuthorId.append(author.id)
    if 'username' not in login_session:
        flash("Sign in to add Authors and Books")
        return render_template('publicindex.html', authors=authors)
    else:
        return render_template('index.html', authors=authors)


@app.route('/index/json')
def showAuthorsJSON():
    authors = session.query(Author)
    return jsonify(Authors=[i.serialize for i in authors])


@app.route('/index/<int:author_id>/books/<int:book_id>/')
def showBook(author_id, book_id):
    books = session.query(Book).filter_by(id=book_id).all()
    author = session.query(Author).filter_by(id=author_id).one()
    return render_template('book.html', books=books, author=author)


@app.route('/index/<int:author_id>/books/<int:book_id>/json')
def showBookJSON(author_id, book_id):
    books = session.query(Book).filter_by(id=book_id).all()
    author = session.query(Author).filter_by(id=author_id).one()
    return jsonify(Books=[i.serialize for i in books])


@app.route('/index/<int:author_id>/')
@app.route('/index/<int:author_id>/books/')
def showBooks(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    books = session.query(Book).filter_by(idAuthor=author_id).all()
    return render_template('AuthorsBooks.html', author=author, books=books)


@app.route('/index/<int:author_id>/books/json/')
def showBooksJSON(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    books = session.query(Book).filter_by(idAuthor=author_id).all()
    return jsonify(books=[i.serialize for i in books])


@app.route('/index/books/')
def showAllBooks():
    authors = session.query(Author)
    books = session.query(Book)
    return render_template('books.html', books=books, authors=authors)


@app.route('/index/books/json')
def showAllBooksJSON():
    books = session.query(Book)
    return jsonify(books=[i.serialize for i in books])


#  ------------------------- Add section -----------------------
# Add Author


@app.route('/index/addAuthor/', methods=['GET', 'POST'])
def newAuthor():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        fullName = request.form['fullName']
        newAuthor = Author(fullName=bleach.clean(fullName),
                           user_id=login_session['user_id'])
        session.add(newAuthor)
        session.commit()
        return redirect(request.referrer)
    else:
        return render_template('newAuthor.html')

# Add book


@app.route('/index/<int:author_id>/books/new/', methods=['GET', 'POST'])
def newBook(author_id):
    if 'username' not in login_session:
        return redirect('/login')
    author = session.query(Author).filter_by(id=author_id).one()
    user = login_session['user_id']
    if request.method == 'POST':
        newBook = Book(title=bleach.clean(request.form['title']),
                       subtitle=bleach.clean(request.form['subtitle']),
                       author=request.form['author'],  idAuthor=author_id,
                       description=bleach.clean(request.form['description']),
                       publishedDate=bleach.clean(request.form['publishedDate']),  # noqa
                       pages=bleach.clean(request.form['pages']),
                       webReaderLink=bleach.clean(request.form['webReaderLink']),  # noqa
                       category=bleach.clean(request.form['category']),
                       image=bleach.linkify(request.form['image']),
                       user_id=user)
        session.add(newBook)
        session.commit()
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template('addBook.html', author_id=author_id)

# ------------------------ Delete Section -----------------------------

# Delete Author


@app.route('/index/<int:author_id>/delete', methods=['GET', 'POST'])
def deleteAuthor(author_id):
    if 'username' not in login_session:
        return redirect('/login')
    authorToDelete = session.query(Author).filter_by(id=author_id).one()
    booksToDelete = session.query(Book).filter_by(idAuthor=author_id).all()
    if authorToDelete.user_id != login_session['user_id']:
        flash('User not authorized to delete author.')
        return redirect(url_for('showAuthors'))
    if request.method == 'POST':
        for book in booksToDelete:
            session.delete(book)
        session.delete(authorToDelete)
        session.commit()
        flash("Author successfully deleted.")
        return redirect(request.referrer)
    else:
        return render_template('deleteAuthor.html', author_id=author_id)

# Delete Book


@app.route('/index/<int:author_id>/books/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(author_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    author = session.query(Author).filter_by(id=author_id).one()
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    if bookToDelete.user_id != login_session['user_id']:
        flash('User not authorized to delete book.')
        return redirect(url_for('showBooks', author_id=author.id))
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book Successfully deleted')
        return redirect(url_for('showBooks',
                                author_id=author_id))
    else:
        flash('Book not deleted')
        return redirect(url_for('showBooks'))

# ---------------------- Edit Section ---------------------------------

# Edit Author


@app.route('/index/edit', methods=['GET', 'POST'])
def editAuthor():
    if 'username' not in login_session:
        return redirect('/login')
    author_id = request.form['id']
    author = session.query(Author).filter_by(id=author_id).one()
    books = session.query(Book).filter_by(idAuthor=author_id).all()
    if author.user_id != login_session['user_id']:
        flash('User not authorized to edit author.')
        return redirect(url_for('showAuthors'))
    if request.method == 'POST':
        for book in books:
            book.author = bleach.clean(request.form['authorName'])
        author.fullName = bleach.clean(request.form['authorName'])
        session.commit()
        flash("Author successfully Edited.")
        return redirect(request.referrer)
    else:
        return render_template('index.html', author=author)

# Edit Book


@app.route('/index/<int:author_id>/books/edit/<int:book_id>',
           methods=['GET', 'POST'])
def editBook(author_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedAuthor = session.query(Author).filter_by(id=author_id).one()
    editedBook = session.query(Book).filter_by(id=book_id).one()
    if editedBook.user_id != login_session['user_id']:
        flash('User not authorized to edit book.')
        return redirect(url_for('showBooks', author_id=author_id))
    if request.method == 'POST':
        if request.form['title']:
            editedBook.title = bleach.clean(request.form['title'])
        if request.form['subtitle']:
            editedBook.subtitle = bleach.clean(request.form['subtitle'])
        if request.form['author']:
            editedBook.author = request.form['author']
        if request.form['description']:
            editedBook.description = bleach.clean(request.form['description'])
        if request.form['publishedDate']:
            editedBook.publishedDate = bleach.clean(request.form['publishedDate'])  # noqa
        if request.form['pages']:
            editedBook.pages = request.form['pages']
        if request.form['webReaderLink']:
            editedBook.webReaderLink = bleach.clean(request.form['webReaderLink'])  # noqa
        if request.form['category']:
            editedBook.category = bleach.clean(request.form['category'])
        if request.form['image']:
            editedBook.image = bleach.linkify(request.form['image'])

        session.add(editedBook)
        session.commit()
        flash('Book successfully edited')
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template('editBook.html',
                               author_id=editedAuthor,
                               book_id=editedBook)

# ---------------------- User Section -------------------------


@app.route('/index/user/authors', methods=['GET', 'POST'])
def showAuthorsUser():
    if 'username' not in login_session:
        return redirect('/login')
    authors = session.query(Author).\
        filter_by(user_id=login_session['user_id']).all()
    listAuthorId = []
    listfullName = []
    for author in authors:
        listAuthorId.append(author.id)
        listfullName.append(author.fullName)
    if 'username' not in login_session:
        flash("Sign in to add Authors and Books")
        return render_template('publicindex.html',
                               authors=authors,
                               listAuthorId=listAuthorId,
                               listfullName=listfullName)
    else:
        return render_template('userindex.html',
                               authors=authors,
                               listAuthorId=listAuthorId,
                               listfullName=listfullName)


@app.route('/index/user/books')
def showAllUserBooks():
    if 'username' not in login_session:
        return redirect('/login')
    authors = session.query(Author)
    books = session.query(Book).\
        filter_by(user_id=login_session['user_id']).all()
    return render_template('userbooks.html',
                           books=books,
                           authors=authors)


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            # del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect('/login')
    else:
        flash("You were not logged in")
        return redirect('/login')

if __name__ == '__main__':
    app.secret_key = 'xDPsCmDxzUDAGAyNlstTHtH5'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
