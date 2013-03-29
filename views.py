from datetime import datetime, timedelta
from sqlalchemy.sql.expression import between, desc
from werkzeug.utils import redirect 

from util import render_template, render_form
from model import post, page, comment
import forms



def authenticated(function):
    """
    only executes the decorated function if performed by an authorized user via beaker session
    Throws Exception('NotAuthenticated') if user is not authorized
    """
    def inner(*args, **kwargs):
        # userame checking goes here
        try:
            username_session = args[1]['beaker.session']['username']      
            ret = function(*args, **kwargs)
            return ret
        except KeyError, e:
            return redirect('/admin/login')
    return inner

def list_last_posts(request, environment, session, page=0):
    posts_per_page = environment['blog.config'].posts_per_page
    
    posts = session.query(post).order_by(desc(post.date)).offset(page*posts_per_page).limit(posts_per_page).all()
    older = session.query(post).filter(post.date < posts[len(posts)-1].date).count()
    newer = session.query(post).filter(post.date > posts[0].date).count()

    return render_template("list_posts_lastweek.htmljinja", environment, page=page, posts=posts, older=older, newer=newer)


def post_details(request, environment, session, id):
    post_obj = session.query(post).filter(post.id == id).one()
    return render_template("post_details.htmljinja", environment, post=post_obj)

def rss(request, environment, session):
    posts = session.query(post).limit(20)
    return render_template("rss.htmljinja", environment, mimetype='application/rss+xml', posts=posts)

def show_page(request, environment, session, page_id):
    page_obj = session.query(page).filter(page.id == page_id).one()
    return render_template("show_page.htmljinja", environment, page=page_obj)

def add_comment(request , environment, session, post_id):
    post_obj = session.query(post).filter(post.id == post_id).one()
    if request.method == 'POST':
        form = forms.CommentForm(request.form, captcha={'ip_address': request.remote_addr})
        if form.validate():
            c = comment()
            c.name = form.name.data
            c.email = form.email.data
            c.text = form.text.data
            c.date = datetime.now()
            post_obj.comments.append(c)
            session.commit()
        else:
            return render_template("post_comment.htmljinja", environment, post=post_obj, form=form)
        return redirect('/posts/post_'+str(post_id))
    else:
        form = forms.CommentForm(captcha={'ip_address': request.remote_addr})
        return render_template("post_comment.htmljinja", environment, post=post_obj, form=form)

def admin_login(request, environment, session):
    """
    attempt login and write username into session if successfull
    """
    if request.method != 'POST':
        return render_template("admin_login.htmljinja", environment, success=None) 
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
            return redirect("/admin")
        else:
            return render_template("admin_login.htmljinja", environment, success=False,errorstring='InvalidLogin') 


def admin_logout(request, environment, session):
    http_session = environment['beaker.session']
    http_session.delete()
    return {'success': True}

"""
Displays a list of all posts
"""
@authenticated
def admin_welcome(request, environment, session):
    posts = session.query(post).order_by(desc(post.date)).all()
    pages = session.query(page).all()
    return render_template("admin_welcome.htmljinja", environment, posts=posts, pages=pages) 
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
        return render_template("admin_create_post.htmljinja", environment, success=None)
    else:
        try:
            title = request.form['title'] 
            excerpt = request.form['excerpt'] 
            content = request.form['content']
        except KeyError, e:
            raise Exception('BuggyHTML')
        # check if at least title and content are present.
        if title == '':
            return render_template("admin_create_post.htmljinja", environment, success=False, errorstring='MissingTitle')
        if content == '':
            return render_template("admin_create_post.htmljinja", environment, success=False, errorstring='MissingPost')

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
        return redirect("/admin") 

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
            return render_template("admin_edit_post.htmljinja", environment, success=None, post=post_obj)
        else:
            try:
                title = request.form['title'] 
                excerpt = request.form['excerpt'] 
                content = request.form['content']
            except KeyError, e:
                raise Exception('BuggyHTML')
            # check if at least title and content are present.
            if title == '':
                return render_template("admin_edit_post.htmljinja", environment, success=False, errorstring='MissingHTML')
            if content == '':
                return render_template("admin_edit_post.htmljinja", environment, success=False, errorstring='MissingTitle')

            # if we don't have an excerpt, we want the field to be not set at all.
            if excerpt == '':
                excerpt = None
            
            post_obj.title = title
            post_obj.excerpt = excerpt
            post_obj.content = content

            session.commit()
            return redirect("/admin")

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
    return redirect("/admin")
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
        return render_template("admin_create_page.htmljinja", environment, success=None)
    else:
        try:
            title = request.form['title'] 
            content = request.form['content']
        except KeyError, e:
            raise Exception('BuggyHTML')

        # check if at least title and content are present.
        if title == '':
            return render_template("admin_create_page.htmljinja", environment, 
                success=False,
                errorstring='MissingTitle'
            )
        if content == '':
            return render_template("admin_create_page.htmljinja", environment, 
                success=False,
                errorstring='MissingContent'
        )

        new = page()
        new.title = title
        new.content = content

        new.lastmodified = datetime.now()        

        session.add(new)
        session.commit()
        
        return redirect('/admin')
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
            return render_template("admin_edit_page.htmljinja", environment, success=None, page=page_obj)
        else:
            try:
                title = request.form['title'] 
                content = request.form['content']
            except KeyError, e:
                raise Exception('BuggyHTML')

            # check if at least title and content are present.
            if title == '':
                return render_template("admin_edit_page.htmljinja", environment,
                    success=False,
                    errorstring='MissingTitle',
                    page=page_obj
                )
            if content == '':
                return render_template("admin_edit_page.htmljinja", environment,
                    success=False,
                    errorstring='MissingContent',
                    page=page_obj
                )
            page_obj.title = title
            page_obj.content = content

            session.commit()
            return redirect("/admin")

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
    return redirect("/admin")
