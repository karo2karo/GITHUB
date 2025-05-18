"""Settings tab functionality."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from gui.components import ComboboxKeyHandler


class SettingsTab:
    def __init__(self, parent, currency_converter, tip_operations):
        self.currency_converter = currency_converter
        self.tip_operations = tip_operations
        
        # Create and add tab
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="Settings")
        
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the Settings tab."""
        frame = ttk.Frame(self.frame, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Base currency setting
        ttk.Label(frame, text="Base Currency:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.base_currency_var = tk.StringVar(value=self.currency_converter.get_base_currency())
        currencies = self.currency_converter.get_available_currencies()
        base_currency_combo = ttk.Combobox(frame, textvariable=self.base_currency_var, values=currencies)
        base_currency_combo.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        ComboboxKeyHandler.setup_keypress(base_currency_combo)
        
        # Update exchange rates button
        update_rates_button = ttk.Button(frame, text="Update Exchange Rates", 
                                         command=self.handle_update_rates)
        update_rates_button.grid(column=1, row=1, sticky=tk.E, pady=10)
        
        # Save settings button
        save_button = ttk.Button(frame, text="Save Settings", 
                                 command=self.save_settings)
        save_button.grid(column=1, row=2, sticky=tk.E, pady=10)
        
        # MongoDB connection info
        mongo_frame = ttk.LabelFrame(frame, text="MongoDB Connection", padding=10)
        mongo_frame.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(mongo_frame, text="Server:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.mongo_server_var = tk.StringVar(value="mongodb://localhost:27017/")
        ttk.Entry(mongo_frame, textvariable=self.mongo_server_var).grid(column=1, row=0, 
                                                                       sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(mongo_frame, text="Database:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.mongo_db_var = tk.StringVar(value="tip_tracker")
        ttk.Entry(mongo_frame, textvariable=self.mongo_db_var).grid(column=1, row=1, 
                                                                   sticky=(tk.W, tk.E), pady=5)
        
        test_button = ttk.Button(mongo_frame, text="Test Connection", 
                                command=self.test_db_connection)
        test_button.grid(column=1, row=2, sticky=tk.E, pady=10)
    
    def handle_update_rates(self):
        """Handle updating exchange rates."""
        threading.Thread(target=self._update_rates_thread).start()
    
    def _update_rates_thread(self):
        """Update exchange rates in a separate thread."""
        self.currency_converter.update_exchange_rates()
        # Update UI from main thread
        self.frame.after(0, lambda: messagebox.showinfo("Exchange Rates", "Exchange rates updated"))
    
    def save_settings(self):
        """Save the settings."""
        # Update base currency
        new_base = self.base_currency_var.get()
        current_base = self.currency_converter.get_base_currency()
        
        if new_base != current_base:
            self.currency_converter.set_base_currency(new_base)
            
            # Recalculate all base amounts for existing tips
            self.tip_operations.recalculate_base_amounts()
            
            messagebox.showinfo("Settings", "Settings saved successfully")
    
    def test_db_connection(self):
        """Test the database connection."""
        try:
            from database.db_manager import DatabaseManager
            
            test_manager = DatabaseManager()
            success, error = test_manager.test_connection(
                self.mongo_server_var.get(),
                self.mongo_db_var.get()
            )
            
            if success:
                messagebox.showinfo("Connection Test", "Successfully connected to MongoDB")
            else:
                messagebox.showerror("Connection Test", f"Failed to connect: {error}")
                
        except Exception as e:
            messagebox.showerror("Connection Test", f"Failed to connect: {str(e)}")