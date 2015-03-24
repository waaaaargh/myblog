from os.path import join

from myblog import app, model, db, base_path

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

from werkzeug.security import generate_password_hash
import wtforms

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

class UserView(ModelView):
    form_excluded_columns = ['posts', 'passwordhash']
    column_list = ['name']
    
    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = wtforms.PasswordField('New Password')
        return form_class
        
    
    def on_model_change(self, form, model):
        if len(form.password.data) > 0:
            model.passwordhash = generate_password_hash(form.password.data)


admin.add_view(UserView(model.user, db.session))

admin.add_view(FileAdmin(join(base_path, "static"), "/static/"))
