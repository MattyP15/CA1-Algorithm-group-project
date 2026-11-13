import sys
from pathlib import Path

import webview

from gui.api import Api

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
UI_FILE = ROOT / "ui" / "index.html"

#Will turn this off for final .exe
DEBUG = True    

def main():
    webview.create_window(
        title="Exeter Route Planner",
        url=str(UI_FILE),
        js_api=Api(), #APi callable from Javascript
        width=1280,
        height=820,
        min_size=(900, 600),
        background_color= "#0f1216",
    
    )
    webview.start(debug=DEBUG,)


if __name__ == "__main__":
    main()