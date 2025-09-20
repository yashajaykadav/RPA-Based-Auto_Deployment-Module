import tkinter as tk
from tkinter import scrolledtext

class ResultViewer:
    def __init__(self, parent, app_controller):
        self.parent = parent
        self.app = app_controller
        self.result_text = None
        self.result_viewer_frame = None
        self.build_viewer()

    def build_viewer(self):
        """Build result viewer with dark theme from original code"""
        # Result viewer frame with dark theme - Made smaller
        self.result_viewer_frame = tk.Frame(
            self.parent, 
            bg=self.app.card_bg, 
            relief="solid", 
            bd=1,
            highlightbackground=self.app.border_color, 
            highlightthickness=1
        )
        
        result_viewer_container = tk.Frame(
            self.result_viewer_frame, 
            bg=self.app.card_bg, 
            padx=12, 
            pady=12
        )
        result_viewer_container.pack(fill="both", expand=True)
        
        # Results header with dark theme
        results_header = tk.Frame(
            result_viewer_container, 
            bg=self.app.dark_bg, 
            relief="solid", 
            bd=1
        )
        results_header.pack(fill="x", pady=(0, 8))
        
        results_title = tk.Label(
            results_header,
            text="📊 Query Results & Output Console",
            font=('Segoe UI', 11, 'bold'),
            bg=self.app.dark_bg,
            fg="white",
            pady=8
        )
        results_title.pack(anchor="w", padx=12)
        
        # Result text area with dark theme
        self.result_text = scrolledtext.ScrolledText(
            result_viewer_container, 
            wrap=tk.NONE, 
            height=10,  # Reduced height
            font=('Consolas', 11),
            bg="#1e1e1e",
            fg="#ffffff",
            selectbackground="#264f78",
            selectforeground="white",
            relief="solid",
            bd=1,
            highlightbackground=self.app.border_color,
            highlightthickness=1,
            state="disabled",
            padx=8,
            pady=8
        )
        self.result_text.pack(fill="both", expand=True)

    def clear_results(self):
        """Clear the results text area"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")

    def append_result(self, result):
        """Append result to display"""
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, result)
        self.result_text.config(state="disabled")
        # Auto-scroll to bottom to show latest results
        self.result_text.see(tk.END)

    def show_execution_summary(self, summary):
        """Display the detailed execution summary at the top (from original)"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)  # Clear previous content
        self.result_text.insert(tk.END, summary + "\n")
        self.result_text.config(state="disabled")
        self.result_text.see("1.0")  # Scroll to top to show summary

    def show_status(self, status_message):
        """Show status message in results area"""
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, f"{status_message}\n")
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

    def show_error(self, error_message):
        """Show error message in results area"""
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, f"ERROR: {error_message}\n")
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

    def get_frame(self):
        """Return the main frame for packing"""
        return self.result_viewer_frame

    def is_empty(self):
        """Check if result viewer is empty"""
        content = self.result_text.get("1.0", tk.END).strip()
        return len(content) == 0
