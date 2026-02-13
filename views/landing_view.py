import flet as ft
import os
import sys
import traceback
import datetime

def LandingView(page: ft.Page):
    log_file = os.path.join(os.path.expanduser("~"), "english_mastery_debug.log")
    def log(msg):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [LANDING] {msg}\n")
        except: pass

    def login(e):
        try:
            val = username_field.value
            if not val:
                username_field.error_text = "Please enter a username"
                username_field.update()
                return
            
            log(f"Login attempt for: {val}")
            
            from database import get_user, create_user, set_last_user
            
            log("Fetching user from DB...")
            user = get_user(val)
            if not user:
                log("User not found, creating...")
                user = create_user(val)
                log(f"Created user ID: {user['id'] if user else 'NONE'}")
            else:
                log(f"Found user ID: {user['id']}")
            
            if not user:
                log("CRITICAL: User object is None after creation attempt")
                username_field.error_text = "DB Error: Could not create user"
                username_field.update()
                return

            log("Setting session session variables...")
            page.session.set("user_id", user['id'])
            page.session.set("username", user['username'])
            
            log("Saving persistence file...")
            set_last_user(user['username'])
            
            log("Navigating to /dashboard...")
            page.go("/dashboard")
            log("Navigation command sent.")
            
        except Exception as ex:
            err = f"LOGIN EVENT CRASH: {str(ex)}\n{traceback.format_exc()}"
            log(err)
            username_field.error_text = f"Error: {str(ex)[:30]}..."
            username_field.update()

    username_field = ft.TextField(
        label="Username",
        border_color="white",
        color="white",
        label_style=ft.TextStyle(color="white"),
        cursor_color="white",
        width=300,
        on_submit=login
    )

    return ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "English Mastery",
                            size=40,
                            weight=ft.FontWeight.BOLD,
                            color="white",
                            font_family="Roboto"
                        ),
                        ft.Text(
                            "Learn 6000 words in 6 levels",
                            size=16,
                            color=ft.Colors.WHITE70,
                        ),
                        ft.Container(height=40),
                        username_field,
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Start Learning",
                            on_click=login,
                            style=ft.ButtonStyle(
                                color="black",
                                bgcolor="white",
                                padding=20,
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            width=200
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                # alignment=ft.alignment.center,
                # Safe replacement for frozen apps
                alignment=ft.Alignment(0, 0),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[ft.Colors.INDIGO_900, ft.Colors.PURPLE_900],
                )
            )
        ],
        padding=0
    )
