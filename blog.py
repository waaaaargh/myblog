#!/usr/bin/python2

import os

from werkzeug.wrappers import Request, Response
from jinja2 import Environment, FileSystemLoader

from config import Configuration
import views
import model

class Blog(object):
    """
    set up blog instance.
    """
    def __init__(self, config_path):
        # load config
        self.config = Configuration()
        self.config.load_from_file(config_path)

        # initialize sqlalchemy
        from sqlalchemy import create_engine
        self.engine = create_engine(self.config.database_uri)

        # initialize jinja templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        )

        # set url maps
        from werkzeug.routing import Map, Rule
        
        # rules for URLs
        self.url_map = Map([
            Rule('/', endpoint='hello'),
        ])

    """
    handle incoming WSGI requests.
    """
    def handle_request(self, environment, start_response):
        # wsgi janitoring
        request = Request(environment)
        adapter = self.url_map.bind_to_environ(request.environ)    
        endpoint, values = adapter.match()
        
        # execute views
        d = getattr(views, endpoint)(request, environment)
        
        # get and render template
        template = self.jinja_env.get_template( endpoint+'.htmljinja' )
        output = template.render(**d)

        # wsgi janitoring
        response = Response(output)
        return response(environment, start_response) 
    
    """
    redirect incoming WSGI requests to handle_request
    """
    def __call__(self, environment, start_response):
        return self.handle_request(environment, start_response)

def create_app(config_path='blog.cfg'):
    return Blog(config_path)

if __name__ == '__main__':
    from werkzeug import run_simple
    from werkzeug import script

    # actions for argv
    action_runserver = script.make_runserver(create_app, use_debugger=True, use_reloader=True)
    action_initdb = lambda: model.initdb(create_app().engine) 
    script.run()
