"""View Tips tab functionality with pagination support."""

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
        
        # Pagination settings
        self.page_size = 20  # Number of entries per page
        self.current_page = 1
        self.total_pages = 1
        self.total_tips = 0
        
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
        
        # Pagination frame
        self.setup_pagination_controls(frame)
        
        # Load initial data
        self.refresh_tips_view()
    
    def setup_pagination_controls(self, parent):
        """Set up pagination controls."""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill='x', pady=5)
        
        # First page button
        self.first_page_btn = ttk.Button(pagination_frame, text="<<", command=self.go_to_first_page)
        self.first_page_btn.pack(side=tk.LEFT, padx=2)
        
        # Previous page button
        self.prev_page_btn = ttk.Button(pagination_frame, text="<", command=self.go_to_prev_page)
        self.prev_page_btn.pack(side=tk.LEFT, padx=2)
        
        # Page information label
        self.page_info_var = tk.StringVar(value="Page 1 of 1")
        page_info_label = ttk.Label(pagination_frame, textvariable=self.page_info_var)
        page_info_label.pack(side=tk.LEFT, padx=10)
        
        # Total entries label
        self.total_entries_var = tk.StringVar(value="Total entries: 0")
        total_entries_label = ttk.Label(pagination_frame, textvariable=self.total_entries_var)
        total_entries_label.pack(side=tk.LEFT, padx=10)
        
        # Next page button
        self.next_page_btn = ttk.Button(pagination_frame, text=">", command=self.go_to_next_page)
        self.next_page_btn.pack(side=tk.LEFT, padx=2)
        
        # Last page button
        self.last_page_btn = ttk.Button(pagination_frame, text=">>", command=self.go_to_last_page)
        self.last_page_btn.pack(side=tk.LEFT, padx=2)
        
        # Page size selection
        ttk.Label(pagination_frame, text="Page size:").pack(side=tk.LEFT, padx=10)
        self.page_size_var = tk.StringVar(value="20")
        page_size_combo = ttk.Combobox(pagination_frame, textvariable=self.page_size_var, 
                                      values=["10", "20", "50", "100"], width=5)
        page_size_combo.pack(side=tk.LEFT)
        page_size_combo.bind("<<ComboboxSelected>>", self.change_page_size)
    
    def change_page_size(self, event=None):
        """Handle page size change."""
        try:
            self.page_size = int(self.page_size_var.get())
            self.current_page = 1  # Reset to first page
            self.refresh_tips_view()
        except ValueError:
            self.page_size = 20
            self.page_size_var.set("20")
    
    def go_to_first_page(self):
        """Go to the first page."""
        if self.current_page > 1:
            self.current_page = 1
            self.load_tips_for_current_page()
    
    def go_to_prev_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tips_for_current_page()
    
    def go_to_next_page(self):
        """Go to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_tips_for_current_page()
    
    def go_to_last_page(self):
        """Go to the last page."""
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.load_tips_for_current_page()
    
    def update_pagination_info(self):
        """Update pagination information and button states."""
        self.page_info_var.set(f"Page {self.current_page} of {self.total_pages}")
        self.total_entries_var.set(f"Total entries: {self.total_tips}")
        
        # Update button states
        self.first_page_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        self.last_page_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
    
    def get_filtered_tips(self):
        """Get tips with current filters."""
        # Parse dates
        start_date = DateParser.parse_date_string(self.start_date_var.get())
        end_date = DateParser.parse_date_string(self.end_date_var.get())
        
        if (self.start_date_var.get() and not start_date) or (self.end_date_var.get() and not end_date):
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format")
            return None
            
        # Get tips with filters
        return self.tip_operations.get_tips(
            start_date=start_date,
            end_date=end_date,
            currency=self.filter_currency_var.get()
        )
    
    def load_tips_for_current_page(self):
        """Load tips for the current page only."""
        # Clear existing items
        for item in self.tips_tree.get_children():
            self.tips_tree.delete(item)
        
        # Get all filtered tips
        all_tips = self.get_filtered_tips()
        if all_tips is None:  # Error occurred
            return
        
        # Calculate pagination
        self.total_tips = len(all_tips)
        self.total_pages = max(1, (self.total_tips + self.page_size - 1) // self.page_size)
        
        # Ensure current page is valid
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # Calculate slice for current page
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_tips = all_tips[start_idx:end_idx]
        
        # Populate tree with current page tips
        for tip in page_tips:
            date_str = DateParser.format_datetime(tip['date'])
            self.tips_tree.insert("", tk.END, text=str(tip['_id']),
                                 values=(date_str, tip['amount'], tip['currency'], 
                                        tip.get('notes', '')))
        
        # Update pagination controls
        self.update_pagination_info()
    
    def refresh_tips_view(self):
        """Refresh the tips view with current filters."""
        self.current_page = 1  # Reset to first page
        self.load_tips_for_current_page()
    
    def export_tips_csv(self):
        """Export tips to CSV file using settings from database."""
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
        
        # Get the setting from database
        settings_collection = self.tip_operations.tips_collection.database.get_collection('settings')
        settings = settings_collection.find_one({"_id": "app_settings"})
        include_zero_days = True  # Default value
        
        if settings and 'include_zero_days_export' in settings:
            include_zero_days = settings['include_zero_days_export']
        
        if self.tip_operations.export_to_csv(filename, start_date, end_date, include_zero_days):
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        else:
            messagebox.showerror("Export Failed", "No data to export or export failed")