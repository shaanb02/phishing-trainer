from datetime import datetime
from app import db
from flask_login import UserMixin

class User(db.Model):
    """
    Model representing employees/users who will receive phishing training emails
    This stores information about trainees in the cybersecurity program
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(50))
    role = db.Column(db.String(50))  # Used for AI personalization (manager, developer, HR, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationship to track clicks
    clicks = db.relationship('ClickLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name} ({self.email})>'

class EmailTemplate(db.Model):
    """
    Model for storing pre-written phishing email templates
    These can be used as-is or enhanced with AI generation
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text)
    category = db.Column(db.String(50))  # e.g., 'credential_harvesting', 'malware', 'social_engineering'
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class PhishingCampaign(db.Model):
    """
    Model representing a phishing training campaign
    Tracks when campaigns are sent and their overall statistics
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    use_ai_generation = db.Column(db.Boolean, default=False)
    ai_prompt_context = db.Column(db.Text)  # Additional context for AI generation
    
    # Campaign sequence support
    is_sequence = db.Column(db.Boolean, default=False)
    interval_days = db.Column(db.Integer, default=3)
    max_emails = db.Column(db.Integer, default=1)
    
    # Campaign status and timing
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Campaign statistics (calculated fields)
    total_sent = db.Column(db.Integer, default=0)
    total_clicked = db.Column(db.Integer, default=0)
    
    # Relationships
    template = db.relationship('EmailTemplate', backref='campaigns')
    emails_sent = db.relationship('SentEmail', backref='campaign', lazy=True)
    
    @property
    def click_rate(self):
        """Calculate the click rate percentage for this campaign"""
        if self.total_sent == 0:
            return 0
        return round((self.total_clicked / self.total_sent) * 100, 2)
    
    def __repr__(self):
        return f'<PhishingCampaign {self.name}>'

class SentEmail(db.Model):
    """
    Model tracking individual emails sent as part of campaigns
    Links users to campaigns and tracks delivery status
    """
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('phishing_campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Email content (may be AI-generated and personalized)
    subject = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    
    # Sequence tracking
    sequence_number = db.Column(db.Integer, default=1)
    
    # Tracking information
    tracking_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID for tracking clicks
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    
    # Relationships
    user = db.relationship('User', backref='sent_emails')
    clicks = db.relationship('ClickLog', backref='sent_email', lazy=True)
    
    @property
    def was_clicked(self):
        """Check if this email was clicked by the recipient"""
        return len(self.clicks) > 0
    
    def __repr__(self):
        return f'<SentEmail {self.tracking_id} to {self.user.email}>'

class ClickLog(db.Model):
    """
    Model for logging when users click on phishing links
    This is the core data for measuring training effectiveness
    """
    id = db.Column(db.Integer, primary_key=True)
    sent_email_id = db.Column(db.Integer, db.ForeignKey('sent_email.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Click tracking data
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.Text)
    
    # Advanced metrics
    time_to_click = db.Column(db.Integer)  # Seconds since email was sent
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    
    # Educational tracking
    viewed_education = db.Column(db.Boolean, default=False)
    education_viewed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<ClickLog user:{self.user_id} at {self.clicked_at}>'

class AdminUser(UserMixin, db.Model):
    """
    Model for administrators who can manage the phishing training system
    Separate from regular users who receive training
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
