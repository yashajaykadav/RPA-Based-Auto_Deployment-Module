from tkinter import ttk
from app.core.config import AppConfig

class StyleManager:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller
        self.style = None
        self.setup_colors()
        self.setup_fonts()
        self.setup_styles()

    def setup_colors(self):
        """Define color scheme from AppConfig"""
        self.colors = AppConfig.COLORS
        self.root.configure(bg=self.colors['bg_color'])

    def setup_fonts(self):
        """Define font scheme from AppConfig"""
        self.fonts = AppConfig.FONTS

    def setup_styles(self):
        """Configure TTK styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self._setup_button_styles()
        self._setup_label_styles()
        self._setup_progressbar_styles()
        self._setup_treeview_styles()
        self._setup_notebook_styles()
        self._setup_panedwindow_styles()
        self._setup_frame_styles()

    def _setup_button_styles(self):
        """Setup all button styles"""
        self.style.configure('Accent.TButton',
                            foreground='white',
                            background=self.colors['accent_color'],
                            font=self.fonts['normal'],
                            padding=(12, 8),
                            borderwidth=0,
                            relief='flat')
        self.style.map('Accent.TButton',
                       background=[('active', self.colors['accent_color'])],
                       foreground=[('active', 'white')])

        self.style.configure('Modern.TButton',
                            foreground=self.colors['primary_color'],
                            background=self.colors['card_bg'],
                            font=self.fonts['normal'],
                            padding=(12, 8),
                            borderwidth=0,
                            relief='flat')
        self.style.map('Modern.TButton',
                       background=[('active', self.colors['light_gray'])],
                       foreground=[('active', self.colors['primary_color'])])

        self.style.configure('Warning.TButton',
                            foreground='white',
                            background=self.colors['warning_color'],
                            font=self.fonts['normal'],
                            padding=(12, 8),
                            borderwidth=0,
                            relief='flat')
        self.style.map('Warning.TButton',
                       background=[('active', self.colors['warning_color'])],
                       foreground=[('active', 'white')])

        self.style.configure('Red.TButton',
                            foreground='white',
                            background=self.colors['error_color'],
                            font=self.fonts['bold'],
                            padding=(12, 8),
                            borderwidth=0,
                            relief='flat')
        self.style.map('Red.TButton',
                       background=[('active', self.colors['error_color'])],
                       foreground=[('active', 'white')])

    def _setup_label_styles(self):
        """Setup label styles"""
        self.style.configure('Header.TLabel',
                            background=self.colors['card_bg'],
                            foreground=self.colors['muted_color'],
                            font=self.fonts['normal'])

        self.style.configure('Header.Bold.TLabel',
                            background=self.colors['card_bg'],
                            foreground=self.colors['primary_color'],
                            font=self.fonts['bold'])

        self.style.configure('Section.TLabel',
                            background=self.colors['bg_color'],
                            foreground=self.colors['primary_color'],
                            font=self.fonts['header'])

    def _setup_progressbar_styles(self):
        """Setup progressbar styles"""
        self.style.configure('Custom.Horizontal.TProgressbar',
                            troughcolor=self.colors['light_gray'],
                            background=self.colors['accent_color'],
                            borderwidth=0)

    def _setup_treeview_styles(self):
        """Setup treeview styles"""
        self.style.configure("Treeview.Heading",
                            font=self.fonts['bold'],
                            background=self.colors['card_bg'],
                            foreground=self.colors['primary_color'],
                            padding=(5, 5))
        self.style.configure("Treeview",
                            font=self.fonts['normal'],
                            rowheight=25,
                            background=self.colors['card_bg'],
                            foreground=self.colors['primary_color'])
        self.style.map('Treeview',
                       background=[('selected', self.colors['accent_color'])],
                       foreground=[('selected', 'white')])

    def _setup_notebook_styles(self):
        self.style.configure("TNotebook", background=self.colors['bg_color'], borderwidth=0, relief='flat')
        self.style.configure("TNotebook.Tab", background=self.colors['dark_bg'], foreground=self.colors['light_gray'], borderwidth=0, padding=(10, 5))
        self.style.map("TNotebook.Tab", background=[('selected', self.colors['card_bg'])], foreground=[('selected', self.colors['primary_color'])])
        self.style.configure("TNotebook.Tab.border", background=self.colors['bg_color'])

    def _setup_panedwindow_styles(self):
        self.style.configure("TPanedwindow", background=self.colors['bg_color'], borderwidth=0)

    def _setup_frame_styles(self):
        self.style.configure("TFrame", background=self.colors['bg_color'], borderwidth=0)
        self.style.configure("Card.TFrame", background=self.colors['card_bg'], borderwidth=1, relief="solid", bordercolor=self.colors['border_color'])

    # --- Methods below are for state management and delegation ---
    def get_style(self):
        return self.style

    def update_theme(self, theme_name):
        if theme_name in self.style.theme_names():
            self.style.theme_use(theme_name)
            self.setup_styles()

    def get_available_themes(self):
        return self.style.theme_names()

    def configure_custom_style(self, style_name, **kwargs):
        self.style.configure(style_name, **kwargs)

    def map_custom_style(self, style_name, **kwargs):
        self.style.map(style_name, **kwargs)

    def create_button_style(self, name, bg_color, fg_color='white', hover_color=None):
        self.style.configure(f'{name}.TButton',
                            foreground=fg_color,
                            background=bg_color,
                            font=self.fonts['normal'],
                            padding=(12, 8),
                            borderwidth=0,
                            relief='flat')

        if hover_color:
            self.style.map(f'{name}.TButton',
                           background=[('active', hover_color)],
                           foreground=[('active', fg_color)])

    def create_label_style(self, name, bg_color, fg_color, font_key='normal'):
        self.style.configure(f'{name}.TLabel',
                            background=bg_color,
                            foreground=fg_color,
                            font=self.fonts[font_key])

    def get_color(self, color_key):
        return self.colors.get(color_key, '#000000')

    def get_font(self, font_key):
        return self.fonts.get(font_key, ('Segoe UI', 11))

    def apply_widget_style(self, widget, bg=None, fg=None, font=None):
        if bg:
            widget.configure(bg=bg)
        if fg:
            widget.configure(fg=fg)
        if font:
            widget.configure(font=font)

    def get_themed_colors(self):
        return {
            'background': self.colors['bg_color'],
            'foreground': self.colors['primary_color'],
            'card_background': self.colors['card_bg'],
            'accent': self.colors['accent_color'],
            'success': self.colors['success_color'],
            'error': self.colors['error_color'],
            'warning': self.colors['warning_color']
        }