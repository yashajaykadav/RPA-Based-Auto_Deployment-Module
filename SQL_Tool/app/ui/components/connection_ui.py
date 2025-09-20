import tkinter as tk
from tkinter import ttk, messagebox
import threading
from app.utils.config_manager import load_credentials

class ConnectionUI:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller
        self.conn_frame = None
        
        # UI elements
        self.server_entry = None
        self.username_entry = None
        self.password_entry = None
        self.connect_button = None
        self.progress = None
        self.status_label = None
        self.db_type_var = None
        self.db_type_selector = None
        
        self.build_ui()

    def build_ui(self):
        """Build connection UI with improved layout and accessibility"""
        if hasattr(self, 'conn_frame') and self.conn_frame:
            self.conn_frame.destroy()

        self.conn_frame = tk.Frame(self.root, bg=self.app.bg_color)
        
        # Card frame with enhanced shadow and rounded corners
        card_frame = tk.Frame(
            self.conn_frame, 
            bg=self.app.card_bg, 
            bd=0,
            highlightbackground="#d0d0d0", 
            highlightthickness=2,
            relief="flat",
            padx=40, 
            pady=40
        )
        card_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Add subtle shadow effect
        card_frame.configure(highlightbackground="#e0e0e0", highlightcolor="#e0e0e0")
        
        # Logo and title section
        self._build_logo_section(card_frame)
        
        # Input fields section
        self._build_input_fields(card_frame)
        
        # Buttons section
        self._build_buttons(card_frame)
        
        # Progress and status section
        self._build_progress_status(card_frame)

    def _build_logo_section(self, parent):
        """Build logo and title section with improved typography"""
        logo_frame = tk.Frame(parent, bg=self.app.card_bg)
        logo_frame.pack(fill="x", pady=(0, 20))
        
        # Logo image with scaling
        if self.app.logo_image:
            logo_label = tk.Label(logo_frame, image=self.app.logo_image, bg=self.app.card_bg)
            logo_label.pack(pady=(0, 15))
        
        # Company title with modern font
        tk.Label(
            logo_frame, 
            text="Zanvar Group of Industries", 
            font=('Helvetica', 20, 'bold'),
            bg=self.app.card_bg, 
            fg=self.app.primary_color
        ).pack()
        
        # Subtitle with better contrast
        tk.Label(
            logo_frame, 
            text="Connect to your database", 
            font=('Helvetica', 13),
            bg=self.app.card_bg, 
            fg=self.app.muted_color
        ).pack(pady=(5, 15))

    def _build_input_fields(self, parent):
        """Build input fields with improved spacing and accessibility"""
        input_frame = tk.Frame(parent, bg=self.app.card_bg)
        input_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(
            input_frame, 
            text="Database Type:", 
            style='Header.TLabel',
            font=self.app.font_label
        ).grid(row=0, column=0, sticky="w", padx=(5, 15), pady=10)

        self.db_type_var = tk.StringVar(value="SQL Server")
        self.db_type_selector = ttk.Combobox(
            input_frame,
            textvariable=self.db_type_var,
            values=["SQL Server", "PostgreSQL", "MySQL"],  # Added MySQL option
            state="readonly",
            width=33,
            font=self.app.font_normal
        )
        self.db_type_selector.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        server_default, username_default = load_credentials()
        fields = [
            ("Server:", "server_entry", server_default or "localhost\\SQLEXPRESS"),
            ("Username:", "username_entry", username_default or "sa"),
            ("Password:", "password_entry", "")
        ]

        for i, (label_text, attr_name, default) in enumerate(fields, 1):
            ttk.Label(
                input_frame, 
                text=label_text, 
                style='Header.TLabel',
                font=self.app.font_label
            ).grid(row=i, column=0, sticky="w", padx=(5, 15), pady=10)
            
            entry = ttk.Entry(
                input_frame, 
                width=35, 
                font=self.app.font_normal
            )
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=10)
            setattr(self, attr_name, entry)
            
            if "password" in attr_name:
                entry.config(show="•")
                # Add show/hide password toggle
                toggle_btn = ttk.Checkbutton(
                    input_frame,
                    text="Show",
                    command=lambda: self._toggle_password_visibility(),
                    style='Toggle.TCheckbutton'
                )
                toggle_btn.grid(row=i, column=2, padx=(5, 0), pady=10)
                
        input_frame.grid_columnconfigure(1, weight=1)

    def _toggle_password_visibility(self):
        """Toggle password visibility"""
        current_show = self.password_entry.cget("show")
        self.password_entry.config(show="" if current_show == "•" else "•")

    def _build_buttons(self, parent):
        """Build buttons with improved spacing and hover effects"""
        button_frame = tk.Frame(parent, bg=self.app.card_bg)
        button_frame.pack(fill="x", pady=(25, 10))
        
        # Connect button with wider padding
        self.connect_button = ttk.Button(
            button_frame, 
            text="Connect", 
            style='Accent.TButton',
            command=self.connect_to_server
        )
        self.connect_button.pack(side="left", padx=(0, 15), pady=5, fill="x", expand=True)
        
        # Exit button
        ttk.Button(
            button_frame, 
            text="Exit", 
            style='Warning.TButton',
            command=self.root.quit
        ).pack(side="right", pady=5, fill="x", expand=True)

    def _build_progress_status(self, parent):
        """Build progress bar and status label with better alignment"""
        progress_container = tk.Frame(parent, bg=self.app.card_bg, height=60)
        progress_container.pack(fill="x", pady=(15, 0))
        progress_container.pack_propagate(False)
        
        self.progress = ttk.Progressbar(
            progress_container, 
            orient="horizontal", 
            length=300, 
            mode="indeterminate", 
            style='Custom.Horizontal.TProgressbar'
        )
        
        self.status_label = tk.Label(
            progress_container, 
            text="Not connected", 
            fg=self.app.muted_color, 
            bg=self.app.card_bg, 
            font=self.app.font_bold,
            height=2
        )
        self.status_label.pack(side="bottom", fill="x", pady=(10, 0))

    def connect_to_server(self):
        """Handle server connection with input validation"""
        db_type = self.db_type_var.get()
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not server:
            messagebox.showwarning("Input Error", "Server is required")
            return
        if not username:
            messagebox.showwarning("Input Error", "Username is required")
            return
        
        self.connect_button.config(state="disabled")
        self.progress.pack(pady=(15, 0), fill="x")
        self.progress.start()
        self.status_label.config(text="Connecting...", fg=self.app.accent_color)
        
        # Run connection in separate thread to prevent UI freeze
        threading.Thread(
            target=self.app.connect_to_server,
            args=(db_type, server, username, password),
            daemon=True
        ).start()

    def show_success(self, message):
        """Handle successful connection message"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text=message, fg=self.app.success_color)
        self.connect_button.config(state="normal")

    def show_error(self, message):
        """Handle error messages"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text=message, fg=self.app.error_color)
        self.connect_button.config(state="normal")

    def show(self):
        """Show connection UI"""
        if self.conn_frame:
            self.conn_frame.pack(expand=True, fill="both")

    def hide(self):
        """Hide connection UI"""
        if self.conn_frame:
            self.conn_frame.pack_forget()

    def reset_form(self):
        """Reset the connection form to default values"""
        self.server_entry.delete(0, tk.END)
        self.server_entry.insert(0, "localhost\\SQLEXPRESS")
        
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, "sa")
        
        self.password_entry.delete(0, tk.END)
        
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Not connected", fg=self.app.muted_color)
        self.connect_button.config(state="normal")

    def get_connection_details(self):
        """Get current connection form values"""
        return {
            'db_type': self.db_type_var.get(),
            'server': self.server_entry.get().strip(),
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get()
        }

    def set_connection_details(self, server="", username="", password=""):
        """Set connection form values"""
        self.server_entry.delete(0, tk.END)
        self.server_entry.insert(0, server)
        
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def enable_form(self, enabled=True):
        """Enable or disable the connection form"""
        state = "normal" if enabled else "disabled"
        self.server_entry.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        self.connect_button.config(state=state)
        self.db_type_selector.config(state=state)

    def bind_enter_key(self):
        """Bind Enter key to connect button"""
        self.server_entry.bind('<Return>', lambda e: self.connect_to_server())
        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())
        self.password_entry.bind('<Return>', lambda e: self.connect_to_server())
        self.db_type_selector.bind('<Return>', lambda e: self.connect_to_server())