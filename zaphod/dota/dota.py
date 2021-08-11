"""
Need to replace the DB logic from below with updated SQLAlchemy calls. The current logic for this Blueprint's routes are no longer compatible with the greater app and DB at this time.

That said, it should be fixable once I have the time, therefore I'm leaving in this 'disabled' state for now.
"""
import random

from flask import Blueprint, render_template

from zaphod import models
from zaphod.dota import utils

bp = Blueprint("dota", __name__, url_prefix="/experiments/dota",
               template_folder='templates', static_folder="static")


# @bp.route("/legs")
# def legs():
#     """Show all the dota heros."""
#     db = get_db()
#     dota_heroes = []
#     dota_heroes_data = db.execute(
#         "SELECT dh.id, hero_name, leg_count"
#         " FROM dota_hero dh"
#         " ORDER BY leg_count ASC"
#     ).fetchall()
#     for data_row in dota_heroes_data:
#         data_row
#         dota_hero = models.DotaHero(*data_row[1:])
#         dota_heroes.append(dota_hero.asDict())
#     return render_template("dota/all_hero_legs.html", dota_heroes=dota_heroes)


# @bp.route("/legs/random")
# def random_legs():
#     """Show leg data for a randomly selected dota hero."""
#     # db = get_db()
#     # dota_hero_count = db.execute(
#         "SELECT COUNT(*)"
#         " FROM dota_hero"
#     ).fetchone()
#     rand_id = random.randint(0, dota_hero_count[0] - 1)
#     dota_hero = utils.get_dota_hero(rand_id)
#     return render_template("dota/random_hero_legs.html", dota_hero=dota_hero)
