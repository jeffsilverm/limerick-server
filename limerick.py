#! /usr/bin/python

import cgi      # we need this to parse the response from the browser.

# This is our application object. It could have any name,
# except when using mod_wsgi where it must be "application"
def application( # It accepts two arguments:
      # environ points to a dictionary containing CGI like environment variables
      # which is filled by the server for each received request from the client
      environ,
      # start_response is a callback function supplied by the server
      # which will be used to send the HTTP status and headers to the server
      start_response):

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    d = cgi.parse_qs(request_body)
    try:
        operation = d['operation']     # d is a dictionary of lists
    except (KeyError):
        operation = [None]

    # build the response body possibly using the environ dictionary.
    if operation[0] == None :
        response_body = generate_initial_form( environ )
    elif operation[0] == "add limerick" :
        response_body = generate_add_limerick_form( environ )
    elif operation[0] == "lookup limerick" :
        response_body = generate_lookup_limerick_form( environ )
    elif operation[0] == "enter limerick" :
        response_body = enter_limerick ( environ, d["limerick_body"][0] )
    elif operation[0] == "lookup limerick 2" :
# This hasn't been written yet so go back to the initial form       
        response_body = generate_initial_form( environ )        
    else :
# This is the start of some debugging code
       response_body = """<html><body>"""
       response_body += "The request method was %s" % environ['REQUEST_METHOD']
       response_body += '\nthe rest of the environment is<br>'
       for envar in environ.keys() :
           response_body += "\n%s : %s<br>" % ( envar, environ[envar] )
       response_body += "\n<hr>\n"
       for dk in d.keys() :
           response_body += "\n%s : %s<br>" % ( dk, d[dk][0] )
# This is the end of the debugging code
    response_body += "</body></html>"         

    # HTTP response code and message
    status = '200 OK'

    # These are HTTP headers expected by the client.
    # They must be wrapped as a list of tupled pairs:
    # [(Header name, Header value)].
    response_headers = [('Content-Type', 'text/html'),
                       ('Content-Length', str(len(response_body)))]

    # Send them to the server using the supplied function
    start_response(status, response_headers)

    # Return the response body.
    # Notice it is wrapped in a list although it could be any iterable.
    return [response_body]


def generate_initial_form ( environ ) :
    """This function returns an HTML which contains the initial form that the user should fill in"""
    body = """
<html>
  <head>
    <title>Select whether to lookup a limerick or enter a limerick</title>
  </head>
  <body>
    <FORM action="http://%s%s" method="post">
      <INPUT type="hidden" value="excaliber" name="find_excaliber">
      <INPUT type="submit" value="add limerick" name="operation">
      <INPUT type="submit" value="lookup limerick" name="operation">
    </FORM>
""" % ( environ["HTTP_HOST"], environ["REQUEST_URI"] )
# The closing </body> and </html> tags are taken care of by the caller

    return body

def generate_add_limerick_form( environ ) :
    """This function returns an HTML body which contains the form to add a limerick"""
    body = """
<html>
  <head>
    <title>Form to enter a limerick</title>
  </head>
  <body>
    <FORM action="http://%s%s" method="post">
      <TEXTAREA value="limerick text goes here" name="limerick_body" rows="5" cols="80"></TEXTAREA>
      <br>
      <INPUT type="submit" value="enter limerick" name="operation">
    </FORM>
""" % ( environ["HTTP_HOST"], environ["REQUEST_URI"] )
    return body

def generate_lookup_limerick_form( environ ) :
    """This function returns an HTML body which contains the form to lookup a limerick"""
    body = """
<html>
  <head>
    <title>Form to lookup a limerick</title>
  </head>
  <body>
  Unfortunately, the code to lookup a limerick hasn't been written yet<br>
    <FORM action="http://%s%s" method="post">
      <INPUT type="submit" value="lookup limerick 2" name="operation">
    </FORM>

""" % ( environ["HTTP_HOST"], environ["REQUEST_URI"] )

    return body

def enter_limerick ( environ, limerick_body ) :
    """This function enters the limerick into the body of the database"""
# The limerick body will have newlines.  Convert them to HTML <br>
    s = limerick_body.replace ( "\n", "<br>\n" )
    body = """
<html>
  <head>
    <title>The limerick has been entered</title>
  </head>
  <body>
  <hr>
  The limerick is:
  <i>
  %s
  </i>
  Thank you for using the limerick server
    <FORM action="http://%s%s" method="post">
      <INPUT type="hidden" value="excaliber" name="find_excaliber">
      <INPUT type="submit" value="add limerick" name="operation">
      <INPUT type="submit" value="lookup limerick" name="operation">
    </FORM>
""" % ( s, environ["HTTP_HOST"], environ["REQUEST_URI"] )

    return body
