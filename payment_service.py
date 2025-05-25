# payment_service.py

import stripe
import os
import logging
import json
from models import Order, PaymentStatus
from flask import current_app

class StripePaymentService:
    """Handles Stripe payment processing."""
    
    def __init__(self, stripe_secret_key=None, stripe_publishable_key=None):
        # Get keys from environment or config
        self.stripe_secret_key = stripe_secret_key or os.getenv('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = stripe_publishable_key or os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY must be set")
        
        stripe.api_key = self.stripe_secret_key
        self.order_manager = Order()
    
    def create_payment_intent(self, order_number, email, amount_cents, currency='usd'):
        """Create Stripe Payment Intent for order."""
        try:
            # Get order details
            order = self.order_manager.get_order(order_number)
            if not order:
                raise ValueError("Order not found")
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'order_number': order_number,
                    'customer_email': email,
                    'product_type': 'visa_photo_download'
                },
                receipt_email=email,
                description=f"Visa Photo Download - Order {order_number}"
            )
            
            # Update order with payment intent ID
            self.order_manager.update_payment_status(
                order_number, 
                PaymentStatus.PENDING.value, 
                intent['id']
            )
            
            logging.info(f"Created payment intent {intent['id']} for order {order_number}")
            
            return {
                'client_secret': intent['client_secret'],
                'payment_intent_id': intent['id'],
                'amount': amount_cents,
                'currency': currency,
                'order_number': order_number
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error creating payment intent: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error creating payment intent: {str(e)}")
            raise
    
    def handle_webhook(self, payload, sig_header, webhook_secret):
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logging.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logging.error(f"Invalid signature: {e}")
            raise
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            self._handle_payment_success(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            self._handle_payment_failed(event['data']['object'])
        else:
            logging.info(f"Unhandled event type: {event['type']}")
        
        return True
    
    def _handle_payment_success(self, payment_intent):
        """Handle successful payment."""
        order_number = payment_intent['metadata'].get('order_number')
        if not order_number:
            logging.error("No order_number in payment_intent metadata")
            return
        
        # Update order status
        self.order_manager.update_payment_status(
            order_number,
            PaymentStatus.COMPLETED.value,
            payment_intent['id']
        )
        
        # Get order details for email
        order = self.order_manager.get_order(order_number)
        if order:
            # Send confirmation email
            self._send_payment_confirmation_email(order)
        
        logging.info(f"Payment succeeded for order {order_number}")
    
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        order_number = payment_intent['metadata'].get('order_number')
        if not order_number:
            logging.error("No order_number in payment_intent metadata")
            return
        
        # Update order status
        self.order_manager.update_payment_status(
            order_number,
            PaymentStatus.FAILED.value,
            payment_intent['id']
        )
        
        logging.info(f"Payment failed for order {order_number}")
    
    def _send_payment_confirmation_email(self, order):
        """Send payment confirmation email with download links."""
        try:
            from email_service import EmailService
            email_service = EmailService()
            email_service.send_payment_confirmation(order)
        except Exception as e:
            logging.error(f"Failed to send confirmation email for order {order['order_number']}: {str(e)}")
    
    def get_publishable_key(self):
        """Get Stripe publishable key for frontend."""
        return self.stripe_publishable_key
    
    def refund_payment(self, order_number, reason=None):
        """Refund a payment."""
        try:
            order = self.order_manager.get_order(order_number)
            if not order:
                raise ValueError("Order not found")
            
            if not order['stripe_payment_intent_id']:
                raise ValueError("No payment intent found for order")
            
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=order['stripe_payment_intent_id'],
                reason=reason or 'requested_by_customer',
                metadata={
                    'order_number': order_number,
                    'refund_reason': reason or 'Customer request'
                }
            )
            
            # Update order status
            self.order_manager.update_payment_status(
                order_number,
                PaymentStatus.REFUNDED.value,
                order['stripe_payment_intent_id']
            )
            
            logging.info(f"Refunded payment for order {order_number}, refund ID: {refund['id']}")
            return refund
            
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error refunding payment: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error refunding payment: {str(e)}")
            raise

class PricingService:
    """Manages pricing for different photo services."""
    
    # Pricing in cents
    PRICING = {
        'single_photo': {
            'amount_cents': 299,  # $2.99
            'currency': 'usd',
            'description': 'Single Visa Photo Download'
        },
        'photo_with_printable': {
            'amount_cents': 499,  # $4.99
            'currency': 'usd', 
            'description': 'Visa Photo + Printable 4x6" Layout'
        }
    }
    
    @classmethod
    def get_price(cls, product_type='single_photo'):
        """Get price for product type."""
        return cls.PRICING.get(product_type, cls.PRICING['single_photo'])
    
    @classmethod
    def get_all_pricing(cls):
        """Get all pricing options."""
        return cls.PRICING

if __name__ == "__main__":
    # Test pricing service
    pricing = PricingService()
    print("Available pricing:")
    for product, details in pricing.get_all_pricing().items():
        print(f"  {product}: ${details['amount_cents']/100:.2f} - {details['description']}")