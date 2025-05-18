"""Main window setup and theme configuration."""

import tkinter as tk
from tkinter import ttk
from config import WINDOW_TITLE, DEFAULT_WINDOW_SIZE, DARK_THEME
from database.db_manager import DatabaseManager
from database.tip_operations import TipOperations
from utils.currency import CurrencyConverter
from gui.add_tip_tab import AddTipTab
from gui.view_tips_tab import ViewTipsTab
from gui.statistics_tab import StatisticsTab
from gui.settings_tab import SettingsTab


class TipTrackerApp:
    def __init__(self):
        # Initialize database components
        self.db_manager = DatabaseManager()
        self.currency_converter = CurrencyConverter(self.db_manager)
        self.tip_operations = TipOperations(self.db_manager, self.currency_converter)
        
        # Initialize the GUI
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)

        # Apply dark theme
        self.setup_dark_theme()

        self.setup_gui()
        
    def setup_dark_theme(self):
        """Configure dark theme for all widgets."""
        # Configure root
        self.root.configure(bg=DARK_THEME['bg_color'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use("default")

        # Basic widget styling
        style.configure("TFrame", background=DARK_THEME['bg_color'])
        style.configure("TLabel", background=DARK_THEME['bg_color'], foreground=DARK_THEME['fg_color'])
        style.configure("TButton", background=DARK_THEME['button_bg'], foreground=DARK_THEME['fg_color'])
        style.map("TButton", background=[("active", DARK_THEME['button_active'])])
        
        # Entry field styling
        style.configure("TEntry", fieldbackground=DARK_THEME['entry_bg'], foreground=DARK_THEME['fg_color'])
        
        # Combobox styling
        style.configure("TCombobox", fieldbackground=DARK_THEME['entry_bg'], background=DARK_THEME['entry_bg'], 
                       foreground=DARK_THEME['fg_color'], arrowcolor=DARK_THEME['fg_color'])
        style.map("TCombobox", fieldbackground=[("readonly", DARK_THEME['entry_bg'])],
                 background=[("readonly", DARK_THEME['button_bg'])])
        
        # LabelFrame styling
        style.configure("TLabelframe", background=DARK_THEME['frame_bg'])
        style.configure("TLabelframe.Label", background=DARK_THEME['frame_bg'], foreground=DARK_THEME['fg_color'])
        
        # Notebook styling
        style.configure("TNotebook", background=DARK_THEME['bg_color'], borderwidth=0)
        style.configure("TNotebook.Tab", background=DARK_THEME['button_bg'], foreground=DARK_THEME['fg_color'], padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", DARK_THEME['button_active'])],
                 foreground=[("selected", DARK_THEME['fg_color'])])
        
        # Treeview styling
        style.configure("Treeview",
                       background=DARK_THEME['entry_bg'],
                       foreground=DARK_THEME['fg_color'],
                       fieldbackground=DARK_THEME['entry_bg'])
        style.configure("Treeview.Heading",
                       background=DARK_THEME['bg_color'],
                       foreground=DARK_THEME['fg_color'])
        style.map("Treeview", background=[("selected", DARK_THEME['button_active'])])
    
    def setup_gui(self):
        """Set up the GUI interface."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add tabs
        self.add_tip_tab = AddTipTab(notebook, self.tip_operations, self.currency_converter)
        self.view_tips_tab = ViewTipsTab(notebook, self.tip_operations, self.currency_converter)
        self.statistics_tab = StatisticsTab(notebook, self.tip_operations, self.currency_converter)
        self.settings_tab = SettingsTab(notebook, self.currency_converter, self.tip_operations)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
        # Close database connection when app closes
        self.db_manager.close_connection()