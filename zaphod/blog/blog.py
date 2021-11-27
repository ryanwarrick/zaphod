from flask import Blueprint, current_app, g, render_template
from sqlalchemy import desc, extract, funcfilter, text
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import func
from zaphod.blog import utils
from zaphod.models import ContentType, Post, PostTag, PostTagMap, db

bp = Blueprint("blog",
               __name__,
               url_prefix="/blog",
               template_folder='templates',
               static_folder="static"
               )


@bp.route("/")
def post_feed():
    posts = Post.query.filter_by(
        content_type=ContentType.POST.name).order_by(Post.date.desc()).all()
    return render_template('blog/post_feed.html', posts=posts)


@bp.route("/tags")
def tags_archive():
    tag_frequency_table = db.session.query(PostTag.name, func.count(
        PostTagMap.c.post_id).label('frequency')).join(PostTagMap).group_by(PostTag.name).order_by(desc(text('frequency')))
    tag_frequency_table = tag_frequency_table.all()
    return render_template('blog/tags_archive.html', tag_frequency_table=tag_frequency_table)


@bp.route("/tags/<selected_tag>")
def posts_by_tag(selected_tag):
    posts = Post.query.filter(Post.tags.any(
        name=selected_tag), Post.content_type.like(ContentType.POST.name))
    return render_template('blog/post_feed.html', posts=posts)


@bp.route('/<url_friendly_post_file_name>')
def post(url_friendly_post_file_name):
    post = Post.query.filter_by(
        url_friendly_file_name=url_friendly_post_file_name).first_or_404()
    return render_template('blog/post.html', post=post)


@ bp.route("/archive")
def date_archive():
    posts_only_subquery = Post.query.filter(
        Post.date.isnot(None)).subquery("posts_only")
    date_data = db.session.query(
        extract('year', posts_only_subquery.c.date).label("year"),
        extract('month', posts_only_subquery.c.date).label("month"),
        func.count(posts_only_subquery.c.id).label("post_count")
    ).group_by("year", "month")
    date_data = date_data.all()

    restructured_date_data = {}
    for tuple_row in date_data:
        (year, month, post_count) = tuple_row
        if year not in restructured_date_data:
            restructured_date_data[year] = {}
        if month not in restructured_date_data[year]:
            restructured_date_data[year][month] = post_count
    num_to_month_dict = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
        6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
        11: 'November', 12: 'December'
    }
    return render_template('blog/date_archive.html', date_data=restructured_date_data, num_to_month_dict=num_to_month_dict, enumerate=utils.enumerate_func)


@bp.route("/archive/<int:year>")
def post_feed_date_archive_by_year(year):
    posts = db.session.query(Post).filter(
        extract('year', Post.date) == year).all()
    return render_template('blog/post_feed.html', posts=posts)


@bp.route("/archive/<int:year>/<int:month>")
def post_feed_date_archive_by_year_and_month(year, month):
    posts = db.session.query(Post).filter(
        extract('year', Post.date) == year,
        extract('month', Post.date) == month
    ).all()
    return render_template('blog/post_feed.html', posts=posts)
