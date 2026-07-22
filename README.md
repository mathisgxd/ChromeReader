# ChromeReader

![ChromeReader Logo](assets/logo.png)

This package provides access to local Chrome profiles data, including browsing history, bookmarks, and saved login data.

## Usage

### Save Chrome profiles for later use
#### Closing the browser beforehand is recommended

```python
from ChromeReader import Profiler

profiler = Profiler() # Uses default Chrome User Data path
profiler.save_profiles("profiles")
```

### Load saved profiles

```python
from ChromeReader import Profiler

profiler = Profiler.load_profiles("Profiles")

# Get first profile (Default)
profile = profiler.profiles[0]
print(profile, "\n")
# Print the last 10 visited urls from its history
print(*profile.history.get_recent_urls(10), sep="\n\n")
```

### Load and visualize a saved profile
#### Profiles can be displayed using the built-in GUI

```python
from ChromeReader import Profile, ChromeReaderApp

profile = Profile.load(path="profiles\Default")
app = ChromeReaderApp(profile) # CTk app to visualize a profile
app.mainloop()
```


## Installing

```
pip install ChromeReader
```