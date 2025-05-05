from typing import Optional
from pywinauto import Application
from pywinauto.application import WindowSpecification

SUPPORTED_BROWSERS = ["Chrome", "Firefox", "Edge", "Opera"]

class BrowserInteractor:
    def __init__(self):
        self.app = Application(backend="uia")
        self.base_url = "geoguessr.com/"
    
    def connect_to_browser(self, browser_name: str) -> bool:
        try:
            self.app.connect(title_re=f".*{browser_name}.*")
            return True
        except:
            print(f"There is no {browser_name} browser open.")
            return False

    def get_url(self, browser_window: WindowSpecification) -> Optional[str]:
        edit_controls = browser_window.descendants(control_type="Edit")
        for control in edit_controls:
            try:
                value = control.get_value()
                if isinstance(value, str) and self.base_url in value:
                    return value
            except: continue
        return None

    def extract_game_token_from_url(self, url: str) -> Optional[str]:
        if url is None: return None
        game_token = url.split("/")[-1].split("?")[0]
        return game_token

    def get_game_token(self) -> Optional[str]:
        for browser_name in SUPPORTED_BROWSERS:
            is_connected = self.connect_to_browser(browser_name)
            if is_connected: break
        
        browser_window = self.app.top_window()

        url = self.get_url(browser_window)
        if url is None:
            print("No supported browser found or unable to extract URL.")
            return None
        
        game_token = self.extract_game_token_from_url(url)

        if game_token is None:
            print("Unable to extract game ID from URL.")
            return None
        
        return game_token