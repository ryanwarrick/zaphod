import os

from zaphod.models import DirectoryItem, DirectoryItemType
from zaphod.models import Article


def get_articles_tree(directory_items):
    articles_tree = []
    for directory_item in directory_items:
        directory_item_dict = {}
        # Get 'name' of type because DirectoryItem.type is an enum.
        directory_item_dict['type'] = directory_item.type.value
        directory_item_dict['name'] = directory_item.name
        directory_item_dict['content_articles_dir_relative_file_path'] = directory_item.articles_relative_path.replace(
            "\\", "/")  # Have to replace double backslashes in DB with forward slashes for Flask
        if directory_item.type == DirectoryItemType.DIRECTORY:
            children_directory_items = DirectoryItem.query.filter_by(
                parent_id=directory_item.id).all()
            directory_item_dict['children'] = get_articles_tree(
                children_directory_items)
        else:  # directory_item.type == DirectoryItemType.FILE
            title = Article.query.filter_by(
                file_path=directory_item.path).one().title
            directory_item_dict["article"] = {
                'content_articles_dir_relative_filepath': directory_item.articles_relative_path.replace("\\", "/"),
                'title': title
            }

        articles_tree.append(directory_item_dict)
    return articles_tree


def sort_by_key_in_nested_lists_and_dicts(list, sort_by_key, nesting_key):
    list = sorted(list, key=lambda x: x[sort_by_key], reverse=True)
    for item in list:
        if nesting_key in item:
            item[nesting_key] = sort_by_key_in_nested_lists_and_dicts(
                item[nesting_key], sort_by_key, nesting_key)
    return list
