from typing import Optional
from pywinauto import Application
from config import SUPPORTED_BROWSERS
from pywinauto.application import WindowSpecification

class BrowserInteractor:
    def __init__(self):
        self.app = Application(backend="uia")
        self.base_url = "geoguessr.com/"
    
    def _connect_to_browser(self, browser_name: str) -> bool:
        try:
            self.app.connect(title_re=f".*{browser_name}.*")
            return True
        except:
            print(f"There is no {browser_name} browser open.")
            return False

    def _get_url(self, browser_window: WindowSpecification) -> Optional[str]:
        edit_controls = browser_window.descendants(control_type="Edit")
        for control in edit_controls:
            try:
                value = control.get_value()
                if isinstance(value, str) and self.base_url in value:
                    return value
            except: continue
        return None

    def _get_game_id_from_url(self, url: str) -> Optional[str]:
        if url is None: return None
        game_id = url.split("/")[-1].split("?")[0]
        return game_id

    def get_game_id(self) -> Optional[str]:
        for browser_name in SUPPORTED_BROWSERS:
            is_connected = self._connect_to_browser(browser_name)
            if is_connected: break
        
        browser_window = self.app.top_window()

        url = self._get_url(browser_window)
        if url is None:
            print("No supported browser found or unable to extract URL.")
            return None
        
        game_id = self._get_game_id_from_url(url)

        if game_id is None:
            print("Unable to extract game ID from URL.")
            return None
        
        return game_id