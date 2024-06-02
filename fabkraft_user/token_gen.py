from django.conf import settings

import hashlib
import hmac
import base64
import time
SECRET_KEY = settings.SECRET_KEY

def generate_token(user_id):
    timestamp = int(time.time())
    data = f"{user_id}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()
    token = f"{data}:{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()

def verify_token(token, expiration=3600):
    try:
        token = base64.urlsafe_b64decode(token).decode()
        user_id, timestamp, signature = token.split(':')
        data = f"{user_id}:{timestamp}"
        expected_signature = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected_signature, signature):
            if int(time.time()) - int(timestamp) <= expiration:
                return int(user_id)
    except Exception as e:
        return None
    return None