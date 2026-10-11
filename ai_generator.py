import json
import os
import logging
from openai import OpenAI
from models import EmailTemplate

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_personalized_email(user_name,
                                user_role,
                                template_id=None,
                                context=None):
    """
    Generate a personalized phishing email using OpenAI's GPT-4o model
    
    Args:
        user_name (str): Target user's name
        user_role (str): Target user's role/department
        template_id (int): Optional base template to enhance
        context (str): Additional context for AI generation
        
    Returns:
        dict: Generated email with subject and HTML content
    """

    if not openai_client:
        logging.error("OpenAI API key not configured")
        return generate_fallback_email(user_name, user_role, template_id)

    try:
        # Get base template if provided
        base_template = None
        if template_id:
            base_template = EmailTemplate.query.get(template_id)

        # Construct the AI prompt for email generation
        prompt = construct_ai_prompt(user_name, user_role, base_template,
                                     context)

        # Generate email content using OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Latest model as of May 13, 2024
            messages=[{
                "role":
                "system",
                "content":
                "You are an expert cybersecurity trainer creating realistic phishing emails for educational purposes. Generate convincing but safe phishing emails that will help users learn to identify threats. Always include proper tracking placeholders and ensure content is professional but deceptive enough to be educational."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"},
            max_tokens=1500,
            temperature=
            0.7  # Balanced creativity for realistic but varied content
        )

        # Parse the AI response
        ai_result = json.loads(response.choices[0].message.content)

        # Validate and process the generated content
        processed_email = process_ai_generated_email(ai_result, user_name)

        logging.info(
            f"AI-generated personalized email for {user_name} ({user_role})")
        return processed_email

    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse AI response: {str(e)}")
        return generate_fallback_email(user_name, user_role, template_id)

    except Exception as e:
        logging.error(f"AI email generation failed: {str(e)}")
        return generate_fallback_email(user_name, user_role, template_id)


def construct_ai_prompt(user_name,
                        user_role,
                        base_template=None,
                        context=None):
    """
    Construct a detailed prompt for AI email generation
    
    Args:
        user_name (str): Target user's name
        user_role (str): Target user's role
        base_template (EmailTemplate): Optional base template
        context (str): Additional context
        
    Returns:
        str: Formatted prompt for AI generation
    """

    prompt = f"""
    Generate a realistic phishing email for cybersecurity training purposes.
    
    Target Information:
    - Name: {user_name}
    - Role: {user_role}
    
    Requirements:
    1. Create a convincing phishing email that someone in the {user_role} role might realistically receive.
    2. Personalize the content deeply based on their role, department, and common tasks associated with that role.
    3. Include multiple variables for high-fidelity personalization: {{USER_NAME}}, {{DEPARTMENT}}, {{CURRENT_DATE}}.
    4. Include a call-to-action that would lead to clicking a link.
    5. Make it educational but believable enough to be an effective training tool.
    6. Include {{{{TRACKING_URL}}}} placeholder where the malicious link should go.
    7. Include {{{{USER_NAME}}}} placeholder for further personalization.
    
    Common phishing scenarios for {user_role} role:
    - Account security alerts
    - Urgent business requests
    - IT support notifications
    - Fake invoices or payments
    - Social engineering attempts
    - Benefits enrollment or HR updates
    """

    if base_template:
        prompt += f"""
        
    Base Template to Enhance:
    Subject: {base_template.subject}
    Category: {base_template.category}
    Content: {base_template.html_content[:500]}...
    
    Enhance this template with personalization for {user_name} in the {user_role} role.
    """

    if context:
        prompt += f"""
        
    Additional Context: {context}
    """

    prompt += """
    
    Return your response as JSON with this exact structure:
    {
        "subject": "Email subject line",
        "html_content": "Complete HTML email content with proper structure",
        "rationale": "Brief explanation of the phishing techniques used",
        "difficulty_level": "easy|medium|hard",
        "warning_signs": ["List of red flags users should notice"]
    }
    
    Ensure the HTML includes proper structure with <html>, <head>, and <body> tags.
    The content should be professional-looking but contain subtle signs that it's a phishing attempt.
    """

    return prompt

def process_ai_generated_email(ai_result, user_name):
    """
    Process and validate AI-generated email content
    
    Args:
        ai_result (dict): Raw AI response
        user_name (str): User name for fallback processing
        
    Returns:
        dict: Processed email content
    """

    try:
        # Extract required fields
        subject = ai_result.get('subject', 'Important Security Notice')
        html_content = ai_result.get('html_content', '')
        rationale = ai_result.get('rationale', '')
        difficulty_level = ai_result.get('difficulty_level', 'medium')
        warning_signs = ai_result.get('warning_signs', [])

        # Validate HTML content structure
        if not html_content or '<html>' not in html_content.lower():
            raise ValueError("Invalid HTML structure in AI response")

        # Ensure tracking placeholders are present
        if '{{TRACKING_URL}}' not in html_content:
            # Add a generic tracking link if missing
            html_content = html_content.replace(
                '</body>',
                '<p><a href="{{TRACKING_URL}}">Click here to verify your account</a></p></body>'
            )

        # Ensure user name placeholder
        if '{{USER_NAME}}' not in html_content:
            html_content = html_content.replace(
                '<body>', f'<body><!-- Personalized for {{{{USER_NAME}}}} -->')

        return {
            'subject': subject,
            'html_content': html_content,
            'rationale': rationale,
            'difficulty_level': difficulty_level,
            'warning_signs': warning_signs
        }

    except Exception as e:
        logging.error(f"Error processing AI email content: {str(e)}")
        raise 


def generate_fallback_email(user_name, user_role, template_id=None):
    """
    Generate a basic personalized email when AI is unavailable
    
    Args:
        user_name (str): Target user's name
        user_role (str): Target user's role
        template_id (int): Optional template to use
        
    Returns:
        dict: Basic personalized email content
    """

    # Use template if provided, otherwise create basic phishing email
    if template_id:
        template = EmailTemplate.query.get(template_id)
        if template:
            return {
                'subject':
                template.subject,
                'html_content':
                template.html_content,
                'rationale':
                'Using base template (AI unavailable)',
                'difficulty_level':
                template.difficulty_level,
                'warning_signs':
                ['Check sender address', 'Verify links before clicking']
            }

    # Role-specific fallback emails
    role_templates = {
        'manager': {
            'subject':
            'Urgent: Employee Complaint Requires Your Review',
            'content':
            '''
            <html>
            <body>
                <p>Dear {{USER_NAME}},</p>
                <p>We have received a formal complaint about one of your team members that requires immediate management attention.</p>
                <p>Please review the details and provide your response within 24 hours:</p>
                <p><a href="{{TRACKING_URL}}" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none;">Review Complaint Details</a></p>
                <p>HR Department<br>Internal Use Only</p>
            </body>
            </html>
            '''
        },
        'developer': {
            'subject':
            'Critical Security Vulnerability - Action Required',
            'content':
            '''
            <html>
            <body>
                <p>Hi {{USER_NAME}},</p>
                <p>Our security team has identified a critical vulnerability in the production system that needs immediate attention.</p>
                <p>Please access the secure portal to review the vulnerability report and apply the necessary patches:</p>
                <p><a href="{{TRACKING_URL}}" style="background-color: #ff9800; color: white; padding: 10px 20px; text-decoration: none;">Access Security Portal</a></p>
                <p>Security Team<br>Priority: Critical</p>
            </body>
            </html>
            '''
        },
        'hr': {
            'subject':
            'Confidential: Employee Background Check Results',
            'content':
            '''
            <html>
            <body>
                <p>Dear {{USER_NAME}},</p>
                <p>The background check results for recent hires are now available for your review.</p>
                <p>Please access the confidential HR portal to review the results and complete the hiring process:</p>
                <p><a href="{{TRACKING_URL}}" style="background-color: #4caf50; color: white; padding: 10px 20px; text-decoration: none;">Access HR Portal</a></p>
                <p>Background Check Services<br>Confidential Document</p>
            </body>
            </html>
            '''
        }
    }

    # Get role-specific template or use generic
    role_key = user_role.lower() if user_role else 'generic'
    template_data = role_templates.get(role_key,
                                       role_templates.get('developer'))

    return {
        'subject':
        template_data['subject'],
        'html_content':
        template_data['content'],
        'rationale':
        f'Role-specific fallback template for {user_role}',
        'difficulty_level':
        'medium',
        'warning_signs': [
            'Urgent language creating pressure', 'Generic sender information',
            'Suspicious call-to-action buttons',
            'Lack of specific company details'
        ]
    }


def analyze_email_effectiveness(email_content, click_rate):
    """
    Use AI to analyze the effectiveness of phishing emails and suggest improvements
    
    Args:
        email_content (str): Email content to analyze
        click_rate (float): Click rate percentage for this email
        
    Returns:
        dict: Analysis and recommendations
    """

    if not openai_client:
        return {
            'analysis':
            'AI analysis unavailable - OpenAI API key not configured',
            'recommendations':
            ['Configure OpenAI API key for detailed analysis']
        }

    try:
        prompt = f"""
        Analyze this phishing training email for effectiveness:
        
        Email Content: {email_content[:1000]}...
        Click Rate: {click_rate}%
        
        Provide analysis on:
        1. What makes this email effective or ineffective
        2. Psychological techniques used
        3. Red flags users should have noticed
        4. Suggestions for improvement
        
        Return as JSON with: {{"analysis": "text", "recommendations": ["list"]}}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role":
                "system",
                "content":
                "You are a cybersecurity expert analyzing phishing email effectiveness for training purposes."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"},
            max_tokens=800)

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        logging.error(f"Failed to analyze email effectiveness: {str(e)}")
        return {
            'analysis': f'Analysis failed: {str(e)}',
            'recommendations': ['Review email manually for effectiveness']
        }
