from ChromeReader import Profiler

profiler = Profiler() # Uses default User Data path

# Get first profile (Default)
profile = profiler.profiles[0]
print(profile, "\n") # Prints basic profile info

# Get last 10 visited urls from its history
hist_urls = profile.history.get_recent_urls(10)
print(*hist_urls, sep="\n\n")