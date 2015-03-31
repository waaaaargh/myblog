from os.path import join

from myblog import app, model, db, base_path

from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext import login

from flask import redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
import wtforms

class LoginAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login'))
        return super(AdminIndexView, self).render('admin/index.html')
        
    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        class LoginForm(wtforms.Form):
            username = wtforms.TextField(validators=[wtforms.validators.Required()])
            password = wtforms.PasswordField(validators=[wtforms.validators.Required()])
        
        form = LoginForm(request.form)
        if request.method == 'POST':
            user = model.user.query.filter(model.user.name == form.username.data).first()
            if user is not None:
                if check_password_hash(user.passwordhash, form.password.data):
                    login.login_user(user)
                    return redirect(url_for('.index'))

        self._template_args['form'] = form
        return self.render('admin/login.html')
        
    @expose('/logout')
    def logout(self):
        login.logout_user()
        return redirect(url_for('.login'))
        

admin = Admin(app, name="MyBlog", index_view=LoginAdminIndexView(name="home"))

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class AuthenticatedFileAdmin(FileAdmin):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class PostView(AuthenticatedModelView):
    form_excluded_columns = ['date', 'comments']
admin.add_view(PostView(model.post, db.session))

class CategoryView(AuthenticatedModelView):
    form_excluded_columns = ['posts']
admin.add_view(CategoryView(model.category, db.session))

class CommentView(AuthenticatedModelView):
    pass
admin.add_view(CommentView(model.comment, db.session))

#class UserView(ModelView):
class UserView(AuthenticatedModelView):
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

admin.add_view(AuthenticatedFileAdmin(join(base_path, "static"), "/static/", name="files"))
