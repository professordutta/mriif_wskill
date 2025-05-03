import uuid
import os
import requests
from django.conf import settings

def get_proposal_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('proposals', filename)

def verify_recaptcha(token):
    """
    Verify a reCAPTCHA v3 token with Google's API
    Returns a tuple of (success, score)
    """
    if not token:
        return False, 0.0
        
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': token
    }
    
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data=data
    )
    
    result = response.json()
    
    # Return success status and score if available
    success = result.get('success', False)
    score = result.get('score', 0.0)
    
    return success, score