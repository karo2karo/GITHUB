"""Currency conversion utilities."""

from datetime import datetime
import requests
from config import EXCHANGE_RATE_API_URL, DEFAULT_BASE_CURRENCY


class CurrencyConverter:
    def __init__(self, db_manager, base_currency=None):
        """Initialize currency converter with database and base currency."""
        self.db_manager = db_manager
        self.currencies_collection = db_manager.get_currencies_collection()
        self.settings_collection = db_manager.get_settings_collection()
        
        # Load or set base currency
        self.base_currency = base_currency or self._load_base_currency()
        
        # Initialize exchange rates
        self.exchange_rates = {}
        self.update_exchange_rates()
    
    def _load_base_currency(self):
        """Load base currency from settings or use default."""
        settings = self.settings_collection.find_one({"_id": "app_settings"})
        if settings and 'base_currency' in settings:
            return settings['base_currency']
        return DEFAULT_BASE_CURRENCY
    
    def update_exchange_rates(self):
        """Update currency exchange rates from API."""
        try:
            response = requests.get(EXCHANGE_RATE_API_URL)
            if response.status_code == 200:
                self.exchange_rates = response.json()['rates']
                # Store in database for offline use
                self.currencies_collection.replace_one(
                    {"_id": "exchange_rates"}, 
                    {"_id": "exchange_rates", "rates": self.exchange_rates, "updated": datetime.now()},
                    upsert=True
                )
        except Exception as e:
            print(f"Failed to update exchange rates: {e}")
            # Try to load from database as fallback
            stored_rates = self.currencies_collection.find_one({"_id": "exchange_rates"})
            if stored_rates:
                self.exchange_rates = stored_rates['rates']
    
    def convert(self, amount, from_currency, to_currency):
        """Convert amount between currencies."""
        if from_currency == to_currency:
            return amount
            
        if not self.exchange_rates:
            return None  # Cannot convert without rates
            
        # Convert through USD as base
        if from_currency == "USD":
            return amount * self.exchange_rates.get(to_currency, 1.0)
        elif to_currency == "USD":
            return amount / self.exchange_rates.get(from_currency, 1.0)
        else:
            # Convert to USD first, then to target currency
            usd_amount = amount / self.exchange_rates.get(from_currency, 1.0)
            return usd_amount * self.exchange_rates.get(to_currency, 1.0)
    
    def convert_to_base(self, amount, currency):
        """Convert amount to base currency."""
        return self.convert(amount, currency, self.base_currency)
    
    def get_base_currency(self):
        """Get the current base currency."""
        return self.base_currency
    
    def set_base_currency(self, new_base_currency):
        """Set new base currency and save to database."""
        self.base_currency = new_base_currency
        self.settings_collection.update_one(
            {"_id": "app_settings"},
            {"$set": {"base_currency": self.base_currency}},
            upsert=True
        )
    
    def get_available_currencies(self):
        """Get list of available currencies."""
        if self.exchange_rates:
            return list(self.exchange_rates.keys())
        return ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"]