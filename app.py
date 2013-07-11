import urllib2
from functools import wraps

from pyquery import PyQuery as pq
from flask import Flask, jsonify, request, current_app

app = Flask(__name__)

def jsonp(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)

    return decorated_function

@app.route('/')
def index():
    return '/products/:id'

@app.route('/products/<id>')
@jsonp
def product_info(id):
    url = 'http://www.amazon.com/gp/product/%s' % id

    req = urllib2.Request(url)
    req.add_header('Accept-Language', 'en-US')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36')
    html = urllib2.urlopen(req).read()

    d = pq(html)

    data = {}

    data['amazon_id'] = id
    data['amazon_url'] = url

    data['title'] = d('#btAsinTitle').text()
    data['image'] = d('#holderMainImage img').attr('src')
    data['author'] = d('.contributorNameTrigger').text()
    data['description'] = d('noscript #postBodyPS').text()

    return jsonify(**data)

if __name__ == '__main__':
    app.run(debug=True, port=1234) 
