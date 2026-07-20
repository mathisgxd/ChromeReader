import customtkinter as ctk
from . import History as h
from . import Bookmarks as bm
from . import LoginData as lg
from . import LocalState as ls
from . import ProfileManager

import webbrowser
import pyperclip
from typing_extensions import Union
import PIL
import os

# Helper functions
def bookmark_to_frame(master, bookmark: Union[bm.Root, bm.Url, bm.Folder]) -> Union["BookmarksFolderFrame", "BookmarksUrlFrame"]:
    match type(bookmark):
        case bm.Root | bm.Folder:
            return BookmarksFolderFrame(master, bookmark)
        case bm.Url:
            return BookmarksUrlFrame(master, bookmark)
        
def bookmarks_to_frames(master, bookmarks: list[Union[bm.Root, bm.Url, bm.Folder]]) -> list[Union["BookmarksFolderFrame", "BookmarksUrlFrame"]]:
    frames = [bookmark_to_frame(master, bookmark) for bookmark in bookmarks]
    return frames

# Fonts
class GiantFont(ctk.CTkFont):
    def __init__(self):
        super().__init__(
            family="Segoe UI",
            size=30,
            weight="bold"
        )

class BigFont(ctk.CTkFont):
    def __init__(self):
        super().__init__(
            family="Segoe UI",
            size=18,
            weight="bold"
        )

class MidFont(ctk.CTkFont):
    def __init__(self):
        super().__init__(
            family="Segoe UI",
            size=16,
            weight="bold"
        )

# Frames
class ExpandableFrame(ctk.CTkFrame):
    '''
    A subclass of CTkFrame which has the ability to expand and retract
    '''
    def __init__(self, master, expand: bool = False, **kwargs):
        super().__init__(master, **kwargs)

        self.expanded = None

        self.expand_or_retract = lambda: self.retract() if self.expanded else self.expand()

        if expand:
            self.expand()

    def _expand(self):
        '''Overwrite in subclass'''
        pass

    def _retract(self):
        '''Overwrite in subclass'''
        pass

    def expand(self):
        self._expand()
        self.expanded = True

    def retract(self):
        self._retract()
        self.expanded = False


class HistoryVisitFrame(ctk.CTkFrame):
    '''
    A subclass of CTkFrame\n
    intended for History.Visit
    '''
    def __init__(self, master, visit: h.Visit, **kwargs):
        super().__init__(master, **kwargs)

        self.visit = visit

        self.label = ctk.CTkLabel(self,
                                         text=f"Visit: {self.visit.visit_datetime}\nDuration: {self.visit.visit_duration_timedelta}",
                                         font=BigFont(),
                                         justify=ctk.LEFT,
                                         fg_color="dark cyan")
        self.label.pack(fill=ctk.X)

class HistoryVisitList(ctk.CTkFrame):
    '''
    A subclass of CTkScrollableFrame\n
    intended for List of History.Visit\n
    used internally in HistoryUrlFrame
    '''
    def __init__(self, master, visits: h.List[h.Visit], **kwargs):
        super().__init__(master, **kwargs)

        self.visits = visits

        for visit in visits:
            visit_frame = HistoryVisitFrame(self, visit)
            visit_frame.pack(fill=ctk.X, pady=8)
        

class BaseUrlFrame(ExpandableFrame):
    '''
    A subclass of ExpandableFrame\n
    compatible with both history and bookmarks urls
    '''
    def __init__(self, master, url: h.Url | bm.Url, **kwargs):
        super().__init__(master, **kwargs)

        self.url = url

        self.name_button = ctk.CTkButton(self,
                                         text=self.url.title if type(self.url) == h.Url else self.url.name,
                                         font=BigFont(),
                                         fg_color="dark slate gray",
                                         command=self.expand_or_retract)
        self.name_button.pack(fill=ctk.X)

        self.expandable_frame = ctk.CTkFrame(self,
                                             fg_color="dark slate gray",
                                             border_width=5,
                                             border_color="dark cyan")

        self.info_label = ctk.CTkLabel(self.expandable_frame,
                                       text=self.url.url,
                                       font=MidFont(),
                                       justify=ctk.LEFT)
        self.info_label.pack(pady=5)

        self.buttons_frame = ctk.CTkFrame(self.expandable_frame)

        open_link_button = ctk.CTkButton(self.buttons_frame,
                                         text="Open in browser",
                                         font=MidFont(),
                                         command=self.open_link)
        open_link_button.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=1)

        copy_link_button = ctk.CTkButton(self.buttons_frame,
                                         text="Copy",
                                         font=MidFont(),
                                         command=self.copy_link,
                                         width=85)
        copy_link_button.pack(side=ctk.LEFT, padx=1)

        self.buttons_frame.pack(fill=ctk.X, padx=5)

    def _expand(self):
        self.expandable_frame.pack(fill=ctk.X, pady=1, ipady=5)
        self.name_button.configure(fg_color="dark cyan")

    def _retract(self):
        self.expandable_frame.pack_forget()
        self.name_button.configure(fg_color="dark slate gray")

    
    def open_link(self):
        webbrowser.open(self.url.url)

    def copy_link(self):
        pyperclip.copy(self.url.url)

class HistoryUrlFrame(BaseUrlFrame):
    """
    A subclass of BaseUrlFrame\n
    Intended for History.Url
    """
    def __init__(self, master, url: h.Url, show_visit_list: bool = True, **kwargs):
        super().__init__(master, url, **kwargs)

        info_lines = [self.url.url,
                      f"Visited {self.url.visit_count} times"]
        
        if self.url.typed_count:
            info_lines.append(f"Typed {self.url.typed_count} times")

        self.info_label.configure(text="\n".join(info_lines))

        self.buttons_frame.pack_forget()

        if show_visit_list:
            visits_label = ctk.CTkLabel(self.expandable_frame,
                                        text=f"Visits ({len(self.url.visits)}):",
                                        font=BigFont())
            visits_label.pack(fill=ctk.X, padx=5)

            visits_list = HistoryVisitList(self.expandable_frame,
                                        visits=self.url.visits,
                                        fg_color="transparent")
            visits_list.pack(fill=ctk.X, padx=5)

            self.buttons_frame.pack(fill=ctk.X, padx=5)

class BookmarksUrlFrame(BaseUrlFrame):
    '''
    A subclass of BaseUrlFrame\n
    intended for Bookmarks.Url
    '''
    def __init__(self, master, url: bm.Url, **kwargs):
        super().__init__(master, url, **kwargs)

        info_lines = [self.url.url,
                      f"Added: {self.url.date_added_datetime}"]
        
        if self.url.date_last_used_datetime:
            info_lines.append(f"Last used: {self.url.date_last_used_datetime}")

        if url.date_modified_datetime:
            info_lines.append(f"Modified on {url.date_modified_datetime}")

        self.info_label.configure(text="\n".join(info_lines))

class BookmarksFolderFrame(ExpandableFrame):
    def __init__(self, master, folder: bm.Folder, **kwargs):
        super().__init__(master, **kwargs)

        self.folder = folder

        self.name_button = ctk.CTkButton(self,
                                         text=f"🗀 {folder.name}",
                                         font=BigFont(),
                                         text_color="black",
                                         fg_color="dark goldenrod",
                                         hover_color="yellow",
                                         command=self.expand_or_retract)
        self.name_button.pack(fill=ctk.X)

        self.expandable_frame = ctk.CTkFrame(self,
                                             fg_color="dark goldenrod",
                                             border_width=5,
                                             border_color="yellow")
        
        info_lines = [f"Added: {self.folder.date_added_datetime}"]

        if self.folder.date_last_used_datetime:
            info_lines.append(f"Last used: {self.folder.date_last_used_datetime}")

        if self.folder.date_modified_datetime:
            info_lines.append(f"Modified: {self.folder.date_modified_datetime}")

        self.info_label = ctk.CTkLabel(self.expandable_frame,
                                       text="\n".join(info_lines),
                                       font=MidFont(),
                                       text_color="black",
                                       justify=ctk.LEFT)
        self.info_label.pack(pady=5)

        self.bookmarks_frame = BookmarksList(self.expandable_frame,
                                              bookmarks=self.folder.bookmarks,
                                              fg_color="transparent")
        self.bookmarks_frame.pack(fill=ctk.BOTH, padx=5, pady=5, expand=True)

    def _expand(self):
        self.expandable_frame.pack(fill=ctk.BOTH, pady=1, anchor="w", expand=True)
        self.name_button.configure(fg_color="yellow")

    def _retract(self):
        self.expandable_frame.pack_forget()
        self.name_button.configure(fg_color="dark goldenrod")

class BookmarksList(ctk.CTkFrame): #CTkScrollableFrame
    def __init__(self, master, bookmarks: list[bm.Root | bm.Folder | bm.Url], **kwargs):
        super().__init__(master, **kwargs)

        self.bookmarks_frames = bookmarks_to_frames(self, bookmarks)

        for bookmark_frame in self.bookmarks_frames:
            bookmark_frame.pack(fill=ctk.X, pady=2)

        #self.configure(height=len(self.bookmarks_frames) * 30)

class BookmarksScrollableList(ctk.CTkScrollableFrame): #CTkScrollableFrame
    def __init__(self, master, bookmarks: list[bm.Root | bm.Folder | bm.Url], **kwargs):
        super().__init__(master, **kwargs)

        self.bookmarks_frames = bookmarks_to_frames(self, bookmarks)

        for bookmark_frame in self.bookmarks_frames:
            bookmark_frame.pack(fill=ctk.X, pady=2)

        #self.configure(height=len(self.bookmarks_frames) * 30)

class BookmarksFrame(ctk.CTkFrame):
    def __init__(self, master, bookmarks_session: bm.BookmarksSession, **kwargs):
        super().__init__(master, **kwargs)

        self.bookmarks_session = bookmarks_session

        search_bar = SearchBar(self, self.search, self.end_search)
        search_bar.pack(fill=ctk.X, pady=2)

        self.bookmarks_list = BaseScrollableList(self, self.bookmarks_session.roots, bookmark_to_frame)
        self.bookmarks_list.pack(fill=ctk.BOTH, expand=True)

    def search(self, query: str):
        bookmarks = self.bookmarks_session.search_bookmarks(query)
        self.bookmarks_list.pack_elements(bookmarks)

    def end_search(self):
        bookmarks = self.bookmarks_session.roots
        self.bookmarks_list.pack_elements(bookmarks)

""" class HistoryUrlList(ctk.CTkScrollableFrame):
    def __init__(self, master, urls: h.List[h.Url], **kwargs):
        super().__init__(master, **kwargs)

        self.urls_frames = [HistoryUrlFrame(self, url) for url in urls]

        for url_frame in self.urls_frames:
            url_frame.pack(fill=ctk.X, pady=2) """

class SearchBar(ctk.CTkFrame):
    def __init__(self, master, search_command, end_search_command, **kwargs):
        super().__init__(master, **kwargs)

        self.search_command = search_command
        self.end_search_command = end_search_command

        self.entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.entry.pack(fill=ctk.X, side=ctk.LEFT, expand=True)

        self.button = ctk.CTkButton(self, text="⌕", command=self.button_pressed, width=35)
        self.button.pack(side=ctk.LEFT)

        self.searching: bool = False

    def search(self):
        self.searching = True
        self.entry.configure(state="disabled")
        self.button.configure(text="✖")
        self.search_command(self.entry.get())

    def end_search(self):
        self.searching = False
        self.entry.configure(state="normal")
        self.entry.delete(0, ctk.END)
        self.button.configure(text="⌕")
        self.end_search_command()
        

    def button_pressed(self):
        if self.searching:
            self.end_search()
        else:
            self.search()



class BaseScrollableList(ctk.CTkScrollableFrame):
    def __init__(self, master, elements: list, t: type, pack_all: bool = True, **kwargs):
        super().__init__(master, **kwargs)

        self.t = t
        self.elements_frames = {element: None for element in elements}
        #self.frames = [self.t(self, element) for element in elements]
        if pack_all:
            self.pack_elements(self.elements_frames.keys())

    def pack_elements(self, elements: list):
        self.elements_frames = self.elements_frames | {element: self.t(self, element) for element in elements if element not in self.elements_frames.keys()}

        for frame in self.elements_frames.values():
            if frame is not None and frame.winfo_ismapped():
                frame.pack_forget()

        for element in elements:
            if (frame := self.elements_frames[element]) is None:
                frame = self.elements_frames[element] = self.t(self, element)
            frame.pack(fill=ctk.X, pady=2)

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master, history_session: h.HistorySession, **kwargs):
        super().__init__(master, **kwargs)

        self.history_session = history_session

        search_bar = SearchBar(self, self.search, self.end_search)
        search_bar.pack(fill=ctk.X, pady=2)

        urls = self.history_session.urls
        self.urls_list = BaseScrollableList(self, urls, HistoryUrlFrame, pack_all=False)
        self.urls_list.pack_elements(self.history_session.get_recent_urls(100))
        self.urls_list.pack(fill=ctk.BOTH, expand=True)

    def search(self, query: str):
        urls = self.history_session.search_urls(query)
        self.urls_list.pack_elements(urls)

    def end_search(self):
        #urls = self.history_session.urls
        urls = self.history_session.get_recent_urls(100)
        self.urls_list.pack_elements(urls)
    






""" class HistoryUrlList(ctk.CTkScrollableFrame):
    def __init__(self, master, urls: h.List[h.Url], **kwargs):
        super().__init__(master, **kwargs)

        self.urls_frames = [HistoryUrlFrame(self, url) for url in urls]

        for url_frame in self.urls_frames:
            url_frame.pack(fill=ctk.X, pady=2) """

class LoginsLoginFrame(ExpandableFrame):
    def __init__(self, master, login: lg.Login, **kwargs):
        super().__init__(master, **kwargs)

        self.login = login

        self.name_button = ctk.CTkButton(self,
                                         text=self.login.origin_url,
                                         font=BigFont(),
                                         fg_color="dark green",
                                         hover_color="green",
                                         command=self.expand_or_retract)
        self.name_button.pack(fill=ctk.X)

        self.expandable_frame = ctk.CTkFrame(self,
                                             fg_color="dark green",
                                             border_width=5,
                                             border_color="green")
        
        self.name_pass_frame = ctk.CTkFrame(self.expandable_frame,
                                            fg_color="transparent")

        username_frame = ctk.CTkFrame(self.name_pass_frame,
                                      fg_color="transparent")

        username_label = ctk.CTkLabel(username_frame,
                                      text="USERNAME: ",
                                      font=BigFont(),
                                      fg_color="transparent")
        username_label.pack(side=ctk.LEFT)

        username_entry = ctk.CTkEntry(username_frame,
                                      font=BigFont(),
                                      fg_color="dark green",
                                      border_color="green")
                                      #state="disabled")
        username_entry.insert(0, self.login.username_value)
        username_entry.configure(state="readonly")
        username_entry.pack(side=ctk.RIGHT, fill=ctk.X, expand=True)

        username_frame.pack(fill=ctk.X, side=ctk.TOP)

        password_frame = ctk.CTkFrame(self.name_pass_frame,
                                      fg_color="transparent")

        password_label = ctk.CTkLabel(password_frame,
                                      text="PASSWORD: ",
                                      font=BigFont(),
                                      fg_color="transparent")
        password_label.pack(side=ctk.LEFT)

        password_entry = ctk.CTkEntry(password_frame,
                                      font=BigFont(),
                                      fg_color="dark green",
                                      border_color="green")
                                      #state="disabled")
        password_entry.insert(0, self.login.password_value)
        password_entry.configure(state="readonly")
        password_entry.pack(side=ctk.RIGHT, fill=ctk.X, expand=True)

        password_frame.pack(fill=ctk.X, side=ctk.BOTTOM)

        self.name_pass_frame.pack(fill=ctk.X, padx=5)

        info_lines = [f"Created: {self.login.date_created_datetime}"]
        if self.login.date_password_modified_datetime:
            info_lines.append(f"Password modified: {self.login.date_password_modified_datetime}")
        info_lines.append(f"Used {self.login.times_used} times")
        if self.login.date_last_used_datetime:
            info_lines.append(f"Last used: {self.login.date_last_used_datetime}")
        """ if self.login.date_last_filled_datetime:
            info_lines.append(f"Last filled: {self.login.date_last_filled_datetime}") """

        self.info_label = ctk.CTkLabel(self.expandable_frame,
                                       text="\n".join(info_lines),
                                       font=MidFont(),
                                       justify=ctk.LEFT)
        self.info_label.pack(pady=5)

    def _expand(self):
        self.expandable_frame.pack(fill=ctk.X, pady=1, ipady=5)
        self.name_button.configure(fg_color="green")

    def _retract(self):
        self.expandable_frame.pack_forget()
        self.name_button.configure(fg_color="dark green")

class LoginsFrame(ctk.CTkFrame):
    def __init__(self, master, login_data_session: lg.LoginDataSession, **kwargs):
        super().__init__(master, **kwargs)

        self.login_data_session = login_data_session

        search_bar = SearchBar(self, self.search, self.end_search)
        search_bar.pack(fill=ctk.X, pady=2)

        self.logins_list = BaseScrollableList(self, self.login_data_session.logins, LoginsLoginFrame)
        self.logins_list.pack(fill=ctk.BOTH, expand=True)

    def search(self, query: str):
        logins = self.login_data_session.search_logins(query)
        self.logins_list.pack_elements(logins)

    def end_search(self):
        logins = self.login_data_session.logins
        self.logins_list.pack_elements(logins)

""" class LoginsScrollableList(ctk.CTkScrollableFrame):
    def __init__(self, master, logins: lg.List[lg.Login], **kwargs):
        super().__init__(master, **kwargs)

        self.logins_frames = [LoginsLoginFrame(self, login) for login in logins]

        for login_frame in self.logins_frames:
            login_frame.pack(fill=ctk.X, pady=2) """

class LocalStateProfileFrame(ctk.CTkFrame):
    def __init__(self, master, profile: ls.Profile, profile_picture: PIL.Image, **kwargs):
        super().__init__(master, **kwargs)

        self.profile = profile
        self.profile_picture = profile_picture

        profile_picture_label = ctk.CTkLabel(self,
                                             text="",
                                             image=ctk.CTkImage(self.profile_picture, size=(150, 150)))
        profile_picture_label.pack(side=ctk.LEFT, padx=10, pady=10)#, expand=True)

        profile_data_frame = ctk.CTkFrame(self)

        profile_name_label = ctk.CTkLabel(profile_data_frame,
                                          text=self.profile.name,
                                          font=GiantFont())
        profile_name_label.pack(fill=ctk.X, pady=10)
        

        profile_info_lines = [f"{profile.gaia_name} | {profile.gaia_given_name} | {profile.user_name}",
                              f"Active time: {profile.active_time_timedelta}"]
        
        profile_info_label = ctk.CTkLabel(profile_data_frame,
                                               text="\n".join(profile_info_lines),
                                               font=BigFont(),
                                               justify=ctk.LEFT)
        profile_info_label.pack()

        profile_data_frame.pack(side=ctk.LEFT, fill=ctk.X, pady=10, expand=True)

# Apps


class ChromeReaderApp(ctk.CTk):
    def __init__(self, profile: ProfileManager.Profile):
        super().__init__()

        self.title(f"ChromeReader - {profile.profile_name}")
        self.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), r"AppIcon.ico"))
        self.geometry("1300x700")

        # Profile Frame
        profile_frame = LocalStateProfileFrame(self, profile, profile.profile_picture or PIL.Image.open("default_pfp.png"))
        profile_frame.pack(fill=ctk.X)

        # History URLs Frame
        urls_frame = ctk.CTkFrame(self)
        urls_label = ctk.CTkLabel(urls_frame,
                                text=f"HISTORY URLS ({len(profile.history.urls)})",
                                font=BigFont())
        urls_label.pack(fill=ctk.X)

        print("loading history...")
        hf = HistoryFrame(urls_frame, profile.history)
        hf.pack(fill=ctk.BOTH, expand=True)
        urls_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        # Bookmarks Frame
        bookmarks_frame = ctk.CTkFrame(self)
        bookmarks_label = ctk.CTkLabel(bookmarks_frame,
                                    text=f"BOOKMARKS",
                                    font=BigFont())
        bookmarks_label.pack(fill=ctk.X)

        print("loading bookmarks...")
        bf = BookmarksFrame(bookmarks_frame, profile.bookmarks)
        bf.pack(fill=ctk.BOTH, expand=True)
        bookmarks_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        # Logins Frame
        logins_frame = ctk.CTkFrame(self)
        logins_label = ctk.CTkLabel(logins_frame,
                                text=f"LOGINS ({len(profile.login_data.logins)})",
                                font=BigFont())
        logins_label.pack(fill=ctk.X)
        print("loading logins...")
        lsf = LoginsFrame(logins_frame, profile.login_data)
        lsf.pack(fill=ctk.BOTH, expand=True)
        logins_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

# Testing
if __name__ == "__main__":
    profile = ProfileManager.Profile.load(r"profiles\Default")
    app = ctk.CTk()
    history_frame = HistoryFrame(app, profile.history)
    history_frame.pack(fill=ctk.BOTH)




