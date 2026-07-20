from .Helpers import *

import json
from typing_extensions import Literal, Union

def child_to_obj(child_dict: dict) -> Union["Url", "Folder"]:
    match child_dict ["type"]:
        case "folder":
            return Folder(child_dict)
        case _:
            return Url(child_dict)

def children_to_obj(children_list: list) -> list[Union["Url", "Folder"]]:
    objects = []
    for child_dict in children_list:
        objects.append(child_to_obj(child_dict))

    return objects

class Folder:
    def __init__(self, child_dict: dict):
        #for key in child_dict.keys():
        #    setattr(self, key, child_dict[key])

        self.date_added: int = int(child_dict ["date_added"])
        self.date_last_used: int = int(child_dict ["date_last_used"])
        self.date_modified: int | None = int(child_dict ["date_modified"]) if "date_modified" in child_dict.keys() else None
        self.guid: str = child_dict ["guid"]
        self.id: int = int(child_dict ["id"])
        self.name: str = child_dict ["name"]

        self.date_added_datetime = chrome_time_to_datetime(self.date_added)
        self.date_last_used_datetime = chrome_time_to_datetime(self.date_last_used)
        self.date_modified_datetime = chrome_time_to_datetime(self.date_modified)

        self.bookmarks = children_to_obj(child_dict ["children"])
    
    def search_bookmarks(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False, in_subfolders: bool = True):
        query = query if case_sensitive else query.lower()
        results = []

        for element in self.bookmarks:
            if type(element) == Url:
                match mode:
                    case "any":
                        if not any([word in (attr if case_sensitive else attr.lower()) for word in query.split() for attr in (element.name, element.url)]):
                            continue
                    case "all":
                        if not all([any([word in (attr if case_sensitive else attr.lower()) for attr in (element.name, element.url)]) for word in query.split()]):
                            continue
                    case "exact":
                        if not any([query == (attr if case_sensitive else attr.lower()) for attr in (element.name, element.url)]):
                            continue
                results.append(element)
            elif in_subfolders:
                results += element.search_bookmarks(query, mode, in_subfolders)

        return results
    
    def __str__(self):
        return "\n".join(["📁 " + colored_text(self.name, color.YELLOW),
                        f"Added {self.date_added_datetime}",
                        f"Last used {self.date_last_used_datetime}"])
            
        


class Url:
    def __init__(self, child_dict: dict):
        #for key in child_dict.keys():
        #    setattr(self, key, child_dict[key])

        self.date_added: int = int(child_dict ["date_added"])
        self.date_last_used: int = int(child_dict ["date_last_used"])
        self.date_modified: int | None = int(child_dict ["date_modified"]) if "date_modified" in child_dict.keys() else None
        self.guid: str = child_dict ["guid"]
        self.id: int = int(child_dict ["id"])
        self.name: str = child_dict ["name"]
        self.url: str = child_dict ["url"]

        self.date_added_datetime = chrome_time_to_datetime(self.date_added)
        self.date_last_used_datetime = chrome_time_to_datetime(self.date_last_used)
        self.date_modified_datetime = chrome_time_to_datetime(self.date_modified) if "date_modified" in child_dict else None

    def __str__(self):
        return "\n".join([colored_text(f"• {self.name}", color.CYAN),
                          colored_text(self.url, color.LIGHTBLUE_EX),
                          f"Added {self.date_added_datetime}",
                          f"Last used {self.date_last_used_datetime}"])
    
class Root(Folder):
    def __init__(self, root_dict: dict):
        super().__init__(root_dict)

    def __str__(self):
        return "🗀 " + colored_text(self.name, color.LIGHTGREEN_EX)


""" def child_to_obj(child_dict: dict):
    match child_dict ["type"]:
        case "folder":
            Folder(child_dict)
        case _:
            Bookmark(child_dict) """
    
""" def get_roots(bookmarks_json_path: str):
    with open(bookmarks_json_path, "r", encoding="utf-8") as bookmarks_file:
        bookmarks_data = json.load(bookmarks_file)

        roots = []
        for root_dict in bookmarks_data ["roots"].values():
            roots.append(Root(root_dict))

        return roots """
    
class BookmarksSession:
    def __init__(self, bookmarks_dict: dict):
        self.bookmarks_data = bookmarks_dict

        self.get_roots()

    def get_roots(self):
        self.roots: list[Root] = [Root(root_dict) for root_dict in self.bookmarks_data ["roots"].values()]

    def search_bookmarks(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False, in_subfolders: bool = True):
        results = []
        for root in self.roots:
            results += root.search_bookmarks(query, mode, case_sensitive, in_subfolders)

        return results

def create_bookmarks_session(bookmarks_json_path: str) -> BookmarksSession:
    '''Create a BookmarksSession instance using the Bookmarks json file path'''
    with open(bookmarks_json_path, "r", encoding="utf-8") as bookmarks_file:
        bookmarks_dict = json.load(bookmarks_file)
        return BookmarksSession(bookmarks_dict)

    
if __name__ == "__main__":
    b = create_bookmarks_session("Bookmarks.json")
    results = b.search_bookmarks("python", mode="any")

    print(*results, sep="\n\n")

