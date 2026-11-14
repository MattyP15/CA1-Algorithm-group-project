# CA1-Algorithm-group-project
Repo for ECM3428 – Algorithms that changed the world coursework, CA1: Algorithm group project. 

setup from root:
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

to run:
       from root:
                 python main.py

## Saved routes (bookmarks)
OS Location 

| Windows | `%APPDATA%\ExeterRoutePlanner\bookmarks.json`<br>(usually `C:\Users\<username>\AppData\Roaming\ExeterRoutePlanner\`) |
| macOS | `~/Library/Application Support/ExeterRoutePlanner/bookmarks.json` |
| Linux | `$XDG_DATA_HOME/ExeterRoutePlanner/bookmarks.json`<br>(usually `~/.local/share/ExeterRoutePlanner/`) |

The folder is created the first time you save a bookmark.
To clear all bookmarks, delete `bookmarks.json`. If the file is damaged,
the app starts with an empty list instead of crashing.