import uuid
import os
import logging
from urllib.parse import urljoin
from flask import url_for, request

def generate_tracking_id():
    """
    Generate a unique tracking ID for phishing email links
    Uses UUID4 for strong uniqueness and security
    
    Returns:
        str: Unique tracking identifier
    """
    tracking_id = str(uuid.uuid4())
    logging.debug(f"Generated tracking ID: {tracking_id}")
    return tracking_id

def get_tracking_url(tracking_id):
    """
    Generate the full tracking URL for a given tracking ID
    This URL will be embedded in phishing emails
    
    Args:
        tracking_id (str): Unique tracking identifier
        
    Returns:
        str: Complete tracking URL
    """
    try:
        # Get base URL from environment or use Flask's url_for
        base_url = os.environ.get('BASE_URL')
        
        if base_url:
            # Use configured base URL (for production)
            tracking_url = urljoin(base_url.rstrip('/'), f'/click/{tracking_id}')
        else:
            # Use Flask's url_for (for development)
            tracking_url = url_for('track_click', tracking_id=tracking_id, _external=True)
        
        logging.debug(f"Generated tracking URL: {tracking_url}")
        return tracking_url
        
    except Exception as e:
        logging.error(f"Failed to generate tracking URL for {tracking_id}: {str(e)}")
        # Fallback URL
        return f"http://localhost:5000/click/{tracking_id}"

def get_education_url(tracking_id):
    """
    Generate URL for educational content related to a specific phishing attempt
    
    Args:
        tracking_id (str): Unique tracking identifier
        
    Returns:
        str: Complete education URL
    """
    try:
        base_url = os.environ.get('BASE_URL')
        
        if base_url:
            education_url = urljoin(base_url.rstrip('/'), f'/education/{tracking_id}')
        else:
            education_url = url_for('show_education', tracking_id=tracking_id, _external=True)
        
        return education_url
        
    except Exception as e:
        logging.error(f"Failed to generate education URL for {tracking_id}: {str(e)}")
        return f"http://localhost:5000/education/{tracking_id}"

def log_click_details(tracking_id, request_obj):
    """
    Extract and log detailed information about a click event
    Captures technical details for analysis while respecting privacy
    
    Args:
        tracking_id (str): Tracking identifier
        request_obj: Flask request object
        
    Returns:
        dict: Extracted click details
    """
    try:
        # Extract IP address (handle proxy forwarding)
        ip_address = request_obj.environ.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # Take the first IP if there are multiple (proxy chain)
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request_obj.remote_addr
        
        # Extract user agent
        user_agent = request_obj.headers.get('User-Agent', '')
        
        # Extract referrer information
        referrer = request_obj.headers.get('Referer', '')
        
        # Extract timestamp information
        from datetime import datetime
        timestamp = datetime.utcnow()
        
        click_details = {
            'tracking_id': tracking_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'referrer': referrer,
            'timestamp': timestamp,
            'method': request_obj.method,
            'url': request_obj.url
        }
        
        logging.info(f"Click details logged for {tracking_id}: IP={ip_address}, UA={user_agent[:50]}...")
        return click_details
        
    except Exception as e:
        logging.error(f"Failed to extract click details for {tracking_id}: {str(e)}")
        return {
            'tracking_id': tracking_id,
            'error': str(e),
            'timestamp': datetime.utcnow()
        }

def validate_tracking_id(tracking_id):
    """
    Validate that a tracking ID has the correct format
    Helps prevent invalid or malicious tracking attempts
    
    Args:
        tracking_id (str): Tracking ID to validate
        
    Returns:
        bool: True if valid UUID format, False otherwise
    """
    try:
        # Attempt to parse as UUID to validate format
        uuid.UUID(tracking_id)
        return True
    except (ValueError, TypeError):
        logging.warning(f"Invalid tracking ID format: {tracking_id}")
        return False

def generate_secure_unsubscribe_url(tracking_id):
    """
    Generate a secure unsubscribe URL for users who want to opt out
    Provides an ethical way for users to remove themselves from training
    
    Args:
        tracking_id (str): Unique tracking identifier
        
    Returns:
        str: Secure unsubscribe URL
    """
    try:
        # In a real implementation, this would include a secure token
        # For this educational tool, we'll use a simple approach
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        unsubscribe_url = urljoin(base_url.rstrip('/'), f'/unsubscribe/{tracking_id}')
        
        return unsubscribe_url
        
    except Exception as e:
        logging.error(f"Failed to generate unsubscribe URL: {str(e)}")
        return f"http://localhost:5000/unsubscribe/{tracking_id}"

def create_tracking_pixel(tracking_id):
    """
    Create a tracking pixel URL for email open tracking
    This allows tracking when emails are opened (in addition to clicks)
    
    Args:
        tracking_id (str): Unique tracking identifier
        
    Returns:
        str: Tracking pixel image URL
    """
    try:
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        pixel_url = urljoin(base_url.rstrip('/'), f'/pixel/{tracking_id}.png')
        
        return pixel_url
        
    except Exception as e:
        logging.error(f"Failed to create tracking pixel URL: {str(e)}")
        return f"http://localhost:5000/pixel/{tracking_id}.png"

def get_click_statistics(tracking_ids):
    """
    Get aggregated statistics for a list of tracking IDs
    Useful for campaign-level reporting
    
    Args:
        tracking_ids (list): List of tracking IDs to analyze
        
    Returns:
        dict: Aggregated click statistics
    """
    try:
        from models import ClickLog, SentEmail
        from app import db
        
        # Query click data for the provided tracking IDs
        clicks = db.session.query(ClickLog).join(
            SentEmail, ClickLog.sent_email_id == SentEmail.id
        ).filter(
            SentEmail.tracking_id.in_(tracking_ids)
        ).all()
        
        # Calculate statistics
        total_tracking_ids = len(tracking_ids)
        total_clicks = len(clicks)
        unique_clickers = len(set(click.user_id for click in clicks))
        
        # Calculate time-based statistics
        if clicks:
            click_times = [click.clicked_at for click in clicks]
            first_click = min(click_times)
            last_click = max(click_times)
        else:
            first_click = None
            last_click = None
        
        statistics = {
            'total_emails': total_tracking_ids,
            'total_clicks': total_clicks,
            'unique_clickers': unique_clickers,
            'click_rate': round((total_clicks / total_tracking_ids) * 100, 2) if total_tracking_ids > 0 else 0,
            'first_click': first_click,
            'last_click': last_click,
            'education_views': sum(1 for click in clicks if click.viewed_education)
        }
        
        return statistics
        
    except Exception as e:
        logging.error(f"Failed to calculate click statistics: {str(e)}")
        return {
            'error': str(e),
            'total_emails': len(tracking_ids),
            'total_clicks': 0,
            'click_rate': 0
        }
