"""
Need to replace the DB logic from below with updated SQLAlchemy calls. The current logic for these functions are no longer compatible with the greater app and DB at this time.

That said, it should be fixable once I have the time, therefore I'm leaving in this 'disabled' state for now.
"""

import requests
from lxml import html
from werkzeug.exceptions import abort

from zaphod.models import db, DotaHero


def get_dota_heroes():
    url = "https://dota2.fandom.com/wiki/Table_of_hero_attributes"
    page = requests.get(url)
    tree = html.fromstring(page.content)
    xpath = '//table[contains(@class, "wikitable")]/tbody/tr[position()>1]'
    heroes_data = tree.xpath(xpath)
    heroes = []
    for hero in heroes_data:
        sub_xpath = ".//td[1]//a[2]//text()"
        name = hero.xpath(sub_xpath)[0]
        sub_xpath = ".//td[last()]/text()"
        leg_count = (hero.xpath(sub_xpath))[0].rstrip()
        heroes.append(DotaHero(name, leg_count))
    return heroes


def get_dota_heroes_as_tuples_for_db():
    heroes = get_dota_heroes()
    names = [hero.name for hero in heroes]
    leg_counts = [hero.leg_count for hero in heroes]
    list_of_tuples = [(names[i], leg_counts[i]) for i in range(0, len(names))]
    return list_of_tuples


# def get_dota_hero(id):
#     """Get a dota hero by id.

#     Checks that the id exists.

#     :param id: id of dota hero to get
#     :return: the dota hero
#     :raise 404: if a dota hero with the given id doesn't exist
#     """
#     dota_hero = (
#         db.get_db()
#         .execute(
#             "SELECT dh.id, hero_name, leg_count"
#             " FROM dota_hero dh"
#             " WHERE dh.id = ?",
#             (id,),
#         ).fetchone()
#     )

#     if dota_hero is None:
#         abort(404, f"Dota hero id {id} doesn't exist.")

#     return dota_hero
