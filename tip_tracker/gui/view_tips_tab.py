"""View Tips tab functionality."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from gui.components import ComboboxKeyHandler, ContextMenu
from utils.date_parser import DateParser


class ViewTipsTab:
    def __init__(self, parent, tip_operations, currency_converter):
        self.tip_operations = tip_operations
        self.currency_converter = currency_converter
        
        # Store reference to parent (notebook) and find root window
        self.parent = parent
        self.root = self._find_root()
        
        # Create and add tab
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="View Tips")
        
        self.setup_tab()
    
    def _find_root(self):
        """Find the root window by traversing up the parent hierarchy."""
        current = self.parent
        while current:
            if hasattr(current, 'master'):  # Notebook has master
                current = current.master
                continue
            elif hasattr(current, 'root'):  # Should be TipTrackerApp
                return current.root
            elif hasattr(current, 'winfo_toplevel'):  # tkinter widget
                return current.winfo_toplevel()
            else:
                break
        return None
    
    def setup_tab(self):
        """Setup the View Tips tab."""
        frame = ttk.Frame(self.frame, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Filters Frame
        filter_frame = ttk.LabelFrame(frame, text="Filters", padding=10)
        filter_frame.pack(fill='x', pady=10)
        
        # Date filters
        ttk.Label(filter_frame, text="Start Date:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.start_date_var).grid(column=1, row=0, pady=5)
        ttk.Label(filter_frame, text="(YYYY-MM-DD)").grid(column=2, row=0, sticky=tk.W, pady=5)
        
        ttk.Label(filter_frame, text="End Date:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.end_date_var).grid(column=1, row=1, pady=5)
        ttk.Label(filter_frame, text="(YYYY-MM-DD)").grid(column=2, row=1, sticky=tk.W, pady=5)
        
        # Filter by currency
        ttk.Label(filter_frame, text="Currency:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.filter_currency_var = tk.StringVar()
        currencies = self.currency_converter.get_available_currencies()
        currencies.insert(0, "")  # Add empty option
        currency_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_currency_var, values=currencies)
        currency_filter_combo.grid(column=1, row=2, pady=5)
        ComboboxKeyHandler.setup_keypress(currency_filter_combo)
        
        # Apply filters button
        ttk.Button(filter_frame, text="Apply Filters", command=self.refresh_tips_view).grid(column=1, row=3, pady=10)
        
        # Export button
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_tips_csv).grid(column=2, row=3, pady=10)
        
        # Treeview for tips
        self.tips_tree = ttk.Treeview(frame, columns=("date", "amount", "currency", "notes"))
        self.tips_tree.heading("#0", text="ID")
        self.tips_tree.heading("date", text="Date")
        self.tips_tree.heading("amount", text="Amount")
        self.tips_tree.heading("currency", text="Currency")
        self.tips_tree.heading("notes", text="Notes")
        
        self.tips_tree.column("#0", width=0, stretch=tk.NO)  # Hide ID column
        self.tips_tree.column("date", width=100)
        self.tips_tree.column("amount", width=100)
        self.tips_tree.column("currency", width=80)
        self.tips_tree.column("notes", width=300)
        
        self.tips_tree.pack(fill='both', expand=True, pady=10)
        
        # Create context menu
        self.context_menu = ContextMenu(self, self.tips_tree, self.tip_operations, self.currency_converter)
        
        # Load initial data
        self.refresh_tips_view()
    
    def refresh_tips_view(self):
        """Refresh the tips view with current filters."""
        # Clear existing items
        for item in self.tips_tree.get_children():
            self.tips_tree.delete(item)
            
        # Parse dates
        start_date = DateParser.parse_date_string(self.start_date_var.get())
        end_date = DateParser.parse_date_string(self.end_date_var.get())
        
        if (self.start_date_var.get() and not start_date) or (self.end_date_var.get() and not end_date):
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format")
            return
            
        # Get tips with filters
        tips = self.tip_operations.get_tips(
            start_date=start_date,
            end_date=end_date,
            currency=self.filter_currency_var.get()
        )
        
        # Populate tree
        for tip in tips:
            date_str = DateParser.format_datetime(tip['date'])
            self.tips_tree.insert("", tk.END, text=str(tip['_id']),
                                 values=(date_str, tip['amount'], tip['currency'], 
                                        tip.get('notes', '')))
    
    def export_tips_csv(self):
        """Export tips to CSV file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        # Parse dates
        start_date = DateParser.parse_date_string(self.start_date_var.get())
        end_date = DateParser.parse_date_string(self.end_date_var.get())
        
        if (self.start_date_var.get() and not start_date) or (self.end_date_var.get() and not end_date):
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format")
            return
            
        if self.tip_operations.export_to_csv(filename, start_date, end_date):
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        else:
            messagebox.showerror("Export Failed", "No data to export or export failed")