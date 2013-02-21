#!/usr/bin/python2

from werkzeug.wrappers import Request, Response

from config import Configuration
import views

class Blog(object):
    """
    set up blog instance.
    """
    def __init__(self, config_path):
        self.config = Configuration()
        self.config.load_from_file(config_path)

        from werkzeug.routing import Map, Rule
        self.url_map = Map([
            Rule('/', endpoint='hello'),
        ])

    def handle_request(self, environment, start_response):
        request = Request(environment)
        adapter = self.url_map.bind_to_environ(request.environ)    
        endpoint, values = adapter.match()

        d = getattr(views, endpoint)(request, environment)
        response = Response()
        return response(environment, start_response) 
   
    def __call__(self, environment, start_response):
        return self.handle_request(environment, start_response)

def create_app(config_path='blog.cfg'):
    return Blog(config_path)

if __name__ == '__main__':
    from werkzeug import run_simple
    app = create_app()
    run_simple('localhost', 9001, app,
        use_debugger=True,
        use_reloader=True
    )
