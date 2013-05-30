from datetime import datetime
from sqlalchemy.sql.expression import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

import re

from util import render_template
from model import post, page, comment, category
from wtforms import Form, TextField, TextAreaField, BooleanField, validators

import util

def authenticated(function):
    """
    only executes the decorated function if performed by an authorized user
    via beaker session.
    Throws Exception('NotAuthenticated') if user is not authorized
    """
    def inner(*args, **kwargs):
        # userame checking goes here
        try:
            username_session = args[1]['beaker.session']['username']
            ret = function(*args, **kwargs)
            return ret
        except KeyError:
            return redirect('/admin/login')
    return inner


def strip_html(string):
    return re.sub('<[^<]+?>', '', string)


def list_last_posts(request, environment, session, page=0):
    posts_per_page = environment['blog.config'].posts_per_page

    posts = session.query(post).order_by(desc(post.date)).offset(page * posts_per_page).limit(posts_per_page).all()
    if len(posts) == 0:
        older, newer = (0, 0)
    else:
        older = session.query(post).filter(post.date < posts[-1].date).count()
        newer = session.query(post).filter(post.date > posts[0].date).count()

    return render_template("list_posts_lastweek.htmljinja", environment,
                           page=page, posts=posts, older=older, newer=newer)


def post_details(request, environment, session, id):
    post_obj = session.query(post).filter(post.id == id).one()
    return render_template("post_details.htmljinja", environment,
                           post=post_obj)


def show_category_list(request, environment, session):
    categories = session.query(category).all()
    return render_template("categories_list.htmljinja",
                           environment, categories=categories)


def show_category_posts(request, environment, session, category_name):
    try:
        c = session.query(category).\
            filter(category.name == category_name).one()
    except NoResultFound:
        raise Exception('Es gibt keine Kategorie mit diesem Namen')

    return render_template("show_category_posts.htmljinja", environment,
                           posts=c.posts, category_name=c.name)


def rss(request, environment, session):
    posts = session.query(post).limit(20)
    return render_template("rss.htmljinja", environment,
                           mimetype='application/rss+xml', posts=posts)


def show_page(request, environment, session, page_id):
    page_obj = session.query(page).filter(page.id == page_id).one()
    return render_template("show_page.htmljinja", environment, page=page_obj)


def add_comment(request , environment, session, post_id):
    from wtfrecaptcha.fields import RecaptchaField

    class CommentForm(Form):
        name = TextField('Name', [validators.Length(min=4, max=25)])
        email = TextField('E-Mail-Addresse',
                          [validators.Length(min=6, max=35)])
        text = TextAreaField('Dein Kommentar',
                             [validators.Length(min=30, max=1000)])
        captcha = RecaptchaField('Bist Du wirklich ein Mensch, und nicht etwa\
                                 ein Kohlkopf oder irgendsowas?',
                                 public_key='6LfNEd8SAAAAAGXTp2hHAm5qVsLBQ5N3\
                                        TyisQivr',
                                 private_key='6LfNEd8SAAAAAAIG55vs01zxnSnFsSg\
                                         EAGtiOMF-',
                                 secure=True)
        accept_rules = BooleanField('Ich bin weder ein Nazi noch ein\
                                    sonstiger Vollidiot',
                                    [validators.Required()])

    post_obj = session.query(post).filter(post.id == post_id).one()

    if request.method == 'POST':
        form = CommentForm(request.form,
                           captcha={'ip_address': request.remote_addr})
        if form.validate():
            c = comment()
            c.name = strip_html(form.name.data)
            c.email = strip_html(form.email.data)
            c.text = strip_html(form.text.data)
            c.date = datetime.now()
            post_obj.comments.append(c)
            session.commit()
        else:
            return render_template("post_comment.htmljinja", environment,
                                   post=post_obj, form=form)
        return redirect('/posts/post_' + str(post_id))
    else:
        form = CommentForm(captcha={'ip_address': request.remote_addr})
        return render_template("post_comment.htmljinja", environment,
                               post=post_obj, form=form)


def admin_login(request, environment, session):
    """
    attempt login and write username into session if successfull
    """
    if request.method != 'POST':
        return render_template("admin_login.htmljinja", environment,
                               success=None)
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
            return render_template("admin_login.htmljinja", environment,
                                   success=False,errorstring='InvalidLogin')


def admin_logout(request, environment, session):
    http_session = environment['beaker.session']
    http_session.delete()
    return {'success': True}


@authenticated
def admin_welcome(request, environment, session):
    """
    Displays a list of all posts
    """
    posts = session.query(post).order_by(desc(post.date)).all()
    pages = session.query(page).all()
    categories = session.query(category).all()

    return render_template("admin_welcome.htmljinja", environment,
                           posts=posts, pages=pages,
                           categories=categories)


@authenticated
def admin_create_post(request, environment, session):
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
    class CreatePostForm(Form):
        title = TextField("Post Title", [validators.required()])
        excerpt = TextField("Post Excerpt", [])
        content = TextAreaField("Post Content", [validators.required()])

    if request.method != 'POST':
        categories = session.query(category).all()
        util.add_categories_to_form(CreatePostForm, categories)
        form = CreatePostForm()
        return render_template("admin_create_post.htmljinja",
                               environment, form=form)
    else:
        categories = session.query(category).all()
        util.add_categories_to_form(CreatePostForm, categories)
        form = CreatePostForm(request.form)
        if form.validate():
            new = post()
            new.title = form.title.data
            if form.excerpt.data != "":
                new.excerpt = form.excerpt.data
            new.content = form.content.data
            new.date = datetime.now()

            # aggregate categories
            for f in form:
                if f.short_name.startswith('cat_'):
                    category_id = int(f.short_name.split('_')[1])
                    category_obj = session.query(category).filter(category.id == category_id).one()
                    new.categories.append(category_obj)

            session.add(new)
            session.commit()
            return redirect("/admin")
        else:
            return render_template("admin_create_post.htmljinja", environment, form=form)


@authenticated
def admin_edit_post(request, environment, session, post_id):
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

        class EditPostForm(Form):
            title = TextField("Post Title", [validators.required()])
            excerpt = TextField("Post Excerpt", [])
            content = TextAreaField("Post Content", [validators.required()])


        # get post Object
        post_obj = session.query(post).filter(post.id == post_id).one()

        if request.method != 'POST':
            categories = session.query(category).all()
            util.add_categories_to_form(EditPostForm, categories)
            form = EditPostForm()
            form.title.data = post_obj.title
            form.excerpt.data = post_obj.excerpt
            form.content.data = post_obj.content
            for c in post_obj.categories:
                getattr(form, "cat_%i" % c.id).data = True
            return render_template("admin_edit_post.htmljinja", environment,
                                   success=None, form=form)
        else:
            categories = session.query(category).all()
            util.add_categories_to_form(EditPostForm, categories)
            form = EditPostForm(request.form)

            if form.validate():
                # reset categories
                for field in form:
                    if field.short_name.startswith('cat'):
                        cat_id = int(field.short_name.split('_')[1])
                        cat_obj = session.query(category).filter(category.id == cat_id).one()
                        if field.data is True and cat_obj not in post_obj.categories:
                            post_obj.categories.append(cat_obj)
                        if field.data is False and cat_obj in post_obj.categories:
                            post_obj.categories.remove(cat_obj)

                post_obj.title = form.title.data
                post_obj.excerpt = form.excerpt.data
                post_obj.content = form.content.data

                session.commit()
                return redirect("/admin")


@authenticated
def admin_delete_post(request, environment, session, post_id):
    """
    deletes the post with the id <post_id>.

    returns:
    * success: True if the post has been deleted successfully
    * success: False and an errorstring if anything has gone
        wrong.
    throws:
    * Exception('NoSuchPost') if there is no post with <post_id>

    """
    post_obj = session.query(post).filter(post.id == post_id).one()
    session.delete(post_obj)
    session.commit()
    return redirect("/admin")

@authenticated
def admin_create_page(request, environment, session):
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

@authenticated
def admin_edit_page(request, environment, session, page_id):
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

@authenticated
def admin_delete_page(request, environment, session, page_id):
    """
    deletes the page with the id <page_id>.

    returns:
        * success: True if the post has been deleted successfully
        * success: False and an errorstring if anything has gone
            wrong.
    throws:
        * Exception('NoSuchPage') if there is no post with <post_id>

    """
    page_obj = session.query(page).filter(page.id == page_id).one()
    session.delete(page_obj)
    session.commit()
    return redirect("/admin")


@authenticated
def admin_create_category(request, environment, session):
    """
    creates a category
    """

    class AddCategoryForm(Form):
        name = TextField("category name", [validators.required()])

    if request.method == "POST":
        form = AddCategoryForm(request.form)
        if not form.validate():
            return render_template("admin_create_category.htmljinja",
                                   environment, form=form)
        else:
            c = category(form.name.data)
            try:
                session.add(c)
                session.commit()
                return redirect('/admin')
            except IntegrityError:
                form.name.data = ""
                form.name.errors.append("This category already exists!")
                return render_template("admin_create_category.htmljinja",
                                       environment, form=form)
    else:
        form = AddCategoryForm()
        return render_template("admin_create_category.htmljinja", environment,
                               form=form)


@authenticated
def admin_delete_category(request, environment, session, category_id):
    try:
        c = session.query(category).filter(category.id == category_id).one()
        #TODO remove deleted category from all posts
        session.delete(c)
        session.commit()
    except NoResultFound:
        pass
    return redirect('/admin')


@authenticated
def admin_delete_comment(request, environment, session, comment_id):
    try:
        comment_obj = session.query(comment).filter(comment.id == comment_id).one()
        session.delete(comment_obj)
        session.commit()
        return redirect('/admin')
    except NoResultFound:
        pass
