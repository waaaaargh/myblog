from datetime import datetime, timedelta

from model import post

from sqlalchemy.sql.expression import between

def list_posts_year(request, environment, session, year):
    upperbound = datetime(year+1, 1, 1)
    lowerbound = datetime(year, 1, 1)
    posts = session.query(post).filter(between(post.date, lowerbound, upperbound)).all()
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
    posts = session.query(post).filter(between(post.date, lowerbound, upperbound)).all()
    return {'posts': posts}

def post_details(request, environment, session, id):
    post_obj = session.query(post).filter(post.id == id).one()
    return {'post': post_obj}

def admin_welcome(request, environment, session):
    return {}


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
