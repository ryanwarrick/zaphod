import os
import sys
from datetime import datetime

import click
from flask import Flask, render_template
from flask.cli import with_appcontext

from zaphod.models import db


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load default/placeholder config values from the imported config module
    app.config.from_object('zaphod.config')

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Set config values for sqlite DB to be stored in app's instance path
    db_path = os.path.join(app.instance_path, "zaphod.sqlite")
    db_url = f"sqlite:///{db_path}"
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Load instance-specific config values (overwrites any overlapping keys previously set)
    app.config.from_pyfile("config.py", silent=True)

    # Inject variable(s) into template context
    # For dynamic copyright 'year' value
    @app.context_processor
    def inject_datetime_now():
        return {'now': datetime.utcnow()}

    # For instance-specific footer info
    @app.context_processor
    def inject_website_author_name():
        return {'website_author_name': app.config['WEBSITE_AUTHOR_NAME']}

    # For instance-specific footer info
    @app.context_processor
    def inject_website_url():
        return {'website_url': app.config['WEBSITE_URL']}

    # For instance-specific site root path target
    @app.context_processor
    def site_root_path_target():
        return {'site_root_path_target': app.config['SITE_ROOT_PATH_TARGET']}

    # Initialize Flask-SQLAlchemy and the init-db commands
    from zaphod.models import db
    db.init_app(app)
    app.cli.add_command(init_db_command)

    # Apply the blueprints to the app
    from zaphod.articles.articles import bp as articles_bp
    from zaphod.blog.blog import bp as blog_bp
    from zaphod.career.career import bp as career_bp
    from zaphod.home.home import bp as home_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(career_bp)

    # Set rule so domain root points to the 'home' route defined in the 'home' blueprint
    app.add_url_rule("/", endpoint=app.config['SITE_ROOT_PATH_TARGET'])

    # Set the 404 error handler
    app.register_error_handler(404, page_not_found)

    return app


@ click.command("init-db")
@ with_appcontext
def init_db_command():
    """Creates 'Flask init-db' command (using click library) and binds it to call the init_db() function."""
    init_db()
    click.echo("Initialized the database.")


def init_db():
    """Drop and recreate all tables in DB. Purges data and then repopulates instance content database entries from files on disk.
    """
    db.drop_all()  # Purge DB
    db.create_all()  # Recreate DB tables (empty)
    load_db_with_instance_content(db.get_app())  # Populate DB tables


def load_db_with_instance_content(app):
    """Calls helper functions to load the following content types from files to the database: (blog) posts, articles, & directory items.
    Args:
        app (flask.Flask - app)): Flask App
    """
    load_db_with_posts(app)
    load_db_with_articles(app)
    load_db_with_directory_items(app)


def load_db_with_posts(app):
    """Loads post content to the database.
    Loading from files of qualifying type in qualifying path within instance dir.
    Args:
        app (flask.Flask - app)): Flask App
    """
    # Load Posts (create DB entries of Post objects from content files)
    from zaphod.models import Post

    # Blog content source dir to walk through for files
    post_dir_path = os.path.join(
        app.instance_path, 'content', 'blog')
    try:
        for _, _, files in os.walk(post_dir_path):
            for file in files:
                if file.endswith(Post.CONTENT_FILE_TYPES):
                    content_path = os.path.join(post_dir_path, file)
                    # Parse (blog) post file and create Post object (& DB row) from data
                    Post.parse_post_file(content_path)
    except IOError:
        sys.exit(1)


def load_db_with_articles(app):
    """Loads article content to the database.
    Loading from files of qualifying type in qualifying path within instance dir.
    Args:
        app (flask.Flask - app)): Flask App
    """
    # Load Articles (create DB entries of Article objects from content files)
    from zaphod.models import Article

    # Articles content source dir to walk through for files
    article_dir_path = os.path.join(
        app.instance_path, 'content', 'articles')
    try:
        for root, _, files in os.walk(article_dir_path):
            for file in files:
                if file.endswith(Article.CONTENT_FILE_TYPES):
                    content_path = os.path.join(root, file)
                    # Parse article file and create Article object (& DB row) from data
                    Article.parse_article_file(content_path)
    except IOError:
        sys.exit(1)


def load_db_with_directory_items(app):
    """Loads directory item content to the database.
    Loading from files and dirs of qualifying type in qualifying path within instance dir.
    Args:
        app (flask.Flask - app)): Flask App
    """
    # Load DirectoryItems (create DB entries of DirectoryItems objects from article content files). For the article tree hierarchy nav page.
    from zaphod.models import DirectoryItem, DirectoryItemType

    # DirectoryItems (articles) content source dir to walk through for files
    article_dir_path = os.path.join(
        app.instance_path, 'content', 'articles')
    try:
        for root, dirs, files in os.walk(article_dir_path):
            root_in_db = DirectoryItem.query.filter_by(path=root).first()
            if root_in_db:
                parent_id = root_in_db.id
            else:
                parent_id = None
            for dir in dirs:
                dir_path = os.path.join(root, dir)  # full path
                # Create DirectoryItem object (& DB row) for current dir
                directoryItem = DirectoryItem(
                    type=DirectoryItemType.DIRECTORY.name, path=dir_path, parent_id=parent_id)
                db.session.add(directoryItem)
            for file in files:
                file_path = os.path.join(root, file)  # full path
                # Create DirectoryItem object (& DB row) for current file
                directoryItem = DirectoryItem(
                    type=DirectoryItemType.FILE.name, path=file_path, parent_id=parent_id)
                db.session.add(directoryItem)
            db.session.commit()
    except IOError:
        sys.exit(1)


def page_not_found(e):
    """Builds 404 'page not found' page to be registered as an error handler with the application above.

    Args:
        e (exception): Exception - see flask docs.

    Returns:
        [string]: Rendered 404 'page not found' template
    """
    return render_template('home/404.html')
