from myblog import login_manager
from model import user

@login_manager.user_loader
def get_user(user_id):
    return user.query.filter(user.id == user_id).first()
