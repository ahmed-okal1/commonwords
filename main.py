import flet as ft
import os
import sys
import traceback

def main(page: ft.Page):
    page.title = "English Mastery"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    
    # 1. Immediate Loading View
    loading_view = ft.View(
        "/loading",
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text("Starting English Mastery...", color="white")
                ], horizontal_alignment="center", spacing=20),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )
    page.views.append(loading_view)
    page.update()

    # 2. Setup Logging to File (to see errors if screen stays blank)
    from database import get_db_path
    log_path = get_db_path().replace(".db", "_log.txt")
    
    def log(msg):
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{msg}\n")
        except: pass

    log("--- App Startup ---")

    def show_error(message):
        log(f"ERROR: {message}")
        page.views.clear()
        page.views.append(ft.View(
            "/error",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=50),
                        ft.Text("Startup Error", size=24, weight="bold", color="red"),
                        ft.Text(str(message), color="white", selectable=True, text_align="center", size=12),
                        ft.ElevatedButton("Retry", on_click=lambda _: page.go("/"))
                    ], horizontal_alignment="center", spacing=20),
                    alignment=ft.alignment.center,
                    padding=20,
                    expand=True
                )
            ]
        ))
        page.update()

    # 3. Deferred Imports & Init
    try:
        log("Initializng Database...")
        from database import init_db
        init_db()
        
        log("Seeding Data...")
        from seed_data import seed_data
        seed_data()
        
        log("Loading Views...")
        from views.landing_view import LandingView
        from views.dashboard_view import DashboardView
        from views.learning_view import LearningView
        from views.words_view import WordsView
        from views.difficult_words_view import DifficultWordsView
        log("Ready.")
    except Exception as e:
        show_error(f"{e}\n{traceback.format_exc()}")
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
            show_error(f"Route Error: {e}")

    page.on_route_change = route_change
    page.on_view_pop = lambda _: [page.views.pop(), page.go(page.views[-1].route)]
    
    try:
        last_username = page.client_storage.get("last_username")
        if last_username:
            page.session.set("username", last_username)
            page.go("/dashboard")
        else:
            page.go("/")
    except Exception as e:
        log(f"Storage Error: {e}")
        page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
