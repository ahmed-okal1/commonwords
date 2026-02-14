import flet as ft
import os
import sys
import traceback
import datetime
import time

# Explicit imports to help Flet build process discovery
from flet import Audio, FilePicker, View, Page

# Import views at the top level so static analyzer sees them
from views.landing_view import LandingView
from views.dashboard_view import DashboardView
from views.learning_view import LearningView
from views.words_view import WordsView
from views.difficult_words_view import DifficultWordsView
import database
from seed_data import seed_data
from session_utils import set_session, get_session
from database import get_last_user

def main(page: Page):
    # Setup log file in user's home directory (always writable)
    log_file = os.path.join(os.path.expanduser("~"), "english_mastery_debug.log")
    
    # Pre-add dummy controls to overlay to ensure plugins are included in the build
    page.overlay.append(Audio(src="dummy.mp3"))
    page.overlay.append(FilePicker())

    def log(msg):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {msg}\n")
        except: pass

    log("\n--- STARTUP INITIALIZED ---")

    # Resilient UI Setup
    page.title = "Mastery Boot"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    
    diag_text = ft.Text("Booting...", size=14, color="white70")
    page.add(
        ft.Text("English Mastery", size=24, weight="bold"),
        ft.Divider(),
        diag_text,
        ft.ProgressBar(width=300, color="blue")
    )
    
    def say(msg):
        log(f"STATUS: {msg}")
        diag_text.value = msg
        page.update()

    try:
        log(f"Platform: {sys.platform} | Version: {sys.version.split()[0]}")
        log(f"Executable: {sys.executable}")
        
        # Step 1: Database Logic
        say("Loading database...")
        db_path = database.get_db_path()
        log(f"Database path: {db_path}")
        database.init_db()
        log("Database initialized.")
        
        # Step 2: Seeding
        say("Verifying data...")
        seed_data()
        log("Seed data complete.")
        
        # Step 3: Launch
        say("Launching UI...")
        time.sleep(0.5)
        
        # Handoff to main App UI
        page.controls.clear()
        page.padding = 0
        page.update()
        log("Diagnostic UI cleared. Launching router.")

    except Exception as e:
        error_msg = f"BOOT CRASH: {str(e)}\n\n{traceback.format_exc()}"
        log(error_msg)
        page.add(ft.Text("Critical Error during boot:", color="red", weight="bold"))
        page.add(ft.Text(error_msg, size=10, selectable=True))
        page.update()
        return

    # Routing Logic
    def route_change(route):
        try:
            log(f"Route change to: {page.route}")
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
        except Exception as ex:
            log(f"ROUTE ERROR: {ex}")

    page.on_route_change = route_change
    page.on_view_pop = lambda _: [page.views.pop(), page.go(page.views[-1].route)]
    
    # Final step: Choose starting page
    try:
        last_user = get_last_user()
        if last_user:
            log(f"Auto-login: {last_user}")
            set_session(page, "username", last_user)
            page.go("/dashboard")
        else:
            log("No auto-login. Landing.")
            page.views.clear()
            page.views.append(LandingView(page))
            page.update()
        
    except Exception as e:
        log(f"UI load failed: {e}")
        page.views.clear()
        page.add(ft.Text(f"Failed to load UI: {e}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
