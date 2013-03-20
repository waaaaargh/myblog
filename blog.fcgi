#!/usr/bin/python2
from flup.server.fcgi import WSGIServer
from blog import create_app

if __name__ == '__main__':
    application = create_app()
    WSGIServer(application).run()

