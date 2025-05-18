"""Add Tip tab functionality."""

import tkinter as tk
from tkinter import ttk
from gui.components import ComboboxKeyHandler


class AddTipTab:
    def __init__(self, parent, tip_operations, currency_converter):
        self.tip_operations = tip_operations
        self.currency_converter = currency_converter
        
        # Create and add tab
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="Add Tip")
        
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the Add Tip tab."""
        frame = ttk.Frame(self.frame, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Amount
        ttk.Label(frame, text="Amount:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(frame, textvariable=self.amount_var)
        amount_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        
        # Currency
        ttk.Label(frame, text="Currency:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.currency_var = tk.StringVar(value="USD")
        currencies = self.currency_converter.get_available_currencies()
        currency_combo = ttk.Combobox(frame, textvariable=self.currency_var, values=currencies)
        currency_combo.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        ComboboxKeyHandler.setup_keypress(currency_combo)
        
        # Notes
        ttk.Label(frame, text="Notes:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(frame, textvariable=self.notes_var)
        notes_entry.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add Button
        add_button = ttk.Button(frame, text="Add Tip", command=self.handle_add_tip)
        add_button.grid(column=1, row=3, sticky=tk.E, pady=20)
        
        # Status Label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(frame, textvariable=self.status_var)
        status_label.grid(column=0, row=4, columnspan=2, sticky=tk.W, pady=5)
        
        # Set focus
        amount_entry.focus()
    
    def handle_add_tip(self):
        """Handle the Add Tip button click."""
        try:
            amount = float(self.amount_var.get())
            currency = self.currency_var.get()
            notes = self.notes_var.get()
            
            if amount <= 0:
                self.status_var.set("Amount must be greater than zero")
                return
                
            if not currency:
                self.status_var.set("Currency must be selected")
                return
            
            tip_id = self.tip_operations.add_tip(amount, currency, notes=notes)
            
            if tip_id:
                self.status_var.set(f"Tip added successfully!")
                # Clear the form
                self.amount_var.set("")
                self.notes_var.set("")
            else:
                self.status_var.set("Failed to add tip")
                
        except ValueError:
            self.status_var.set("Please enter a valid amount")