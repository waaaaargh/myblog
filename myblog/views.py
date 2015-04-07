from myblog import app, db, model
from flask import render_template, redirect, request

from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime

@app.route('/')
def redirect_to_recent_posts():
    return redirect('/posts/recent/0')

@app.route('/posts/recent/<int:page_number>', defaults={'page_number': 0})
def show_posts(page_number):
    posts_per_page = 5
    posts = model.post.query.\
            order_by(model.post.date.desc()).\
            offset(page_number * posts_per_page).\
            limit(posts_per_page).\
            all()
    return render_template('list_posts_lastweek.htmljinja', posts=posts)

@app.route('/posts/<int:post_id>', defaults={'slug': ''})
def single_post_view(post_id, slug):
    try:
        post = model.post.query.\
               filter(model.post.id == post_id).\
               limit(1).\
               one()
    except NoResultFound:
        return "Post not found", 404
    return render_template('post_details.htmljinja', post=post)

@app.route('/posts/<int:post_id>/comment', methods=['POST', 'GET'])
def add_post_comment(post_id):
    from wtforms import Form, validators, TextField, TextAreaField, BooleanField
    from flask.ext.wtf import RecaptchaField
    class CommentForm(Form):
        name = TextField('Name', [validators.Length(min=4, max=25)])
        email = TextField('E-Mail-Addresse', [validators.Length(min=6, max=35)])
        text = TextAreaField('Dein Kommentar',
                             [validators.Length(min=30, max=1000)])
        captcha = RecaptchaField('Bist Du wirklich ein Mensch, und nicht etwa ein Kohlkopf oder irgendsowas?')
        accept_rules = BooleanField('Ich bin weder ein Nazi noch ein sonstiger Vollidiot', [validators.Required()])
        
    form = CommentForm(request.form)
    post = model.post.query.filter(model.post.id == post_id).first()
    
    if request.method == "POST":
        if form.validate():
            c = model.comment()
            c.post = post
            c.date = datetime.now()
            c.name = form.name.data
            c.email = form.email.data
            c.text = form.text.data
            db.session.add(c)
            db.session.commit()
            return redirect("/posts/%i" % post.id)

    return render_template('post_comment.htmljinja', form=form, post=post)
    

@app.route('/category/<category_name>')
def show_category_posts(category_name):
    try:
        category = model.category.query.\
                   filter(model.category.name == category_name).\
                   one()
    except NoResultFound:
        return "Category not found", 404

    return render_template('show_category_posts.htmljinja', category=category)
