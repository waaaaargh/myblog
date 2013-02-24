#!/usr/bin/python2

import os

from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import sessionmaker

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

        # set url maps
        from werkzeug.routing import Map, Rule
        
        # rules for URLs
        self.url_map = Map([
            Rule('/', endpoint='list_posts_lastweek'),
            Rule('/posts/<int:year>', endpoint='list_posts_year'),
            Rule('/posts/<int:year>/<int:month>', endpoint='list_posts_month'),
            Rule('/posts/<int:year>/<int:month>/<int:day>', endpoint='list_posts_day'),
            Rule('/posts/post_<int:id>', endpoint='post_details'),
            Rule('/admin/', endpoint='admin_welcome'),
            Rule('/admin/create', endpoint='admin_create_post'),
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

        # execute views
        d = getattr(views, endpoint)(request, environment, session, **values)
        
        # get and render template
        template = self.jinja_env.get_template( endpoint+'.htmljinja' )
        output = template.render(**d)

        # wsgi janitoring
        response = Response(output, mimetype='text/html')
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

    app = SharedDataMiddleware(app, {'/static': 'static'})
    
    return app

if __name__ == '__main__':
    from werkzeug import run_simple
    from werkzeug import script

    # actions for argv
    action_runserver = script.make_runserver(create_app, use_debugger=True, use_reloader=True)
    action_initdb = lambda: model.initdb(create_app().engine) 
    action_shell = script.make_shell(lambda: {'blog': create_app()})
    script.run()
