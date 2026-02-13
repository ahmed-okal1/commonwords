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
    
    # Global Error Display
    def show_error(message):
        page.views.clear()
        page.views.append(ft.View(
            "/error",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=50),
                        ft.Text("Startup Error", size=30, weight="bold", color="red"),
                        ft.Text(message, color="white", selectable=True, text_align="center"),
                        ft.ElevatedButton("Retry", on_click=lambda _: page.go("/"))
                    ], horizontal_alignment="center", spacing=20),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
        ))
        page.update()

    try:
        init_db()
        seed_data()
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n\n{traceback.format_exc()}"
        show_error(error_details)
        return

    def route_change(route):
        try:
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
        except Exception as e:
            show_error(str(e))

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Check for persistent login
    try:
        last_username = page.client_storage.get("last_username")
        if last_username:
            page.session.set("username", last_username)
            page.go("/dashboard")
        else:
            page.go("/")
    except Exception as e:
        show_error(f"Storage Error: {str(e)}")

if __name__ == "__main__":
    ft.app(target=main)
