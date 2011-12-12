#!/usr/bin/env python
import argparse
import glob
import os
from bottle import Bottle, LocalRequest, run, template
import misaka

GENERATED_DIR = 'generated/'
POSTS_DIR = 'posts/'

# monkey patch LocalRequest
LocalRequest.environ = {}
app = Bottle()


def list_posts():
    posts = []
    for md in glob.glob(POSTS_DIR + '*.md'):
        name = os.path.splitext(os.path.basename(md))[0]
        posts.append(name)
    return posts


def cache_routes(app):
    def cache_static(route):
        path = os.path.join(GENERATED_DIR, route.rule[1:])
        try:
            os.mkdir(path)
        except OSError:
            pass
        with open(os.path.join(path, 'index.html'), 'w') as html:
            html.write(route.call())

    def cache_posts(route):
        posts_path = os.path.join(GENERATED_DIR, 'posts')
        try:
            os.mkdir(posts_path)
        except OSError:
            pass
        for md in list_posts():
            path = os.path.join(posts_path, md)
            try:
                os.mkdir(path)
            except OSError:
                pass
            with open(os.path.join(path, 'index.html'), 'w') as html:
                html.write(route.call(post=md))

    for route in app.routes:
        if route.name == 'posts':
            cache_posts(route)
        else:
            cache_static(route)


@app.get('/')
def index():
    posts = dict((name, app.get_url('posts', post=name)) for name in list_posts())
    return template('index', posts=posts)


@app.get('/posts/:post/', name='posts')
def posts(post):
    with open(os.path.join(POSTS_DIR, post + '.md')) as md:
        html = misaka.html(md.read())
    return template('posts', content=html, title=post)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    args = parser.parse_args()
    if args.generate:
        cache_routes(app)
    else:
        run(app=app)
