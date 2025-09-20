import tkinter as tk
from tkinter import messagebox
import threading
from queue import Queue, Empty
from datetime import datetime

from app.ui.components.connection_ui import ConnectionUI
from app.ui.components.main_ui import MainUI
from app.ui.styling.styles import StyleManager
from app.ui.styling.logo_handler import LogoHandler
from app.database.connection import DatabaseManager
from app.database.query_executor import QueryExecutor
from app.utils.query_history import QueryHistoryManager
from app.utils.file_operations import FileOperationsManager
from app.utils.validators import QueryValidator
from app.core.config import AppConfig
# FIX 1: Import BOTH save and load functions
from app.utils.config_manager import save_credentials, load_credentials

class SQLToolApp:
    def __init__(self, root):
        self.root = root

        # runtime state
        self.conn = None
        self.current_server = None
        self.current_db = None
        self.current_server = None # This will now store the whole config dict
        self.db_vars = {}
        self.db_checkbuttons = {}
        self.message_queue = Queue()
        self.query_history = []
        self.query_running = False
        self.current_query = None

        self.setup_application()
        self.initialize_managers()
        self.initialize_ui()
        self.check_queue()  # start polling

    def setup_application(self):
        """Window setup for login screen (windowed, not fullscreen)."""
        self.root.title("Zanvar's SQL Tool")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)

        # style references from config
        self.bg_color = AppConfig.COLORS['bg_color']
        self.primary_color = AppConfig.COLORS['primary_color']
        self.muted_color = AppConfig.COLORS['muted_color']
        self.success_color = AppConfig.COLORS['success_color']
        self.accent_color = AppConfig.COLORS['accent_color']
        self.border_color = AppConfig.COLORS['border_color']
        self.card_bg = AppConfig.COLORS['card_bg']
        self.light_gray = AppConfig.COLORS['light_gray']
        self.dark_bg = AppConfig.COLORS['dark_bg']
        self.error_color = AppConfig.COLORS['error_color']
        self.warning_color = AppConfig.COLORS['warning_color']

        # fonts
        self.font_normal = AppConfig.FONTS['normal']
        self.font_bold = AppConfig.FONTS['bold']
        self.font_label = AppConfig.FONTS['label']
        self.font_header = AppConfig.FONTS['header']
        self.font_database = AppConfig.FONTS['database']
        self.font_subtitle = AppConfig.FONTS['subtitle']
        self.font_small = AppConfig.FONTS['small']

        # logo and bg
        self.logo_image = LogoHandler.create_logo_placeholder()
        self.root.configure(bg=self.bg_color)

    def initialize_managers(self):
        """Initialize all manager classes."""
        self.style_manager = StyleManager(self.root, self)
        self.db_manager = DatabaseManager()
        self.history_manager = QueryHistoryManager()
        self.query_executor = QueryExecutor(self.db_manager, self.message_queue)
        self.file_manager = FileOperationsManager()

    def initialize_ui(self):
        """Create UI components."""
        self.connection_ui = ConnectionUI(self.root, self)
        self.main_ui = MainUI(self.root, self)
        self.main_ui.hide()
        self.connection_ui.show()

    # ------------- Connection -------------
    def connect_to_server(self,db_type, server, username, password):
        # FIX 2: Move validation BEFORE saving credentials
        if not server.strip():
            messagebox.showwarning("Input Error", "Server is required")
            return
        if not username.strip():
            messagebox.showwarning("Input Error", "Username is required")
            return
            
        # Now it's safe to save
        save_credentials(server, username)

        # self.db_manager.set_server_config(db_type,server, username, password)
        self.db_manager.set_config(db_type, server, username, password)

        # self.current_server = self.db_manager.current_config
        self.current_server = self.db_manager.current_config

        threading.Thread(target=self.attempt_connection, daemon=True).start()

    def attempt_connection(self):
        ok, message = self.db_manager.test_connection()
        if ok:
            self.message_queue.put(("success", message))
        else:
            self.message_queue.put(("error", f"Connection failed: {message}"))

    def disconnect_server(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None

        self.current_server = None
        self.db_vars = {}

        # back to login window sizing
        self.main_ui.hide()
        self.root.attributes('-fullscreen', False)
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.connection_ui.show()

    # ------------- Query execution -------------
    def start_query_thread(self, selected_databases, query):
        if self.query_running:
            messagebox.showwarning("Wait", "Query already running")
            return
        if not selected_databases:
            messagebox.showwarning("Selection Error", "Select at least one database.")
            return
        if not query.strip():
            messagebox.showwarning("Input Error", "Enter a SQL query.")
            return

        if QueryValidator.contains_dangerous_sql(query):
            confirm = messagebox.askyesno(
                "Confirm Destructive Query",
                "⚠️ This query may modify or delete data.\n\nDo you want to proceed?"
            )
            if not confirm:
                return

        # record for logging
        self.current_query = {
            'query': query,
            'databases': selected_databases,
            'start_time': datetime.now(),
            'results': []  # will be filled after execution
        }

        # add to history
        self.history_manager.add_query(query)

        # UI state and launch
        self.query_running = True
        self.main_ui.set_query_running_state(True)
        self.main_ui.clear_results()
        self.main_ui.show_status("Executing query...")

        threading.Thread(
            target=self._execute_query_thread,
            args=(selected_databases, query),
            daemon=True
        ).start()

    def _execute_query_thread(self, databases, query):
        """Run the query and collect structured results for saving."""
        try:
            result = self.query_executor.execute_query(databases, query)
            # Merge aggregate metrics
            self.current_query.update(result)

            # Flatten per-database structured results into current_query["results"]
            flat = []
            for db_info in result.get("databases_info", []):
                for item in db_info.get("results_struct", []):
                    flat.append(item)
            if flat:
                self.current_query["results"] = flat

            self.message_queue.put(("done", "Query execution completed"))
            self.message_queue.put(("enable_log_button", True))
        except Exception as e:
            self.message_queue.put(("error", f"Query execution failed: {str(e)}"))
            self.message_queue.put(("done", "Query execution failed"))

    # ------------- File operations -------------
    def save_query_log(self):
        """Save current query + results; shows Save dialog and writes .log."""
        if not self.current_query or not self.current_query.get("results"):
            messagebox.showwarning("Nothing to save", "Run a query first")
            return
        ok, msg = self.file_manager.save_query_log(self.current_query, self.current_server)
        (messagebox.showinfo if ok else messagebox.showerror)("Save Log", msg)

    # ------------- History -------------
    def show_query_history(self):
        from app.ui.dialogs.history_dialog import HistoryDialog
        HistoryDialog(self.root, self).show_history()

    def load_query_from_history(self, query):
        self.main_ui.set_query_text(query)

    # ------------- Queue processing -------------
    def check_queue(self):
        """Process UI messages from worker threads."""
        try:
            while True:
                typ, payload = self.message_queue.get_nowait()

                if typ == "enable_log_button":
                    self.main_ui.enable_save_log_button()
                elif typ == "success":
                    self.handle_success_message(payload)
                elif typ == "error":
                    self.handle_error_message(payload)
                elif typ == "execution_summary":
                    self.main_ui.show_execution_summary(payload)
                elif typ == "result":
                    self.main_ui.append_result(payload)
                elif typ == "status":
                    self.main_ui.show_status(payload)
                elif typ == "done":
                    self.query_running = False
                    self.main_ui.set_query_running_state(False)
        except Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def handle_success_message(self, msg):
        """On successful connection, update connection UI then switch."""
        self.connection_ui.show_success(msg)
        self.root.after(800, self._switch_to_main_ui)

    def handle_error_message(self, msg):
        if self.query_running:
            self.main_ui.show_error(msg)
        else:
            self.connection_ui.show_error(msg)


    def _switch_to_main_ui(self):
        """Switch to main UI with maximized window (not fullscreen)."""
        try:
            databases = self.db_manager.get_databases()
            self.connection_ui.hide()

            # maximize but not fullscreen
            self.root.geometry("")
            self.root.state('zoomed')
            self.root.attributes('-fullscreen', False)
            self.root.resizable(True, True)

            # 1. First, REBUILD/REFRESH the main UI structure.
            if hasattr(self.main_ui, "refresh_connection_status"):
                self.main_ui.refresh_connection_status()
                
            # 2. THEN, POPULATE the newly created UI with the database list.
            self.main_ui.populate_databases(databases)
            
            self.main_ui.show()
        except Exception as e:
            self.handle_error_message(f"Failed to load databases: {str(e)}")
            
    # ------------- Lifecycle -------------
    def on_close(self):
        self.history_manager.save_history()
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        self.root.destroy()

    # ------------- Utilities -------------
    def get_current_server_info(self):
        if self.current_server:
            return {
                'server': self.current_server['server'],
                'username': self.current_server['username'],
                'db_type': self.current_server.get('db_type')
            }
        return None

    def get_query_history(self):
        return self.history_manager.get_history()

    def clear_query_editor(self):
        self.main_ui.clear_query_editor()

    def clear_results(self):
        self.main_ui.clear_results()