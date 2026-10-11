import smtplib
import os
import logging
import re
import resend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content

def send_phishing_email(to_email, subject, html_content, text_content=None):
    """
    Send a phishing training email to a user
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject line
        html_content (str): HTML email body
        text_content (str): Plain text email body (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        from_email = os.environ.get('FROM_EMAIL', 'security-training@phishingsim.com')
        
        # Generate plain text from HTML if not provided
        if not text_content:
            plain_text = re.sub('<[^<]+?>', '', html_content)
            plain_text = plain_text.replace('&nbsp;', ' ').strip()
            text_content = plain_text
        
        # Priority 1: Use Resend if API key is available (recommended)
        resend_api_key = os.environ.get('RESEND_API_KEY')
        if resend_api_key:  # Removed email restriction for proper functionality
            resend.api_key = resend_api_key
            
            params = {
                "from": os.environ.get('FROM_EMAIL', 'IT Security Team <onboarding@resend.dev>'),
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            
            try:
                response = resend.Emails.send(params)
                logging.info(f"Email sent successfully to {to_email} via Resend (ID: {response.get('id', 'unknown')})")
                return True
            except Exception as e:
                logging.error(f"Resend sending failed: {str(e)}")
                # Continue to fallbacks if Resend fails
        
        # Priority 2: Use SendGrid if API key is available
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        if sendgrid_api_key:
            # Use SendGrid for email delivery with enhanced deliverability
            sg = SendGridAPIClient(sendgrid_api_key)
            
            from sendgrid.helpers.mail import Email, Content, Category, CustomArg
            
            # Create the email message with better deliverability settings
            message = Mail(
                from_email=Email(from_email, "IT Security Team"),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add plain text version to improve deliverability
            message.add_content(Content("text/plain", text_content))
            
            # Add categories for tracking and reputation
            message.add_category(Category("phishing-training"))
            message.add_category(Category("security-awareness"))
            
            # Add custom arguments for internal tracking
            message.add_custom_arg(CustomArg("campaign_type", "training"))
            message.add_custom_arg(CustomArg("purpose", "education"))
            
            # Set mail settings to improve deliverability
            from sendgrid.helpers.mail import MailSettings, BypassListManagement
            
            mail_settings = MailSettings()
            mail_settings.bypass_list_management = BypassListManagement(enable=False)
            message.mail_settings = mail_settings
            
            # Set tracking settings
            from sendgrid.helpers.mail import TrackingSettings, ClickTracking, OpenTracking
            tracking_settings = TrackingSettings()
            tracking_settings.click_tracking = ClickTracking(enable=False)  # Disable to avoid spam flags
            tracking_settings.open_tracking = OpenTracking(enable=False)    # Disable to avoid spam flags
            message.tracking_settings = tracking_settings
            
            response = sg.send(message)
            logging.info(f"Email sent successfully to {to_email} via SendGrid with enhanced deliverability (Status: {response.status_code})")
            return True
        
        # Priority 3: Fall back to SMTP or development mode
        smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '').replace(' ', '')
        
        from_display_name = "IT Security Team"
        from_header = f"{from_display_name} <{from_email}>"
        
        # Create multipart message
        message = MIMEMultipart('alternative')
        message['From'] = from_header
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add text content if provided
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            message.attach(text_part)
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Connect to SMTP server and send email
        if smtp_server == 'localhost':
            # For development/testing - use local SMTP server or print to console
            logging.info(f"[DEVELOPMENT MODE] Would send email to {to_email}")
            logging.info(f"Subject: {subject}")
            logging.info(f"HTML Content: {html_content[:200]}...")
            return True
        
        else:
            # Production email sending via SMTP
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Enable encryption
            
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
    
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def validate_email_template(html_content):
    """
    Validate that email template contains required elements for phishing simulation
    
    Args:
        html_content (str): HTML email content to validate
        
    Returns:
        dict: Validation result with success status and any errors
    """
    errors = []
    
    # Check for tracking URL placeholder
    if '{{TRACKING_URL}}' not in html_content:
        errors.append("Template must contain {{TRACKING_URL}} placeholder")
    
    # Check for user name placeholder
    if '{{USER_NAME}}' not in html_content:
        errors.append("Template should contain {{USER_NAME}} placeholder for personalization")
    
    # Check for basic HTML structure
    if '<html>' not in html_content.lower() or '<body>' not in html_content.lower():
        errors.append("Template should contain proper HTML structure with <html> and <body> tags")
    
    # Check for potentially harmful content (this is educational, but we want to be careful)
    dangerous_elements = ['<script>', 'javascript:', 'onload=', 'onclick=']
    for element in dangerous_elements:
        if element.lower() in html_content.lower():
            errors.append(f"Template contains potentially dangerous element: {element}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def create_tracking_email_content(template_content, tracking_url, user_name):
    """
    Process email template and insert tracking URL and user personalization
    
    Args:
        template_content (str): Original template content
        tracking_url (str): Unique tracking URL for this user
        user_name (str): User's name for personalization
        
    Returns:
        str: Processed email content with tracking and personalization
    """
    # Replace placeholders with actual values
    processed_content = template_content.replace('{{TRACKING_URL}}', tracking_url)
    processed_content = processed_content.replace('{{USER_NAME}}', user_name)
    
    # Convert newlines to <br> tags to prevent "clump of text" in HTML emails
    processed_content = processed_content.replace('\n', '<br>')
    
    # Add educational disclaimer to email (hidden but present for ethical reasons)
    disclaimer = '''
    <!-- This is a cybersecurity training email. If you received this, 
         you are part of a phishing awareness training program. -->
    '''
    
    # Insert disclaimer after opening body tag
    if '<body>' in processed_content.lower():
        body_index = processed_content.lower().find('<body>') + 6
        processed_content = (processed_content[:body_index] + 
                           disclaimer + 
                           processed_content[body_index:])
    
    return processed_content

def send_test_email(to_email, template_id=None):
    """
    Send a test email to verify SMTP configuration
    Used by administrators to test email delivery
    
    Args:
        to_email (str): Email address to send test to
        template_id (int): Optional template ID to test with
        
    Returns:
        bool: True if test email sent successfully
    """
    try:
        subject = "Cybersecurity Training System - Test Email"
        
        html_content = """
        <html>
        <body>
            <h2>Email Configuration Test</h2>
            <p>This is a test email from the Cybersecurity Training System.</p>
            <p>If you received this email, the SMTP configuration is working correctly.</p>
            <p><strong>Note:</strong> This is NOT a phishing simulation.</p>
            <hr>
            <small>Cybersecurity Training System</small>
        </body>
        </html>
        """
        
        return send_phishing_email(to_email, subject, html_content)
        
    except Exception as e:
        logging.error(f"Failed to send test email: {str(e)}")
        return False
