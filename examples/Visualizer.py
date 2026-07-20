import ChromeReader

import os
import sys

def get_file_folder_path():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        folder_path = os.path.dirname(os.path.abspath(file_path))
        return folder_path
    
    return None

def open_profile_folder_app(path: str = ""):
    print("loading profile...")
    profile = ChromeReader.Profile.load(path)
    app = ChromeReader.ChromeReaderApp(profile)
    
    app.mainloop()

if __name__ == "__main__":
    path = get_file_folder_path() or ""
    open_profile_folder_app(path)
    #open_profile_folder_app()