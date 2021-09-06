import enum
import os
import re
from datetime import datetime

import mistune
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name

# Builds a SQLAlchemy DB object for use by zaphod/__init__.py.
db = SQLAlchemy()


def generate_file_name_no_ext_for_content(context):
    file_name_no_ext = os.path.splitext(
        context.get_current_parameters()['file_name'])[0]
    return file_name_no_ext


def generate_html_for_content(context):
    file_name = context.get_current_parameters()['file_name']
    content = context.get_current_parameters()['content']
    if file_name.endswith('.md'):
        html = md_to_html(content)
    else:
        html = content
    return html


def generate_name_for_directory_item(context):
    path = context.get_current_parameters()['path']
    name = os.path.basename(path)
    return name


def generate_articles_relative_file_path_for_directory_item(context):
    path = context.get_current_parameters()['path']
    articles_relative_file_path = os.path.relpath(path, os.path.join(
        current_app.instance_path, "content", "articles"))
    return articles_relative_file_path


PostTagMap = db.Table(
    'PostTagMap',
    db.Column('tag_id',
              db.Integer,
              db.ForeignKey('PostTag.id'),
              primary_key=True),
    db.Column('post_id',
              db.Integer,
              db.ForeignKey('Content.id'),
              primary_key=True)
)

ArticleTagMap = db.Table(
    'ArticleTagMap',
    db.Column('tag_id',
              db.Integer,
              db.ForeignKey('ArticleTag.id'),
              primary_key=True),
    db.Column('article_id',
              db.Integer,
              db.ForeignKey('Content.id'),
              primary_key=True)
)


class ContentType(enum.Enum):
    POST = "post"
    ARTICLE = "article"


class Content(db.Model):
    __tablename__ = "Content"
    CONTENT_FILE_TYPES = ('md', 'html')

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.Enum(ContentType))
    file_name = db.Column(db.String(50), unique=True, nullable=False)
    file_path = db.Column(db.String(200), unique=False, nullable=False)
    title = db.Column(db.String(200), unique=False, nullable=False)
    summary = db.Column(db.String(200), unique=False, nullable=False)
    content = db.Column(db.Text(2000), unique=False, nullable=False)
    file_name_no_ext = db.Column(db.String(50), unique=False, nullable=False,
                                 default=generate_file_name_no_ext_for_content)
    html = db.Column(db.Text(2000), unique=False, nullable=False,
                     default=generate_html_for_content)

    def __init__(self, **kwargs):
        # Call init of db.Model (super/parent class)
        super().__init__(**kwargs)

    def extract_content_file_data(content_path, regex_pattern):
        with open(content_path, 'r') as f:
            content_data = f.read()
        regex_object = re.compile(regex_pattern, re.X | re.DOTALL)
        metadata = regex_object.match(content_data).groupdict()
        content = re.split(regex_object, content_data)[-1]
        return metadata, content


class Article(Content):
    __tablename__ = "Article"
    tags = db.relationship('ArticleTag', secondary=ArticleTagMap, lazy='subquery',
                           backref=db.backref('Articles', lazy=True))

    def __init__(self, content_type, file_name, file_path, title, summary, content):
        super().__init__(content_type=content_type, file_name=file_name, file_path=file_path,
                         title=title, summary=summary, content=content)

    @classmethod
    def parse_article_file(cls, content_path):
        """
        Use a regular expression to parse the components of a Markdown post's
        header and the post body. Return an assembled Post object,
        """
        pattern = r'''
            .*
            Title:\s(?P<Title>[^\n]*)\s.*
            Tags:\s(?P<Tags>[^\n]*)\s.*
            Summary:\s(?P<Summary>[^\n]*)
        '''
        post_metadata, post_content = super().extract_content_file_data(
            content_path, pattern)

        type = ContentType.ARTICLE.name
        file_name = os.path.basename(content_path)
        file_path = content_path
        title = post_metadata['Title']
        summary = post_metadata['Summary']
        tags = sorted([tag.strip()
                      for tag in post_metadata['Tags'].split(',')])
        if not Article.query.filter_by(file_path=file_path).all():
            article = Article(content_type=type,
                              file_name=file_name,
                              file_path=file_path,
                              title=title,
                              summary=summary,
                              content=post_content
                              )
            for tag_str in tags:
                tag = None
                # Newly Encountered tag 'name'
                if not ArticleTag.query.filter_by(name=tag_str).all():
                    tag = ArticleTag(name=tag_str)
                    article.tags.append(tag)
                # Previously Encountered tag 'name'
                else:
                    tag = ArticleTag.query.filter_by(name=tag_str).one()
                    article.tags.append(tag)
            db.session.add(article)
            db.session.commit()


class Post(Content):
    __tablename__ = "Post"
    date = db.Column(db.Date, unique=False, nullable=True)
    tags = db.relationship('PostTag', secondary=PostTagMap, lazy='subquery',
                           backref=db.backref('Posts', lazy=True))

    def __init__(self, content_type, file_name, file_path, title, summary, content, date):
        super().__init__(content_type=content_type, file_name=file_name, file_path=file_path,
                         title=title, summary=summary, content=content)
        self.date = date

    @classmethod
    def parse_post_file(cls, content_path):
        """
        Use a regular expression to parse the components of a Markdown post's
        header and the post body. Return an assembled Post object,
        """
        pattern = r'''
            .*
            Title:\s(?P<Title>[^\n]*)\s.*
            Date:\s(?P<Date>\d{4}-\d{2}-\d{2})\s.*
            Tags:\s(?P<Tags>[^\n]*)\s.*
            Summary:\s(?P<Summary>[^\n]*)
        '''
        post_metadata, post_content = super().extract_content_file_data(
            content_path, pattern)

        type = ContentType.POST.name
        file_name = os.path.basename(content_path)
        file_path = content_path
        title = post_metadata['Title']
        date = datetime.strptime(post_metadata['Date'], "%Y-%m-%d").date()
        summary = post_metadata['Summary']
        tags = sorted([tag.strip()
                      for tag in post_metadata['Tags'].split(',')])
        if not Post.query.filter_by(file_path=file_path).all():
            post = Post(content_type=type,
                        file_name=file_name,
                        file_path=file_path,
                        title=title,
                        summary=summary,
                        content=post_content,
                        date=date
                        )
            tags = list(set(tags))
            for tag_str in tags:
                tag = None
                # Newly Encountered tag 'name'
                if not PostTag.query.filter_by(name=tag_str).all():
                    tag = PostTag(name=tag_str)
                    post.tags.append(tag)
                # Previously Encountered tag 'name'
                else:
                    tag = PostTag.query.filter_by(name=tag_str).one()
                    post.tags.append(tag)
            db.session.add(post)
            db.session.commit()


class DirectoryItemType(enum.Enum):
    DIRECTORY = "directory"
    FILE = "file"


class DirectoryItem(db.Model):
    __tablename__ = "DirectoryItem"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(DirectoryItemType))
    name = db.Column(db.String(50), unique=False,
                     nullable=False, default=generate_name_for_directory_item)
    path = db.Column(db.String(260), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('DirectoryItem.id'),
                          nullable=True)
    articles_relative_path = db.Column(db.String(
        260), unique=True, nullable=False, default=generate_articles_relative_file_path_for_directory_item)


class PostTag(db.Model):
    __tablename__ = "PostTag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)


class ArticleTag(db.Model):
    __tablename__ = "ArticleTag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)


class HighlightRenderer(mistune.Renderer):
    """
    Extend renderer built into mistune module. This object enables code
    highlighting during Markdown-to-HTML conversions.
    """

    def block_code(self, code, lang):
        """
        Get the language indicated in each fenced code block. Get the
        appropriate Pygments lexer based on this language and parse code
        accordingly into HTML format. If not language is detected, use vanilla
        <code> blocks.
        """
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


def md_to_html(md_content):
    """
    Convert a Markdown string to HTML.
    """
    markdown_formatter = mistune.Markdown(
        renderer=HighlightRenderer(parse_block_html=True))
    html = markdown_formatter(md_content)
    return html
