"""Statistics tab functionality."""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import DARK_THEME
from utils.date_parser import DateParser


class StatisticsTab:
    def __init__(self, parent, tip_operations, currency_converter):
        self.tip_operations = tip_operations
        self.currency_converter = currency_converter
        
        # Create and add tab
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="Statistics")
        
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the Statistics tab."""
        self.stats_frame = ttk.Frame(self.frame, padding=20)
        self.stats_frame.pack(fill='both', expand=True)
        
        # Date range for stats
        filter_frame = ttk.LabelFrame(self.stats_frame, text="Date Range", padding=10)
        filter_frame.pack(fill='x', pady=10)
        
        ttk.Label(filter_frame, text="Start Date:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.stats_start_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.stats_start_date_var).grid(column=1, row=0, pady=5)
        
        ttk.Label(filter_frame, text="End Date:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.stats_end_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.stats_end_date_var).grid(column=1, row=1, pady=5)
        
        ttk.Button(filter_frame, text="Generate Statistics", command=self.update_statistics).grid(column=1, row=2, pady=10)
        
        # Stats info
        self.stats_text = tk.Text(self.stats_frame, height=10, width=50, 
                                  bg=DARK_THEME['entry_bg'], fg=DARK_THEME['fg_color'])
        self.stats_text.pack(fill='both', expand=True, pady=10)
        
        # Canvas for charts
        self.chart_frame = ttk.Frame(self.stats_frame)
        self.chart_frame.pack(fill='both', expand=True, pady=10)
        
        # Initial stats
        self.update_statistics()
    
    def update_statistics(self):
        """Update the statistics display."""
        # Clear existing stats
        self.stats_text.delete(1.0, tk.END)
        
        # Clear existing charts
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Parse dates
        start_date = DateParser.parse_date_string(self.stats_start_date_var.get())
        end_date = DateParser.parse_date_string(self.stats_end_date_var.get())
        
        if (self.stats_start_date_var.get() and not start_date) or (self.stats_end_date_var.get() and not end_date):
            self.stats_text.insert(tk.END, "Invalid date format. Use YYYY-MM-DD.\n")
            return
            
        # Get statistics
        stats = self.tip_operations.get_summary_stats(start_date, end_date)
        
        if not stats:
            self.stats_text.insert(tk.END, "No data available for the selected period.\n")
            return
            
        # Display text stats
        self.stats_text.insert(tk.END, f"Total Tips: {stats['total_tips']}\n\n")
        self.stats_text.insert(tk.END, f"Total in {stats['base_currency']}: {stats['total_base_currency']:.2f}\n\n")
        
        self.stats_text.insert(tk.END, "By Currency:\n")
        for curr, amount in stats['currency_totals'].items():
            # Add the USD equivalent for reference
            usd_equiv = stats['usd_equivalents'].get(curr, 0)
            self.stats_text.insert(tk.END, f"  {curr}: {amount:.2f} (≈ USD {usd_equiv:.2f})\n")
            
        # Create chart for currency distribution
        self.create_pie_chart(stats)
    
    def create_pie_chart(self, stats):
        """Create pie chart for currency distribution."""
        fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor=DARK_THEME['bg_color'])
        ax = fig.add_subplot(111, facecolor=DARK_THEME['bg_color'])
        
        # Use the USD equivalents for the pie chart
        labels = list(stats['usd_equivalents'].keys())
        sizes = list(stats['usd_equivalents'].values())
        
        # Create labels with both currency and USD value
        pie_labels = [f"{curr}\n(${val:.2f})" for curr, val in zip(labels, sizes)]
        
        # Create pie chart with improved styling
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=pie_labels, 
            autopct='%1.1f%%',
            startangle=90, 
            textprops=dict(color='white'),
            wedgeprops=dict(width=0.5, edgecolor=DARK_THEME['bg_color'])
        )
        
        # Improve title
        ax.set_title('Tips by Currency (USD Equivalent - Purchasing Power)', color='white', pad=20)
        
        # Set equal aspect ratio to ensure circular plot
        ax.set_aspect('equal')
        
        fig.tight_layout()
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)