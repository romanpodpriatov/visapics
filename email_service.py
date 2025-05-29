# email_service.py

import os
import logging
import json
from datetime import datetime
from flask import url_for, current_app
try:
    from flask_mail import Mail, Message
except ImportError:
    Mail = None
    Message = None
from models import EmailLog

# Brevo API imports
try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    BREVO_AVAILABLE = True
except ImportError:
    BREVO_AVAILABLE = False
    logging.warning("Brevo SDK not available. Install with: pip install sib-api-v3-sdk")

class EmailService:
    """Handles email sending for payment confirmations and receipts."""
    
    def __init__(self, mail_instance=None):
        self.mail = mail_instance
        self.email_logger = EmailLog()
        
        # Initialize Brevo API client
        self.brevo_client = None
        self.use_brevo = False
        
        if BREVO_AVAILABLE:
            api_key = os.getenv('MAIL_API')
            if api_key:
                try:
                    configuration = sib_api_v3_sdk.Configuration()
                    configuration.api_key['api-key'] = api_key
                    client = sib_api_v3_sdk.ApiClient(configuration)
                    self.brevo_client = sib_api_v3_sdk.TransactionalEmailsApi(client)
                    self.use_brevo = True
                    logging.info("Brevo email service initialized successfully")
                except Exception as e:
                    logging.error(f"Failed to initialize Brevo: {e}")
                    self.use_brevo = False
            else:
                logging.warning("MAIL_API environment variable not set for Brevo")
        
        if not self.use_brevo and not mail_instance:
            logging.warning("No email service configured - emails will be logged only")
    
    def send_payment_confirmation(self, order):
        """Send payment confirmation email with download links."""
        try:
            subject = f"Payment Confirmed - Order {order['order_number']}"
            recipient = order['email']
            
            # Parse photo info if available
            photo_info = {}
            if order['photo_info']:
                try:
                    photo_info = json.loads(order['photo_info'])
                except:
                    pass
            
            # Generate download links
            try:
                download_link = url_for('download_paid_file', 
                                      order_number=order['order_number'],
                                      file_type='processed',
                                      _external=True)
                
                printable_link = None
                if order['printable_filename']:
                    printable_link = url_for('download_paid_file',
                                           order_number=order['order_number'], 
                                           file_type='printable',
                                           _external=True)
            except RuntimeError:
                # Working outside of application context - use direct links
                domain = os.getenv('DOMAIN', 'visapics.org')
                base_url = f"https://{domain}"
                download_link = f"{base_url}/download/{order['order_number']}/processed"
                printable_link = f"{base_url}/download/{order['order_number']}/printable" if order['printable_filename'] else None
            
            # Email content
            html_content = self._generate_confirmation_email_html(
                order, photo_info, download_link, printable_link
            )
            
            text_content = self._generate_confirmation_email_text(
                order, photo_info, download_link, printable_link
            )
            
            # Send email via Brevo or Flask-Mail
            if self.use_brevo and self.brevo_client:
                # Send via Brevo API
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{"email": recipient, "name": recipient.split('@')[0].title()}],
                    sender={"email": "support@visapics.org", "name": "VisaPics Support"},
                    reply_to={"email": "support@visapics.org", "name": "VisaPics Support"},
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content
                )
                
                response = self.brevo_client.send_transac_email(send_smtp_email)
                logging.info(f"Brevo email sent successfully. Message ID: {response.message_id}")
                status = 'sent'
                error_msg = None
                
            elif self.mail and Message:
                # Send via Flask-Mail
                msg = Message(
                    subject=subject,
                    recipients=[recipient],
                    html=html_content,
                    body=text_content
                )
                self.mail.send(msg)
                status = 'sent'
                error_msg = None
                
            else:
                # For testing/demo - just log the email
                logging.info(f"EMAIL WOULD BE SENT TO: {recipient}")
                logging.info(f"SUBJECT: {subject}")
                logging.info(f"DOWNLOAD LINK: {download_link}")
                if printable_link:
                    logging.info(f"PRINTABLE LINK: {printable_link}")
                status = 'sent'
                error_msg = None
            
            # Log email
            self.email_logger.log_email(
                order['order_number'],
                'payment_confirmation',
                recipient,
                subject,
                status,
                error_msg
            )
            
            logging.info(f"Payment confirmation email sent for order {order['order_number']}")
            return True
            
        except ApiException as e:
            error_msg = f"Brevo API error: {e.status} {e.reason}"
            logging.error(f"Failed to send payment confirmation email via Brevo: {error_msg}")
            logging.error(f"Brevo error body: {e.body}")
            self.email_logger.log_email(
                order['order_number'],
                'payment_confirmation',
                order['email'],
                subject,
                'failed',
                error_msg
            )
            return False
            
        except Exception as e:
            logging.error(f"Failed to send payment confirmation email: {str(e)}")
            self.email_logger.log_email(
                order['order_number'],
                'payment_confirmation',
                order['email'],
                subject,
                'failed',
                str(e)
            )
            return False
    
    def _generate_confirmation_email_html(self, order, photo_info, download_link, printable_link):
        """Generate HTML email content."""
        amount_dollars = order['amount_cents'] / 100
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .order-details {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
                .download-section {{ background: #e8f5e8; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 5px 0; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed!</h1>
                    <p>Thank you for your purchase</p>
                </div>
                
                <div class="content">
                    <h2>Order Details</h2>
                    <div class="order-details">
                        <p><strong>Order Number:</strong> {order['order_number']}</p>
                        <p><strong>Amount:</strong> ${amount_dollars:.2f} {order['currency'].upper()}</p>
                        <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Email:</strong> {order['email']}</p>
                    </div>
                    
                    <h2>Your Downloads</h2>
                    <div class="download-section">
                        <p><strong>📸 Processed Visa Photo (without watermark)</strong></p>
                        <a href="{download_link}" class="button">Download Processed Photo</a>
                        
                        {f'''
                        <p style="margin-top: 20px;"><strong>🖨️ Printable 4x6" Layout</strong></p>
                        <a href="{printable_link}" class="button">Download Printable Layout</a>
                        ''' if printable_link else ''}
                        
                        <div class="warning">
                            <p><strong>⚠️ Important:</strong></p>
                            <ul>
                                <li>Download links expire in 30 days</li>
                                <li>Maximum 5 downloads per order</li>
                                <li>Save your files after downloading</li>
                            </ul>
                        </div>
                    </div>
                    
                    {self._generate_photo_info_html(photo_info) if photo_info else ''}
                    
                    <h2>Need Help?</h2>
                    <p>If you have any issues with your order or downloads, please contact us with your order number: <strong>{order['order_number']}</strong></p>
                    <p>We're here to help ensure you get the perfect visa photo!</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 VisaPicture. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_confirmation_email_text(self, order, photo_info, download_link, printable_link):
        """Generate plain text email content."""
        amount_dollars = order['amount_cents'] / 100
        
        text = f"""
PAYMENT CONFIRMED!

Thank you for your purchase. Your visa photo is ready for download.

ORDER DETAILS:
Order Number: {order['order_number']}
Amount: ${amount_dollars:.2f} {order['currency'].upper()}
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Email: {order['email']}

YOUR DOWNLOADS:
Processed Visa Photo (without watermark): {download_link}
"""
        
        if printable_link:
            text += f"Printable 4x6\" Layout: {printable_link}\n"
        
        text += f"""
IMPORTANT:
- Download links expire in 30 days
- Maximum 5 downloads per order  
- Save your files after downloading

Need help? Contact us with your order number: {order['order_number']}

© 2025 VisaPicture. All rights reserved.
        """
        
        return text
    
    def _generate_photo_info_html(self, photo_info):
        """Generate HTML for photo processing information."""
        if not photo_info:
            return ""
        
        html = """
        <h2>Photo Processing Details</h2>
        <div class="order-details">
        """
        
        # Add key photo information
        if photo_info.get('spec_country'):
            html += f"<p><strong>Country:</strong> {photo_info['spec_country']}</p>"
        if photo_info.get('spec_document_name'):
            html += f"<p><strong>Document Type:</strong> {photo_info['spec_document_name']}</p>"
        if photo_info.get('photo_size_str'):
            html += f"<p><strong>Photo Size:</strong> {photo_info['photo_size_str']}</p>"
        if photo_info.get('achieved_head_height_mm'):
            html += f"<p><strong>Head Height:</strong> {photo_info['achieved_head_height_mm']:.1f}mm</p>"
        if photo_info.get('compliance_status'):
            status_color = "#4CAF50" if photo_info['compliance_status'] == "COMPLIANT" else "#ff9800"
            html += f"<p><strong>Compliance:</strong> <span style='color: {status_color}'>{photo_info['compliance_status']}</span></p>"
        
        html += "</div>"
        return html

def configure_mail(app):
    """Configure Flask-Mail for the application."""
    # Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@visapicture.com')
    
    mail = Mail(app)
    return mail

if __name__ == "__main__":
    # Test email template generation
    test_order = {
        'order_number': 'ORD-TEST123',
        'email': 'test@example.com',
        'amount_cents': 299,
        'currency': 'usd',
        'printable_filename': 'test_printable.jpg'
    }
    
    email_service = EmailService()
    html = email_service._generate_confirmation_email_html(
        test_order, {}, 
        'http://example.com/download/processed',
        'http://example.com/download/printable'
    )
    
    print("Test email HTML generated successfully")
    print(f"Length: {len(html)} characters")