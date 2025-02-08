#Configurations and constants

from streamlit_cookies_controller import CookieController

# Cookie configuration
cookie_controller = CookieController()
if cookie_controller._CookieController__cookies is None:
    cookie_controller._CookieController__cookies = {}
    