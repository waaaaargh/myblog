from werkzeug.wrappers import Response
import re

def render_template(template_name, environment, mimetype='text/html', **kwargs):
    jinja_env = environment['blog.jinja_env']
    template = jinja_env.get_template(template_name)
    return Response(template.render(**kwargs), mimetype=mimetype)

def generate_slug(string):
    """
    Generates a "slug", SEO-URL-Version of the sting-input

    >>> generate_slug("This is a test.")
    'this-is-a-test'

    >>> generate_slug("This! is another(!) One!")
    'this-is-another-one'
    """
    string = re.sub(r'\W+', ' ', string.lower())
    string = string.strip()

    string = re.sub(' ', '-', string)    
    return string

def render_form(form_obj, action):
    output  = "<form method='POST' action='"+action+"'>"
    for field in form_obj:
        output += '<div>'+str(field.label)+': '+field()+'</div>'
    output += '<input type="submit">'
    output += '</form>'
    return output 

if __name__ == '__main__':
    import doctest
    doctest.testmod()
