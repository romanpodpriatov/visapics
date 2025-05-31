# models.py

import sqlite3
import os
import uuid
from datetime import datetime
from enum import Enum
import logging

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'payments.db')

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class DatabaseManager:
    """Manages SQLite database operations for payment system."""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    processed_filename TEXT NOT NULL,
                    printable_filename TEXT,
                    preview_filename TEXT,
                    stripe_payment_intent_id TEXT UNIQUE,
                    payment_status TEXT NOT NULL DEFAULT 'pending',
                    amount_cents INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'usd',
                    photo_info TEXT,  -- JSON string of photo processing info
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    download_expires_at TIMESTAMP,
                    download_count INTEGER DEFAULT 0,
                    max_downloads INTEGER DEFAULT 5
                )
            ''')
            
            # Download logs table for tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL,
                    file_type TEXT NOT NULL,  -- 'processed', 'printable'
                    ip_address TEXT,
                    user_agent TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_number) REFERENCES orders (order_number)
                )
            ''')
            
            # Email logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL,
                    email_type TEXT NOT NULL,  -- 'payment_confirmation', 'download_link'
                    recipient_email TEXT NOT NULL,
                    subject TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',  -- 'sent', 'failed'
                    error_message TEXT,
                    FOREIGN KEY (order_number) REFERENCES orders (order_number)
                )
            ''')
            
            conn.commit()
            logging.info("Database initialized successfully")
        finally:
            conn.close()

class Order:
    """Represents a payment order."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number."""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def create_order(self, email, processed_filename, amount_cents, 
                    printable_filename=None, preview_filename=None, 
                    photo_info=None, currency='usd'):
        """Create new order in database."""
        order_number = self.generate_order_number()
        
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    order_number, email, processed_filename, printable_filename,
                    preview_filename, amount_cents, currency, photo_info,
                    payment_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_number, email, processed_filename, printable_filename,
                preview_filename, amount_cents, currency, photo_info,
                PaymentStatus.PENDING.value
            ))
            conn.commit()
            logging.info(f"Created order {order_number} for {email}")
            return order_number
        finally:
            conn.close()
    
    def get_order(self, order_number):
        """Get order details by order number."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM orders WHERE order_number = ?
            ''', (order_number,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def update_payment_status(self, order_number, status, stripe_payment_intent_id=None):
        """Update payment status for order."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == PaymentStatus.COMPLETED.value:
                # Set paid_at timestamp and download expiration (e.g., 30 days)
                cursor.execute('''
                    UPDATE orders SET 
                        payment_status = ?, 
                        stripe_payment_intent_id = ?,
                        paid_at = CURRENT_TIMESTAMP,
                        download_expires_at = datetime('now', '+30 days')
                    WHERE order_number = ?
                ''', (status, stripe_payment_intent_id, order_number))
            else:
                cursor.execute('''
                    UPDATE orders SET 
                        payment_status = ?, 
                        stripe_payment_intent_id = ?
                    WHERE order_number = ?
                ''', (status, stripe_payment_intent_id, order_number))
            
            conn.commit()
        
        logging.info(f"Updated order {order_number} status to {status}")
    
    def update_order_email(self, order_number, email):
        """Update email address for order."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orders SET email = ? WHERE order_number = ?
            ''', (email, order_number))
            conn.commit()
        
        logging.info(f"Updated order {order_number} email to {email}")
    
    def can_download(self, order_number):
        """Check if order can be downloaded."""
        order = self.get_order(order_number)
        if not order:
            return False, "Order not found"
        
        if order['payment_status'] != PaymentStatus.COMPLETED.value:
            return False, "Payment not completed"
        
        # Check expiration
        if order['download_expires_at']:
            expires_at = datetime.fromisoformat(order['download_expires_at'])
            if datetime.now() > expires_at:
                return False, "Download link expired"
        
        # Check download count
        if order['download_count'] >= order['max_downloads']:
            return False, "Maximum downloads exceeded"
        
        return True, "OK"
    
    def increment_download_count(self, order_number, file_type, ip_address=None, user_agent=None):
        """Increment download count and log download."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Increment download count
            cursor.execute('''
                UPDATE orders SET download_count = download_count + 1 
                WHERE order_number = ?
            ''', (order_number,))
            
            # Log download
            cursor.execute('''
                INSERT INTO download_logs (order_number, file_type, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (order_number, file_type, ip_address, user_agent))
            
            conn.commit()
        
        logging.info(f"Logged download for order {order_number}, file type: {file_type}")

class EmailLog:
    """Manages email sending logs."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def log_email(self, order_number, email_type, recipient_email, subject, 
                  status='sent', error_message=None):
        """Log email sending attempt."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_logs (
                    order_number, email_type, recipient_email, subject, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_number, email_type, recipient_email, subject, status, error_message))
            conn.commit()
        
        logging.info(f"Logged email {email_type} for order {order_number} to {recipient_email}")

if __name__ == "__main__":
    # Test database initialization
    db = DatabaseManager()
    order_manager = Order(db)
    
    # Test order creation
    order_num = order_manager.create_order(
        email="test@example.com",
        processed_filename="test_processed.jpg",
        amount_cents=299,  # $2.99
        photo_info='{"test": "data"}'
    )
    
    print(f"Created test order: {order_num}")
    
    # Test order retrieval
    order = order_manager.get_order(order_num)
    print(f"Retrieved order: {order}")