import flet as ft
from views.landing_view import LandingView
from views.dashboard_view import DashboardView
from views.learning_view import LearningView
from views.words_view import WordsView
from views.difficult_words_view import DifficultWordsView
from database import init_db
from seed_data import seed_data

def main(page: ft.Page):
    page.title = "English Mastery"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    
    init_db()
    seed_data()

    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(LandingView(page))
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page))
        elif page.route == "/learn":
            page.views.append(LearningView(page))
        elif page.route == "/words":
            page.views.append(WordsView(page))
        elif page.route == "/difficult":
            page.views.append(DifficultWordsView(page))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Check for persistent login
    last_username = page.client_storage.get("last_username")
    if last_username:
        page.session.set("username", last_username)
        # We might need to ensure user exists or get ID, but for dashboard display username is enough 
        # (and views get_user checks DB anyway)
        page.go("/dashboard")
    else:
        page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
