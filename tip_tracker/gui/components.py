"""Reusable GUI components and utilities."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bson.objectid import ObjectId
from config import DARK_THEME
from utils.date_parser import DateParser


class ComboboxKeyHandler:
    """Setup keyboard navigation for comboboxes.
    
    Enables jumping to items that start with the pressed key when the dropdown is open.
    """
    
    @staticmethod
    def setup_keypress(combobox):
        """Setup keyboard navigation for comboboxes."""
        # Store state variables as attributes on the combobox widget itself
        combobox._last_key = None
        combobox._last_key_time = 0
        combobox._key_press_index = 0
        
        def on_key_press(event):
            """Handle key press events - fired when dropdown is open or closed."""
            # Get the typed key
            key = event.char.upper()
            
            # Skip if not an alphanumeric or printable character
            if not key or not key.strip():
                return
                
            # If dropdown is not open, use the standard behavior
            if not _is_dropdown_open(combobox):
                # This works when dropdown is closed
                values = combobox['values']
                for value in values:
                    if str(value).upper().startswith(key):
                        combobox.set(value)
                        break
                return
                
            # Beyond this point, the dropdown is open
            
            # Get current time for multi-key handling
            current_time = event.time
            
            # Reset index if different key or too much time has passed
            if key != combobox._last_key or (current_time - combobox._last_key_time > 500):  # 500ms timeout
                combobox._key_press_index = 0
            elif key == combobox._last_key:
                # Move to next match for repeated key press
                combobox._key_press_index += 1
            
            # Store key and time for next comparison
            combobox._last_key = key
            combobox._last_key_time = current_time
            
            # Find all values starting with the key
            matching_indices = []
            for i, value in enumerate(combobox['values']):
                if str(value).upper().startswith(key):
                    matching_indices.append(i)
            
            # If we have matches
            if matching_indices:
                # Wrap around the index if needed
                match_index = combobox._key_press_index % len(matching_indices)
                value_index = matching_indices[match_index]
                
                # Select the item in the dropdown
                combobox.current(value_index)
                
                # Prevent default handling
                return "break"
                
        def _is_dropdown_open(combobox):
            """Check if the dropdown is currently open.
            
            This is a heuristic based on combobox state and behavior.
            """
            # If combobox has 'dropdownVisible' attribute (some versions of tkinter), use it
            if hasattr(combobox, 'dropdownVisible'):
                return combobox.dropdownVisible
                
            # Otherwise use a heuristic - if combobox is mapped and has focus
            # Try multiple approaches to detect dropdown state
            try:
                # Approach 1: Check if dropdown is posted
                return combobox.winfo_ismapped() and combobox.tk.call("ttk::combobox::IsPopdown", combobox)
            except tk.TclError:
                try:
                    # Approach 2: Check if dropdown popdown is visible
                    return combobox.tk.call("ttk::combobox::Popdown", combobox) == 1
                except tk.TclError:
                    # Fallback approach: Focus heuristic
                    return combobox.focus_get() == combobox
        
        # Bind to both KeyPress (when dropdown is open) and KeyRelease (when closed)
        combobox.bind('<KeyPress>', on_key_press)
        
        # Track dropdown state with post-command and bindings
        def track_dropdown_open():
            combobox._dropdown_open = True
            
        def track_dropdown_close(event=None):
            combobox._dropdown_open = False
            
        # Try to bind to dropdown post and unpost events
        try:
            combobox['postcommand'] = track_dropdown_open
            combobox.bind('<<DropdownClose>>', track_dropdown_close)
        except:
            pass
            
        # Return the combobox for chaining
        return combobox


class JumpToKeyCombobox:
    """Enhanced combobox that jumps to items starting with pressed keys when dropdown is open.
    
    This implementation focuses on the standard behavior users expect:
    - When dropdown is open and user presses a key, it jumps to the first item starting with that key
    - Multiple quick presses of the same key cycle through items starting with that key
    - Works with regular combobox behavior for all other interactions
    """
    
    def __init__(self, combobox, values=None):
        """Initialize the jump-to-key combobox.
        
        Args:
            combobox: The ttk.Combobox widget
            values: Optional list of initial values
        """
        self.combobox = combobox
        self.values = list(values) if values else []
        
        # Set initial values
        if values:
            self.combobox['values'] = values
        
        # Setup the key press handler
        ComboboxKeyHandler.setup_keypress(combobox)
    
    def set_values(self, values):
        """Update the list of values."""
        self.values = list(values)
        self.combobox['values'] = self.values


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
        currency_combo = ttk.Combobox(frame, textvariable=self.currency_var, values=currencies)
        currency_combo.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        # Use the improved key handler for immediate searching
        ComboboxKeyHandler.setup_keypress(currency_combo)
        
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