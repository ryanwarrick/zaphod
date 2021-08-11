import os
import json

from flask import Blueprint, current_app, render_template

from zaphod.articles import utils
from zaphod.models import DirectoryItem, Content

bp = Blueprint("articles",
               __name__,
               url_prefix="/articles",
               template_folder='templates',
               static_folder="static"
               )


@bp.route("/")
def articles_tree():
    directory_items = DirectoryItem.query.filter_by(parent_id=None).all()
    articles_tree = utils.get_articles_tree(directory_items)
    articles_tree = utils.sort_by_key_in_nested_lists_and_dicts(
        articles_tree, 'type', 'children')
    return render_template('articles/content_directory.html', articles_tree=articles_tree)


@bp.route("/<path:path>")
def articles_tree_traversal(path):
    # path = path.replace("/", "\\")
    split_path = path.split('/')
    safe_path = os.path.join(*split_path)
    subdirectory = DirectoryItem.query.filter_by(
        articles_relative_path=safe_path).one()
    directory_items = DirectoryItem.query.filter_by(
        parent_id=subdirectory.id).all()
    articles_tree = utils.get_articles_tree(directory_items)
    articles_tree = utils.sort_by_key_in_nested_lists_and_dicts(
        articles_tree, 'type', 'children')
    return render_template('articles/content_directory.html', articles_tree=articles_tree)


@bp.route('/article/<path:path>')
def article(path):
    # path = path.replace("/", "\\")
    split_path = path.split('/')
    safe_path = os.path.join(*split_path)
    article_path = DirectoryItem.query.filter_by(
        articles_relative_path=safe_path).one().path
    # article_path = article_path.replace("/", "\\")
    article = Content.query.filter_by(file_path=article_path).one()
    return render_template('articles/article.html', article=article, path=path)
