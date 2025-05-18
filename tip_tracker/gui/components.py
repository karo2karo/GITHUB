"""Reusable GUI components and utilities."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bson.objectid import ObjectId
from config import DARK_THEME
from utils.date_parser import DateParser


class EnhancedComboboxSearch:
    """An enhanced search functionality for tkinter comboboxes.
    
    Features:
    - Incremental search (finds matches as you type)
    - Shows dropdown automatically when typing
    - Filters the dropdown list to show only matching items
    - Supports case-insensitive search
    - Supports searching within the text, not just at the beginning
    - Remembers previous selections
    - Has placeholder text
    - Allows immediate keyboard searching when dropdown is opened
    """
    
    def __init__(self, combobox, values=None, placeholder="Search...", highlight_color="#4a90e2"):
        """Initialize the enhanced combobox search.
        
        Args:
            combobox: The ttk.Combobox widget
            values: Optional list of initial values
            placeholder: Text to show when the combobox is empty
            highlight_color: Color to highlight matching text (for future enhancements)
        """
        self.combobox = combobox
        self.original_values = list(values) if values else []
        self.placeholder = placeholder
        self.highlight_color = highlight_color
        self.search_var = combobox['textvariable']
        self.last_search = ""
        self.recent_selections = []  # Store recent selections
        
        # Set initial values
        if values:
            self.combobox['values'] = values
            
        # Setup event bindings
        self.combobox.bind('<KeyRelease>', self._on_keyrelease)
        self.combobox.bind('<<ComboboxSelected>>', self._on_selection)
        self.combobox.bind('<FocusIn>', self._on_focus_in)
        self.combobox.bind('<FocusOut>', self._on_focus_out)
        
        # Add special handling for dropdown button click and dropdown display
        self.combobox.bind('<Down>', self._on_dropdown_key)
        self.combobox.bind('<Button-1>', self._on_button_click)
        
        # Bind to postcommand to enable immediate keyboard search when dropdown opens
        self.combobox['postcommand'] = self._on_dropdown_opened
        
        # Set placeholder when empty
        if not self.search_var.get():
            self._set_placeholder()
    
    def _set_placeholder(self):
        """Set the placeholder text."""
        self.combobox.configure(foreground="gray")
        self.search_var.set(self.placeholder)
    
    def _clear_placeholder(self):
        """Clear the placeholder text."""
        self.combobox.configure(foreground="")
        self.search_var.set("")
    
    def _on_button_click(self, event):
        """Handle click on the combobox or dropdown button."""
        # Check if click is on dropdown button
        if self.combobox.identify(event.x, event.y) == 'downarrow':
            # Set focus to combobox entry - this allows immediate keyboard input
            self.combobox.focus_set()
            
            # If text is placeholder, clear it on dropdown button click
            if self.search_var.get() == self.placeholder:
                self._clear_placeholder()
    
    def _on_dropdown_key(self, event):
        """Handle down arrow key press."""
        # When down arrow pressed, ensure focus is on the combobox
        self.combobox.focus_set()
        
        # If text is placeholder, clear it on down arrow
        if self.search_var.get() == self.placeholder:
            self._clear_placeholder()
    
    def _on_dropdown_opened(self):
        """Called just before dropdown list is displayed."""
        # This ensures the combobox entry has focus when dropdown opens
        self.combobox.focus_set()
        
        # Show recent selections first if available
        if self.recent_selections:
            combined_values = self.recent_selections + [v for v in self.original_values if v not in self.recent_selections]
            self.combobox['values'] = combined_values
    
    def _on_focus_out(self, event):
        """Handle focus out event."""
        if not self.search_var.get():
            self._set_placeholder()
    
    def _on_selection(self, event):
        """Handle selection event."""
        selected = self.search_var.get()
        if selected and selected != self.placeholder:
            # Add to recent selections (avoid duplicates)
            if selected in self.recent_selections:
                self.recent_selections.remove(selected)
            self.recent_selections.insert(0, selected)
            self.recent_selections = self.recent_selections[:5]  # Keep only 5 most recent
        
        # Reset the dropdown to show all values next time
        self.combobox['values'] = self.original_values
    
    def _on_keyrelease(self, event):
        """Handle key release event."""
        # Skip special keys (arrows, enter, etc.)
        if event.keysym in ('Up', 'Down', 'Return', 'Escape'):
            return
        
        # Get current text
        current_text = self.search_var.get()
        
        # If the field was empty and this is the first character, clear placeholder
        if self.search_var.get() == self.placeholder and event.char:
            self._clear_placeholder()
            current_text = event.char
            self.search_var.set(current_text)
        
        # Don't search if empty
        if not current_text or current_text == self.placeholder:
            # Reset to show all values
            self.combobox['values'] = self.original_values
            return
        
        # Don't repeat the same search
        if current_text == self.last_search:
            return
        
        self.last_search = current_text
        
        # Find matches (case-insensitive, anywhere in the text)
        matching_values = []
        search_term = current_text.lower()
        
        # First add exact matches
        for value in self.original_values:
            if search_term == str(value).lower():
                matching_values.append(value)
        
        # Then add prefix matches
        for value in self.original_values:
            if str(value).lower().startswith(search_term) and value not in matching_values:
                matching_values.append(value)
        
        # Then add contains matches
        for value in self.original_values:
            if search_term in str(value).lower() and value not in matching_values:
                matching_values.append(value)
        
        # Update the combobox dropdown values
        if matching_values:
            self.combobox['values'] = matching_values
            
            # Show the dropdown if not already shown
            if not self.combobox.winfo_ismapped():
                self.combobox.event_generate('<Down>')
        else:
            # No matches, don't show dropdown
            self.combobox['values'] = []
    
    def set_values(self, values):
        """Update the list of values."""
        self.original_values = list(values)
        self.combobox['values'] = self.original_values
    
    def get_recent_selections(self):
        """Get the list of recent selections."""
        return self.recent_selections


class ComboboxKeyHandler:
    """Legacy key handler for comboboxes - kept for backward compatibility."""
    @staticmethod
    def setup_keypress(combobox):
        """Setup keyboard navigation for comboboxes."""
        def on_keypress(event):
            # Get the typed key
            key = event.char.upper()
            
            if not key.isalpha():
                return
                
            # Get all values
            values = combobox['values']
            for value in values:
                if str(value).upper().startswith(key):
                    combobox.set(value)
                    break
        
        combobox.bind('<KeyRelease>', on_keypress)


class EditTipDialog:
    def __init__(self, parent, tip_data, tip_operations, currency_converter):
        self.parent = parent
        self.tip_operations = tip_operations
        self.currency_converter = currency_converter
        
        # Extract tip data
        self.tip_id = tip_data['id']
        self.amount = tip_data['amount']
        self.currency = tip_data['currency']
        self.date_string = tip_data['date']
        self.notes = tip_data['notes']
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the edit dialog."""
        # Find the actual tkinter root window
        root = self._find_tkinter_root()
        
        # Now create the dialog with the proper root
        self.dialog = tk.Toplevel(root)
        self.dialog.title("Edit Tip")
        self.dialog.geometry("400x300")
        self.dialog.transient(root)
        self.dialog.grab_set()
        
        # Apply dark theme
        self.dialog.configure(bg=DARK_THEME['bg_color'])
        
        # Create form
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Amount
        ttk.Label(frame, text="Amount:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar(value=self.amount)
        ttk.Entry(frame, textvariable=self.amount_var).grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        
        # Currency
        ttk.Label(frame, text="Currency:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.currency_var = tk.StringVar(value=self.currency)
        currencies = self.currency_converter.get_available_currencies()
        currency_combo = ttk.Combobox(frame, textvariable=self.currency_var)
        currency_combo.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        # Use the enhanced search instead of the basic key handler
        self.currency_search = EnhancedComboboxSearch(
            currency_combo,
            values=currencies,
            placeholder="Type to search currency..."
        )
        
        # Date
        ttk.Label(frame, text="Date:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=self.date_string)
        ttk.Entry(frame, textvariable=self.date_var).grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
        
        # Notes
        ttk.Label(frame, text="Notes:").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar(value=self.notes)
        ttk.Entry(frame, textvariable=self.notes_var).grid(column=1, row=3, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=4, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        self.center_dialog(root)
    
    def _find_tkinter_root(self):
        """Find the actual tkinter root window."""
        current = self.parent
        
        # Method 1: Check if parent has a root attribute (TipTrackerApp instance)
        if hasattr(current, 'root') and hasattr(current.root, 'tk'):
            return current.root
        
        # Method 2: If parent has a frame, use its root
        if hasattr(current, 'frame') and hasattr(current.frame, 'winfo_toplevel'):
            return current.frame.winfo_toplevel()
        
        # Method 3: Traverse up to find the main window
        while current and hasattr(current, 'parent'):
            if hasattr(current, 'root') and hasattr(current.root, 'tk'):
                return current.root
            current = current.parent
        
        # Method 4: Use tkinter._default_root if available
        if tk._default_root:
            return tk._default_root
        
        # Fallback: Create a temporary root window
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide it immediately
        return temp_root
    
    def center_dialog(self, root):
        """Center dialog on parent window."""
        if root:
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
            y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def save_changes(self):
        """Save changes to the tip."""
        try:
            new_amount = float(self.amount_var.get())
            new_currency = self.currency_var.get()
            new_notes = self.notes_var.get()
            new_date_str = self.date_var.get()
            
            # Parse date
            new_date = DateParser.parse_date_string(new_date_str, "%Y-%m-%d %H:%M")
            if not new_date:
                messagebox.showerror("Invalid Date", "Please enter date as YYYY-MM-DD HH:MM")
                return
            
            if new_amount <= 0:
                messagebox.showerror("Invalid Amount", "Amount must be greater than zero")
                return
            
            if not new_currency:
                messagebox.showerror("Invalid Currency", "Currency must be selected")
                return
            
            # Convert string ID to ObjectId
            tip_id = ObjectId(self.tip_id)
            
            # Update tip in database
            self.tip_operations.update_tip(
                tip_id=tip_id, 
                amount=new_amount, 
                currency=new_currency, 
                date=new_date,
                notes=new_notes
            )
            
            # Close dialog
            self.dialog.destroy()
            
            # Signal parent to refresh
            if hasattr(self.parent, 'refresh_tips_view'):
                self.parent.refresh_tips_view()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount")


class ContextMenu:
    def __init__(self, parent, treeview, tip_operations, currency_converter):
        self.parent = parent
        self.treeview = treeview
        self.tip_operations = tip_operations
        self.currency_converter = currency_converter
        
        # For the menu widget, we need to use the actual tkinter widget as master
        # The treeview is the tkinter widget that has the required attributes
        
        # Create context menu using the treeview as master
        self.menu = tk.Menu(treeview, tearoff=0, bg=DARK_THEME['entry_bg'], fg=DARK_THEME['fg_color'])
        self.menu.add_command(label="Edit", command=self.edit_selected_tip)
        self.menu.add_command(label="Delete", command=self.delete_selected_tip)
        
        # Bind right-click on tree
        self.treeview.bind("<Button-3>", self.show_menu)
        # Double-click to edit
        self.treeview.bind("<Double-1>", lambda event: self.edit_selected_tip())
    
    def show_menu(self, event):
        """Show context menu on right-click."""
        item = self.treeview.identify_row(event.y)
        if item:
            # Select the item
            self.treeview.selection_set(item)
            # Show menu
            self.menu.post(event.x_root, event.y_root)
    
    def edit_selected_tip(self):
        """Edit the selected tip."""
        selected = self.treeview.selection()
        if not selected:
            return
            
        item_id = selected[0]
        tip_id_str = self.treeview.item(item_id, "text")
        values = self.treeview.item(item_id, "values")
        
        # Extract tip data
        tip_data = {
            'id': tip_id_str,
            'date': values[0],
            'amount': values[1],
            'currency': values[2],
            'notes': values[3]
        }
        
        # Create edit dialog
        EditTipDialog(self.parent, tip_data, self.tip_operations, self.currency_converter)
    
    def delete_selected_tip(self):
        """Delete the selected tip."""
        selected = self.treeview.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this tip?"):
            for item_id in selected:
                tip_id = self.treeview.item(item_id, "text")
                # Convert string ID to ObjectId
                self.tip_operations.delete_tip(ObjectId(tip_id))
            
            # Signal parent to refresh
            if hasattr(self.parent, 'refresh_tips_view'):
                self.parent.refresh_tips_view()
