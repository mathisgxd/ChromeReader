from .Helpers import *
import json
import os

class Profile:
    def __init__(self, profile_dict: dict, profile_name: str | None):# | None = None): 
        self.profile_dict = profile_dict
        self.profile_name = profile_name

        """ for key, value in self.profile_dict.items():
            setattr(self, key, value) """

        self.active_time: float = profile_dict["active_time"]
        self.gaia_given_name: str = profile_dict["gaia_given_name"]
        self.gaia_id: str = profile_dict["gaia_id"]
        self.gaia_name: str = profile_dict["gaia_name"]
        self.is_considered_primary_account: bool | None = profile_dict["is_considered_primary_account"] if "is_considered_primary_account" in self.profile_dict.keys() else None
        self.name = profile_dict["name"]
        self.shortcut_name = profile_dict["shortcut_name"]
        self.user_name = profile_dict["user_name"]

        self.active_time_timedelta = dt.datetime.fromtimestamp(self.active_time).replace(microsecond=0)#chrome_time_to_datetime(self.active_time, epoch_start=dt.datetime(1970,1,1))

    def save_as_file(self, path: str, name: str = "ProfileLocalState", extension: str = "json") -> str:
        '''
        Save this profile's local state data as a file
        '''
        file_path = os.path.join(path, f"{name}.{extension}")

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.profile_dict, file)

        return file_path
    
    def __str__(self):
        text_lines = [colored_text(f"• {self.name}", color.LIGHTMAGENTA_EX),
                      self.user_name,
                      f"Given name: {self.gaia_given_name}",
                      f"Name: {self.gaia_name}",
                      f"Active time: {self.active_time_timedelta}"]
        return "\n".join(text_lines)
    
    @classmethod
    def load_from_file(cls, path: str, profile_name: str | None = None) -> "Profile":
        return cls(load_json(path), profile_name)

    
class LocalStateSession:
    def __init__(self, local_state_dict: dict):
        self.local_state_dict = local_state_dict
        self.profiles: list[Profile] = self.get_profiles()

    def get_profiles_names(self) -> list[str]:
        return self.local_state_dict ["profile"] ["profiles_order"]

    def get_profile_dict(self, profile_name: str = "Default") -> dict:
        return self.local_state_dict ["profile"] ["info_cache"] [profile_name]
    
    def get_profile(self, profile_name: str = "Default") -> Profile:
        return Profile(self.get_profile_dict(profile_name), profile_name)
    
    def get_profiles_dict(self, profile_names: list[str] | None = None) -> dict[str, Profile]:
        profile_names = profile_names if profile_names else self.get_profiles_names()
        profiles = {name: self.get_profile(name) for name in profile_names}
        return profiles
    
    def get_profiles(self, profile_names: list[str] | None = None) -> list[Profile]:
        profile_names = profile_names if profile_names else self.get_profiles_names()
        profiles = [self.get_profile(name) for name in profile_names]
        return profiles

def create_local_state_session(local_state_json_path: str):
    local_state_dict = load_json(local_state_json_path)
    return LocalStateSession(local_state_dict)

if __name__ == "__main__":
    local_state = create_local_state_session("Local State.json")
    profiles = local_state.profiles

    print(*profiles, sep="\n\n")

