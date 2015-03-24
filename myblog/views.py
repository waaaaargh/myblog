from myblog import app
from myblog import model
from flask import render_template, redirect

from sqlalchemy.orm.exc import NoResultFound

@app.route('/')
def redirect_to_recent_posts():
    return redirect('/posts/recent/0')

@app.route('/posts/recent/<int:page_number>', defaults={'page_number': 0})
def show_posts(page_number):
    posts_per_page = 5
    posts = model.post.query.\
            order_by(model.post.date).\
            offset(page_number * posts_per_page).\
            limit(posts_per_page).\
            all()
    return render_template('list_posts_lastweek.htmljinja', posts=posts)

@app.route('/posts/<int:post_id>', defaults={'slug': ''})
@app.route('/posts/<int:post_id>/<slug>')
def single_post_view(post_id, slug):
    try:
        post = model.post.query.\
               filter(model.post.id == post_id).\
               limit(1).\
               one()
    except NoResultFound:
        return "Post not found", 404
    return render_template('post_details.htmljinja', post=post)

@app.route('/category/<category_name>')
def show_category_posts(category_name):
    try:
        category = model.category.query.\
                   filter(model.category.name == category_name).\
                   one()
    except NoResultFound:
        return "Category not found", 404

    return render_template('show_category_posts.htmljinja', category=category)
