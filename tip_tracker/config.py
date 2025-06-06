"""Configuration file for the Tip Tracker application."""

# MongoDB Configuration
MONGODB_URL = 'mongodb://localhost:27017/'
DATABASE_NAME = 'tip_tracker'
COLLECTIONS = {
    'tips': 'tips',
    'currencies': 'currencies',
    'settings': 'settings'
}

# Exchange Rate API
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/USD"

# Default Settings
DEFAULT_BASE_CURRENCY = "USD"
DEFAULT_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"]

# GUI Settings
WINDOW_TITLE = "Tip Tracker"
DEFAULT_WINDOW_SIZE = "800x600"

# Dark Theme Colors
DARK_THEME = {
    'bg_color': "#2e2e2e",
    'fg_color': "#ffffff",
    'entry_bg': "#3c3f41",
    'button_bg': "#3c3f41",
    'button_active': "#505357",
    'frame_bg': "#232323"
}