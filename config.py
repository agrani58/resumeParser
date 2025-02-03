from streamlit_cookies_controller import CookieController

# Cookie configuration
cookie_controller = CookieController()
if not hasattr(cookie_controller, '_CookieController__cookies') is None:
    cookie_controller._CookieController__cookies = {}