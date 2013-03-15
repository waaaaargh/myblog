from werkzeug.wrappers import Response

def render_template(template_name, environment, mimetype='text/html', **kwargs):
    jinja_env = environment['blog.jinja_env']
    template = jinja_env.get_template(template_name)
    return Response(template.render(**kwargs), mimetype=mimetype)
