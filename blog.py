#coding:utf-8
"""
    wanzifa_blog
    this is my personal blog~~~😄
"""

import sys
import os
from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask_script import Manager, Shell


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'


app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)

manager = Manager(app)


def make_shell_context():
    manager.add_command("shell", Shell(make_context=make_shell_context))


@app.route("/wanzifa/")
def index():
    return render_template('index_b.html')


@app.route('/blog/')
def blog():
    articles = (p for p in pages if 'date' in p.meta)
    latest = sorted(articles, key=lambda p: p.meta['date'], reverse=True)
    return render_template('blog.html', pages=latest)


@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        manager.run()

