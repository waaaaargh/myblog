#!/usr/bin/python2

import os

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import sessionmaker
from beaker.middleware import SessionMiddleware

from config import Configuration
import views
import model

class Blog(object):
    """
    set up blog instance.
    """
    def __init__(self, config_path):
        # set locales to german
        import locale
        locale.setlocale(locale.LC_TIME, 'de_DE.utf-8')

        # load config
        self.config = Configuration()
        self.config.load_from_file(config_path)

        # initialize sqlalchemy
        from sqlalchemy import create_engine
        self.engine = create_engine(self.config.database_uri)
        self.session_factory = sessionmaker(bind=self.engine)

        # initialize jinja templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        )
        
        # rules for URLs
        self.url_map = Map([
            Rule('/', endpoint='list_last_posts'),
            Rule('/prev/<int:page>', endpoint='list_last_posts'),
            Rule('/page/<int:page_id>', endpoint='show_page'),
            Rule('/posts/post_<int:id>', endpoint='post_details'),
            Rule('/rss', endpoint='rss'),
            Rule('/admin', endpoint='admin_welcome'),
            Rule('/admin/logout', endpoint='admin_logout'),
            Rule('/admin/login', endpoint='admin_login'),
            Rule('/admin/posts/create', endpoint='admin_create_post'),
            Rule('/admin/posts/edit/<int:post_id>', endpoint='admin_edit_post'),
            Rule('/admin/posts/delete/<int:post_id>', endpoint='admin_delete_post'),
            Rule('/admin/pages/create', endpoint='admin_create_page'),
            Rule('/admin/pages/edit/<int:page_id>', endpoint='admin_edit_page'),
            Rule('/admin/pages/delete/<int:page_id>', endpoint='admin_delete_page'),
        ])

    """
    handle incoming WSGI requests.
    """
    def handle_request(self, environment, start_response):
        # wsgi janitoring
        request = Request(environment)
        adapter = self.url_map.bind_to_environ(request.environ)    
        endpoint, values = adapter.match()
        
        # prepare sqlalchemy session
        session = self.session_factory()        

        # put config and jinja environment in environment variable
        environment['blog.config'] = self.config
        environment['blog.jinja_env'] = self.jinja_env

        # execute views
        response = getattr(views, endpoint)(request, environment, session, **values)
        return response(environment, start_response) 
    
    """
    redirect incoming WSGI requests to handle_request
    """
    def __call__(self, environment, start_response):
        return self.handle_request(environment, start_response)

def create_app(config_path='blog.cfg', with_static=True):
    app = Blog(config_path)
    
    # adds static directory serving if needed
    #   In production content, leave the web serving 
    #   to the _real_ web server instead of the 
    #   werkzeug middleware.
    app = SessionMiddleware(app)
    app = SharedDataMiddleware(app, {'/static': 'static'})
    
    return app

if __name__ == '__main__':
    from werkzeug import run_simple
    from werkzeug import script

    # actions for argv
    action_runserver = script.make_runserver(create_app, use_debugger=True, use_reloader=True)
    action_initdb = lambda: model.initdb(Blog(config_path='blog.cfg').engine) 
    action_shell = script.make_shell(lambda: {'blog': Blog(config_path='blog.cfg')}) 
    script.run()
