from datetime import datetime, timedelta

from model import post, page

from sqlalchemy.sql.expression import between, desc

"""
only executes the decorated function if performed by an authorized user via beaker session
Throws Exception('NotAuthenticated') if user is not authorized
"""
def authenticated(function):
    def inner(*args, **kwargs):
        # userame checking goes here
        try:
            username_session = args[1]['beaker.session']['username']      
        except KeyError, e:
            raise Exception('NotAuthenticated')

        ret = function(*args, **kwargs)
        
        return ret

    return inner

def list_posts_year(request, environment, session, year):
    upperbound = datetime(year+1, 1, 1)
    lowerbound = datetime(year, 1, 1)
    posts = session.query(post).filter(between(
        post.date, lowerbound, upperbound)).all()
    return {'posts': posts, 'year': year} 

def list_posts_month(request, environment, session, year, month):
    upperbound = datetime(year, month+1, 1)
    lowerbound = datetime(year, month, 1)
    posts = session.query(post).filter(between(post.date, lowerbound, upperbound)).all()
    return {'posts': posts, 'month': month, 'year': year} 

def list_posts_day(request, environment, session, month, year, day):
    upperbound = datetime(year, month, day + 1)
    lowerbound = datetime(year, month, day)
    posts = session.query(post).filter(between(post.date, lowerbound, upperbound)).all()
    return {'posts': posts, 'day': day, 'month': month, 'year': year}

def list_posts_lastweek(request, environment, session):
    upperbound = datetime.now()
    lowerbound = upperbound - timedelta(days=7)
    posts = session.query(post).filter(between(post.date, lowerbound, upperbound)).order_by(desc(post.date)).all()
    return {'posts': posts}

def post_details(request, environment, session, id):
    post_obj = session.query(post).filter(post.id == id).one()
    return {'post': post_obj}

def rss(request, environment, session):
    posts = session.query(post).limit(20)
    return {'posts': posts}

def show_page(request, environment, session, page_id):
    page_obj = session.query(page).filter(page.id == page_id).one()
    return {'page': page}

"""
attempt login and write username into session if successfull

returns
    * success: False if login was not successfull
    * success: True if login was successfull
    * success: None if the login has not been performed yet

errorstring may be:
    * 'InvalidLogin', if username/password combination is unknown
"""
def admin_login(request, environment, session):
    if request.method != 'POST':
        return {'success': None}
    else:
        try:
            username = request.form['username']
            password = request.form['password']
        except KeyError, e:
            raise Exception('BuggyHTML')

        if username == environment['blog.config'].username and password == environment['blog.config'].password:
            http_session = environment['beaker.session']
            http_session['username'] = username
            http_session.save()
            return {'success': True} 
        else: 
            return {'success': False, 'errorstring': 'InvalidLogin'}


def admin_logout(request, environment, session):
    http_session = environment['beaker.session']
    http_session.delete()
    return {'success': True}

"""
Displays a list of all posts
"""
@authenticated
def admin_welcome(request, environment, session):
    posts = session.query(post).all()
    pages = session.query(page).all()
    return {'posts': posts, 'pages': pages}
    raise Exception('nigger')

"""
Creates a post.

returns:
    * success: True if the post has been created successfully
    * success: False and an errorstring if anything has gone
        wrong.
    * success: None, if no action has been performed at all.

errortype may be:
    * 'MissingTitle' if no title has been passed
    * 'MissongContent' if no content has been passed
    * 'BuggyHTML' if something is wrong with the form.
"""
@authenticated
def admin_create_post(request, environment, session):
    if request.method != 'POST':
        return {'success': None}
    else:
        try:
            title = request.form['title'] 
            excerpt = request.form['excerpt'] 
            content = request.form['content']
        except KeyError, e:
            return {'success': False, 'errorstring': 'BuggyHTML'}

        # check if at least title and content are present.
        if title == '':
            return {'success': False, 'errorstring': 'MissingTitle'}
        if content == '':
            return {'success': False, 'errorstring': 'MissingPost'}

        # if we don't have an excerpt, we want the field to be not set at all.
        if excerpt == '':
            excerpt = None

        new = post()
        new.title = title
        new.excerpt = excerpt
        new.content = content

        new.date = datetime.now()        

        session.add(new)
        session.commit()
        
        return {'success': True}

"""
Opens the post <post_id> for editing and saves it.

returns:
    * success: True if the post has been created successfully
    * success: False and an errorstring if anything has gone
        wrong.
    * success: None, if no action has been performed at all.

errortype may be:
    * 'MissingTitle' if no title has been passed
    * 'MissongContent' if no content has been passed
    * 'BuggyHTML' if something is wrong with the form.

may throw:
    * 
"""
@authenticated
def admin_edit_post(request, environment, session, post_id):
        # get post Object
        post_obj = session.query(post).filter(post.id == post_id).one()

        if request.method != 'POST':
            return {'success': None, 'post': post_obj}
        else:
            try:
                title = request.form['title'] 
                excerpt = request.form['excerpt'] 
                content = request.form['content']
            except KeyError, e:
                return {'success': False, 'errorstring': 'BuggyHTML'}

            # check if at least title and content are present.
            if title == '':
                return {'success': False, 'errorstring': 'MissingTitle'}
            if content == '':
                return {'success': False, 'errorstring': 'MissingPost'}

            # if we don't have an excerpt, we want the field to be not set at all.
            if excerpt == '':
                excerpt = None
            
            post_obj.title = title
            post_obj.excerpt = excerpt
            post_obj.content = content

            session.commit()
            
            return {'success': True, 'post': post_obj}

"""
deletes the post with the id <post_id>.

returns:
    * success: True if the post has been deleted successfully
    * success: False and an errorstring if anything has gone
        wrong.
throws:
    * Exception('NoSuchPost') if there is no post with <post_id>

"""
@authenticated
def admin_delete_post(request, environment, session, post_id):
    post_obj = session.query(post).filter(post.id == post_id).one()
    session.delete(post_obj)
    session.commit()
    return {'success': True}

"""
Creates a page.

returns:
    * success: True if the page has been created successfully
    * success: False and an errorstring if anything has gone
        wrong.
    * success: None, if no action has been performed at all.

errortype may be:
    * 'MissingTitle' if no title has been passed
    * 'MissongContent' if no content has been passed
    * 'BuggyHTML' if something is wrong with the form.
"""
@authenticated
def admin_create_page(request, environment, session):
    if request.method != 'POST':
        return {'success': None}
    else:
        try:
            title = request.form['title'] 
            content = request.form['content']
        except KeyError, e:
            return {'success': False, 'errorstring': 'BuggyHTML'}

        # check if at least title and content are present.
        if title == '':
            return {'success': False, 'errorstring': 'MissingTitle'}
        if content == '':
            return {'success': False, 'errorstring': 'MissingPost'}

        new = page()
        new.title = title
        new.content = content

        new.lastmodified = datetime.now()        

        session.add(new)
        session.commit()
        
        return {'success': True}

"""
Opens the page <page_id> for editing and saves it.

returns:
    * success: True if the post has been created successfully
    * success: False and an errorstring if anything has gone
        wrong.
    * success: None, if no action has been performed at all.

errortype may be:
    * 'MissingTitle' if no title has been passed
    * 'MissongContent' if no content has been passed
    * 'BuggyHTML' if something is wrong with the form.

may throw:
    * 
"""
@authenticated
def admin_edit_page(request, environment, session, page_id):
        # get page Object
        page_obj = session.query(page).filter(page.id == page_id).one()

        if request.method != 'POST':
            return {'success': None, 'page': page_obj}
        else:
            try:
                title = request.form['title'] 
                excerpt = request.form['excerpt'] 
                content = request.form['content']
            except KeyError, e:
                return {'success': False, 'errorstring': 'BuggyHTML'}

            # check if at least title and content are present.
            if title == '':
                return {'success': False, 'errorstring': 'MissingTitle'}
            if content == '':
                return {'success': False, 'errorstring': 'MissingContent'}
            
            page_obj.title = title
            page_obj.content = content

            session.commit()
            
            return {'success': True, 'page': page_obj}

"""
deletes the page with the id <page_id>.

returns:
    * success: True if the post has been deleted successfully
    * success: False and an errorstring if anything has gone
        wrong.
throws:
    * Exception('NoSuchPage') if there is no post with <post_id>

"""
@authenticated
def admin_delete_page(request, environment, session, page_id):
    page_obj = session.query(page).filter(page.id == page_id).one()
    session.delete(page_obj)
    session.commit()
    return {'success': True}
