def set_session(page, key, value):
    """Sets a session value using the best available method for the environment."""
    try:
        # Standard Flet (Antigravity)
        page.session.set(key, value)
    except:
        try:
            # Built app environment
            page.session[key] = value
        except: pass

def get_session(page, key):
    """Gets a session value using the best available method for the environment."""
    try:
        # Standard Flet (Antigravity)
        return page.session.get(key)
    except:
        try:
            # Built app environment
            return page.session[key]
        except: return None
