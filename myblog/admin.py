from os.path import join

from myblog import app, model, db, base_path

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

admin = Admin(app, name="MyBlog")

class PostView(ModelView):
    form_excluded_columns = ['date', 'comments']
admin.add_view(PostView(model.post, db.session))

class CategoryView(ModelView):
    form_excluded_columns = ['posts']
admin.add_view(CategoryView(model.category, db.session))

class CommentView(ModelView):
    pass
admin.add_view(CommentView(model.comment, db.session))

admin.add_view(FileAdmin(join(base_path, "static"), "/static/"))
