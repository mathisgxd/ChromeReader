""" 
Profiler joins History, Bookmarks and LoginData modules to get all the data of a user profile
 """


""" import LocalState

class Profile(LocalState.Profile):
    def __init__(self):
        super().__init__()



class Session(LocalState.LocalStateSession):
    def __init__(self, local_state_dict: str):
        super().__init__(local_state_dict)


if __name__ == "__main__":
    s = Session("Local State.json")
    s. """


from . import Folders
from . import LocalState
from .Helpers import load_json

from . import History
from . import Bookmarks
from . import LoginData

import os
from warnings import warn
from functools import cached_property
import PIL

class Profile(Folders.ProfileFolder, LocalState.Profile):
    '''
    This class joins the LocalState Profile (for info) with its ProfileFolder (for data)
    It also offers the user's history, bookmarks and logins.

    Use the save method to copy all the necessary files and data into a folder
    Use Profile.load method to load a previously copied folder
    '''
    """ history: History.HistorySession | None
    bookmarks: Bookmarks.BookmarksSession | None
    login_data: LoginData.LoginDataSession | None """

    def __init__(self, path, profile_dict: dict, profile_name: str | None):
        super().__init__(path)
        LocalState.Profile.__init__(self, profile_dict, profile_name)

    @cached_property
    def history(self) -> History.HistorySession | None:
        try:
            return History.create_history_session(os.path.join(self.path, "History"))
        except:
            warn(f"Failed to get history of Profile {self.name} ({self.profile_name})")
            return None
        
    @cached_property
    def bookmarks(self) -> History.HistorySession | None:
        try:
            return Bookmarks.create_bookmarks_session(os.path.join(self.path, "Bookmarks"))
        except:
            warn(f"Failed to get bookmarks of Profile {self.name} ({self.profile_name})")
            return None
        
    @cached_property
    def login_data(self) -> History.HistorySession | None:
        try:
            return LoginData.create_login_data_session(os.path.join(self.path, "Login Data"))
        except:
            warn(f"Failed to get login data of Profile {self.name} ({self.profile_name})")
            return None
        
    @cached_property
    def profile_picture(self) -> History.HistorySession | None:
        try:
            return PIL.Image.open(os.path.join(self.path, "Google Profile Picture.png"))
        except:
            warn(f"Failed to get profile picture of Profile {self.name} ({self.profile_name})")
            return None

    def save(self, path: str, make_folder: bool = True):
        if make_folder:
            path = os.path.join(path, self.profile_name or self.name)

        os.makedirs(path, exist_ok=True)
        self.copy_all_files(path)
        self.save_as_file(path)

        return path

    @classmethod
    def load(cls, path: str):
        return cls(path, profile_dict=load_json(os.path.join(path, "ProfileLocalState.json")), profile_name=os.path.split(path)[1])
        

class ProfilerLoader:
    def __init__(self, path: str):
        super().__init__(path)
        self.profiles = self.get_profiles()

    def get_profiles_names(self) -> list[str]:
        return os.path.listdir(self.path)

    def get_profile(self, profile_name: str = "Default") -> Profile:
        return Profile.load(os.path.join(self.path, profile_name))

    def get_profiles(self, profile_names: list[str] | None = None) -> list[Profile]:
        profile_names = profile_names or self.get_profiles_names()
        profiles = [self.get_profile(profile_name) for profile_name in profile_names]

    def save_profiles(self, path: str):
        for profile in self.profiles:
            profile.save(path, make_folder=True)


class Profiler(Folders.UserDataFolder, LocalState.LocalStateSession):
    '''
    This class joins the LocalStateSession (for info) with the UserDataFolder (for data) to get full profiles
    '''
    def __init__(self, user_data_path: str = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')):
        super().__init__(user_data_path)
        LocalState.LocalStateSession.__init__(self, load_json(os.path.join(self.path, "Local State")))

        self.profiles: list[Profile] = self.get_profiles()

    def get_profile(self, profile_name = "Default") -> Profile:
        profile_path = os.path.join(self.path, profile_name)
        profile_dict = self.get_profile_dict(profile_name)
        return Profile(profile_path, profile_dict, profile_name)
    
    def save_profiles(self, path: str):
        for profile in self.profiles:
            profile.save(path, make_folder=True)

    @classmethod
    def load_profiles(cls, path: str) -> ProfilerLoader:
        '''
        Load saved profiles
        '''
        return ProfilerLoader(path)

    
    
if __name__ == "__main__":
    test: str = "save"

    match test:
        case "save":
            profiler = Profiler(os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data'))
            profiles = profiler.save_profiles("profiles")
        case "load":
            profile = Profile.load(r"profiles\Default")
            print(profile)