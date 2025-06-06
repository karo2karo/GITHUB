"""Tip-related database operations."""

from datetime import datetime, timedelta
import pymongo
import pandas as pd
from bson.objectid import ObjectId


class TipOperations:
    def __init__(self, db_manager, currency_converter):
        """Initialize tip operations with database manager and currency converter."""
        self.tips_collection = db_manager.get_tips_collection()
        self.currency_converter = currency_converter
    
    def add_tip(self, amount, currency, date=None, notes="", location=""):
        """Add a new tip entry to database."""
        if date is None:
            date = datetime.now()
            
        tip_data = {
            "amount": float(amount),
            "currency": currency,
            "date": date,
            "notes": notes,
            "location": location,
            # Store the equivalent in base currency for easier reporting
            "base_amount": self.currency_converter.convert_to_base(float(amount), currency)
        }
        
        result = self.tips_collection.insert_one(tip_data)
        return result.inserted_id
    
    def update_tip(self, tip_id, amount=None, currency=None, date=None, notes=None, location=None):
        """Update an existing tip entry."""
        update_data = {}
        
        if amount is not None:
            update_data["amount"] = float(amount)
            
        if currency is not None:
            update_data["currency"] = currency
            
        if date is not None:
            update_data["date"] = date
            
        if notes is not None:
            update_data["notes"] = notes
            
        if location is not None:
            update_data["location"] = location
            
        # Recalculate base amount if amount or currency changed
        if amount is not None or currency is not None:
            # Get current tip data
            current_tip = self.tips_collection.find_one({"_id": tip_id})
            
            if current_tip:
                # Use new values or current values
                new_amount = amount if amount is not None else current_tip["amount"]
                new_currency = currency if currency is not None else current_tip["currency"]
                
                # Update base amount
                update_data["base_amount"] = self.currency_converter.convert_to_base(
                    float(new_amount), new_currency
                )
        
        if update_data:
            result = self.tips_collection.update_one(
                {"_id": tip_id},
                {"$set": update_data}
            )
            return result.modified_count
        
        return 0
    
    def get_tips(self, start_date=None, end_date=None, currency=None, location=None):
        """Retrieve tips with optional filters."""
        query = {}
        
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        elif end_date:
            query["date"] = {"$lte": end_date}
            
        if currency:
            query["currency"] = currency
            
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
            
        return list(self.tips_collection.find(query).sort("date", pymongo.DESCENDING))
    
    def get_summary_stats(self, start_date=None, end_date=None):
        """Get summary statistics of tips."""
        tips = self.get_tips(start_date, end_date)
        
        if not tips:
            return None
            
        # Group by currency
        currency_totals = {}
        for tip in tips:
            curr = tip['currency']
            if curr not in currency_totals:
                currency_totals[curr] = 0
            currency_totals[curr] += tip['amount']
            
        # Calculate in base currency
        total_base = sum(tip['base_amount'] for tip in tips if 'base_amount' in tip)
            
        # Add USD equivalents for pie chart
        usd_equivalents = {}
        for curr, amount in currency_totals.items():
            usd_equivalents[curr] = self.currency_converter.convert(amount, curr, "USD")
        
        return {
            "total_tips": len(tips),
            "currency_totals": currency_totals,
            "total_base_currency": total_base,
            "base_currency": self.currency_converter.get_base_currency(),
            "usd_equivalents": usd_equivalents
        }
    
    def delete_tip(self, tip_id):
        """Delete a tip by ID."""
        result = self.tips_collection.delete_one({"_id": tip_id})
        return result.deleted_count
    
    def export_to_csv(self, filename, start_date=None, end_date=None, include_zero_days=True):
        """
        Export tips to CSV file with option to include zero values for missing dates.
        
        Args:
            filename: Path to save the CSV file
            start_date: Optional start date filter
            end_date: Optional end date filter
            include_zero_days: If True, includes a single entry with 0 amount for dates with no tips
            
        Returns:
            bool: True if export successful, False otherwise
        """
        # Get tips with filters
        tips = self.get_tips(start_date, end_date)
        if not tips:
            return False
        
        # If we don't need to fill missing dates, just export as before
        if not include_zero_days:
            df = pd.DataFrame(tips)
            df.to_csv(filename, index=False)
            return True
        
        # Determine date range
        if not start_date:
            first_tip = min(tips, key=lambda x: x['date'])
            start_date = first_tip['date']
        
        if not end_date:
            last_tip = max(tips, key=lambda x: x['date'])
            end_date = last_tip['date']
        
        # Create a complete date range - use date portions only to avoid time issues
        date_range = []
        current_date = datetime.combine(start_date.date(), datetime.min.time())
        end_date_normalized = datetime.combine(end_date.date(), datetime.min.time())
        
        while current_date <= end_date_normalized:
            date_range.append(current_date)
            current_date = current_date + timedelta(days=1)
        
        # Get default currency (use base currency or first available)
        default_currency = self.currency_converter.get_base_currency()
        if not default_currency and tips:
            default_currency = tips[0]['currency']
        
        # Group the original tips by date - use date portion only
        tips_by_date = {}
        for tip in tips:
            # Use just the date portion as key to avoid time issues
            date_key = tip['date'].strftime('%Y-%m-%d')
            if date_key not in tips_by_date:
                tips_by_date[date_key] = []
            tips_by_date[date_key].append(tip)
        
        # Create rows for the comprehensive DataFrame
        comprehensive_data = []
        
        for date in date_range:
            date_key = date.strftime('%Y-%m-%d')
            
            # If no tips for this date, add a single zero entry
            if date_key not in tips_by_date:
                comprehensive_data.append({
                    'date': date,
                    'amount': 0.0,
                    'currency': default_currency,
                    'notes': 'Auto-generated zero entry',
                    'base_amount': 0.0,
                    'location': ''
                })
            else:
                # Add all existing entries for this date
                for tip in tips_by_date[date_key]:
                    comprehensive_data.append(tip)
        
        # Create and export the comprehensive DataFrame
        comprehensive_df = pd.DataFrame(comprehensive_data)
        comprehensive_df.to_csv(filename, index=False)
        return True
    
    def recalculate_base_amounts(self):
        """Recalculate all base amounts after base currency change."""
        # Get all tips
        tips = list(self.tips_collection.find({}))
        
        update_operations = []
        for tip in tips:
            # Calculate the new base amount
            new_base_amount = self.currency_converter.convert_to_base(tip['amount'], tip['currency'])
            
            # Prepare bulk update operation
            update_operations.append(
                pymongo.UpdateOne(
                    {"_id": tip["_id"]},
                    {"$set": {"base_amount": new_base_amount}}
                )
            )
        
        # Execute bulk updates if any
        if update_operations:
            self.tips_collection.bulk_write(update_operations)