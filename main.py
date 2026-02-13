import flet as ft
import os
import sys
import traceback
import datetime

def main(page: ft.Page):
    # Setup log file in user's home directory (always writable)
    log_file = os.path.join(os.path.expanduser("~"), "english_mastery_debug.log")
    
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
        say("Loading database logic...")
        import database
        log("Database module imported.")
        
        say("Detecting database path...")
        db_path = database.get_db_path()
        log(f"Database path determined: {db_path}")
        
        say("Initializing database file...")
        database.init_db()
        log("Database initialized (tables created).")
        
        # Step 2: Seeding
        say("Verifying vocabulary data...")
        from seed_data import seed_data
        log("Seed data module imported.")
        seed_data()
        log("Seed data verification/insertion complete.")
        
        # Step 3: Views
        say("Loading application views...")
        from views.landing_view import LandingView
        from views.dashboard_view import DashboardView
        from views.learning_view import LearningView
        from views.words_view import WordsView
        from views.difficult_words_view import DifficultWordsView
        log("All views imported successfully.")
        
        say("Preparing to launch UI...")
        import time
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
        from database import get_last_user
        last_user = get_last_user()
        
        if last_user:
            log(f"Auto-login detected for: {last_user}")
            page.session.set("username", last_user)
            page.go("/dashboard")
            log("Dispatched to dashboard.")
        else:
            log("No auto-login found. Dispatching to landing.")
            page.views.clear()
            page.views.append(LandingView(page))
            page.update()
            log("Initial view (Landing) loaded.")
        
    except Exception as e:
        log(f"Auto-login or View load failed: {e}")
        page.views.clear()
        page.add(ft.Text(f"Failed to load UI: {e}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
