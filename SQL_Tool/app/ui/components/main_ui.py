# A small description for the code file.
# This file defines the main user interface after a successful connection.
import tkinter as tk
from tkinter import ttk
from .database_explorer import DatabaseExplorer
from .query_editor import QueryEditor
from .result_viewer import ResultViewer
from app.ui.styling.logo_handler import LogoHandler

class MainUI:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller
        self.main_frame = None
        self.status_bar = None
        self.connected_icon = None  # To hold the connected icon image

        # UI components
        self.database_explorer = None
        self.query_editor = None
        self.result_viewer = None

        # UI elements
        self.run_query_btn = None
        self.save_log_btn = None

        self.build_ui()

    def build_ui(self):
        """Build main application UI - Complete implementation from original build_main_ui"""
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg=self.app.bg_color)

        # Modern header with all buttons
        self.build_main_ui_header()

        # Main content with paned window
        paned = ttk.PanedWindow(self.main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Create left and right panels
        left_panel = ttk.Frame(paned, padding=10)
        right_panel = ttk.Frame(paned, padding=10)

        # Adjusted weights for the main horizontal panels
        paned.add(left_panel, weight=2)
        paned.add(right_panel, weight=8)

        # Build components
        self.build_database_explorer(left_panel)
        self.build_query_view(right_panel)
        
        # Status bar at the bottom
        self._build_status_bar()

    def build_main_ui_header(self):
        """Build modern header with connection status and all action buttons"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=self.app.card_bg,
            pady=15,
            highlightbackground=self.app.border_color,
            highlightthickness=1
        )
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Left side - Connection status
        self._build_connection_status(header_frame)

        # Center - Action buttons
        self._build_action_buttons(header_frame)

        # Right side - Disconnect button
        ttk.Button(
            header_frame,
            text="Disconnect",
            style='Red.TButton',
            command=self.app.disconnect_server
        ).grid(row=0, column=2, sticky="e", padx=10)

    def _build_connection_status(self, parent):
        """Build connection status display with icon and green text"""
        status_frame = tk.Frame(parent, bg=self.app.card_bg)
        status_frame.grid(row=0, column=0, sticky="w", padx=10)
        
        # Connected icon
        self.connected_icon = LogoHandler.create_connected_icon()
        status_label = tk.Label(status_frame, image=self.connected_icon, bg=self.app.card_bg)
        status_label.pack(side="left", padx=(0, 5))

        server_info = self.app.get_current_server_info()
        if server_info:
            tk.Label(
                status_frame,
                text=f"Connected to: {server_info['username']} on {server_info['server']}",
                bg=self.app.card_bg,
                fg=self.app.success_color,  # Greened
                font=self.app.font_bold
            ).pack(side="left", anchor="center")

    def _build_action_buttons(self, parent):
        """Build center action buttons with improved padding"""
        button_frame = tk.Frame(parent, bg=self.app.card_bg)
        button_frame.grid(row=0, column=1, sticky="", padx=20)

        self.run_query_btn = ttk.Button(
            button_frame,
            text="▶️ Execute Query",
            style='Accent.TButton',
            command=self._execute_query
        )
        self.run_query_btn.grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="📜 History",
            style='Modern.TButton',
            command=self.app.show_query_history
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="🧹 Clear Editor",
            style='Warning.TButton',
            command=self.clear_query_editor
        ).grid(row=0, column=2, padx=5)

        self.save_log_btn = ttk.Button(
            button_frame,
            text="💾 Export Results",
            style='Modern.TButton',
            command=self.app.save_query_log,
            state='disabled'
        )
        self.save_log_btn.grid(row=0, column=3, padx=5)

        ttk.Button(
            button_frame,
            text="🧹 Clear Results",
            style='Warning.TButton',
            command=self.clear_results
        ).grid(row=0, column=4, padx=5)

    def build_database_explorer(self, parent):
        self.database_explorer = DatabaseExplorer(parent, self.app)

    def build_query_view(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        query_pane = ttk.PanedWindow(parent, orient="vertical")
        query_pane.grid(row=0, column=0, sticky="nsew")

        self.query_editor = QueryEditor(query_pane, self.app)
        self.result_viewer = ResultViewer(query_pane, self.app)

        query_pane.add(self.query_editor.get_frame(), weight=7)
        query_pane.add(self.result_viewer.get_frame(), weight=3)

    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready.",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.app.dark_bg,
            fg='white',
            font=self.app.font_small
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _execute_query(self):
        selected_databases = self.database_explorer.get_selected_databases()
        query = self.query_editor.get_query()
        self.app.start_query_thread(selected_databases, query)

    def set_query_running_state(self, is_running):
        state = "disabled" if is_running else "normal"
        self.run_query_btn.config(state=state)
        if is_running:
            self.save_log_btn.config(state="disabled")
            self.query_editor.disable()
            self.show_status("Executing query...")
        else:
            self.query_editor.enable()
            self.show_status("Ready.")

    def enable_save_log_button(self):
        self.save_log_btn.config(state="normal")
        self.show_status("Query execution completed. You can now export the results.")

    def populate_databases(self, databases):
        if self.database_explorer:
            self.database_explorer.populate_databases(databases)

    def clear_query_editor(self):
        if self.query_editor:
            self.query_editor.clear_editor()

    def set_query_text(self, query):
        if self.query_editor:
            self.query_editor.set_query(query)

    def get_query_text(self):
        if self.query_editor:
            return self.query_editor.get_query()
        return ""

    def clear_results(self):
        if self.result_viewer:
            self.result_viewer.clear_results()
        self.show_status("Results cleared.")

    def show_status(self, status):
        if self.status_bar:
            self.status_bar.config(text=status)

    def show_error(self, error_message):
        if self.result_viewer:
            self.result_viewer.show_error(error_message)
        if self.status_bar:
            self.status_bar.config(text=f"Error: {error_message}", fg=self.app.error_color)

    def show(self):
        if self.main_frame:
            self.main_frame.pack(fill="both", expand=True)

    def hide(self):
        if self.main_frame:
            self.main_frame.pack_forget()

    def get_selected_databases(self):
        if self.database_explorer:
            return self.database_explorer.get_selected_databases()
        return []

    def has_database_selection(self):
        if self.database_explorer:
            return self.database_explorer.has_selection()
        return False

    def get_database_info(self):
        if self.database_explorer:
            return self.database_explorer.get_database_info()
        return {}

    def refresh_connection_status(self):
        self.build_ui()

    def show_execution_summary(self, summary):
        """Passes the execution summary to the result viewer."""
        if self.result_viewer:
            # CORRECT: Call the existing 'show_execution_summary' method
            self.result_viewer.show_execution_summary(summary)

    def append_result(self, result_text):
        """Passes a chunk of result text to the result viewer."""
        if self.result_viewer:
            # CORRECT: Change 'append_text' to 'append_result'
            self.result_viewer.append_result(result_text)