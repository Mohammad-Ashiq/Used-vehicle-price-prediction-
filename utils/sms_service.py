import os
import json
import urllib.request
import urllib.parse
import secrets
import logging

logger = logging.getLogger(__name__)

# Supported SMS Gateways Environment Keys:
# 1. FAST2SMS_API_KEY (Recommended for India - https://www.fast2sms.com)
# 2. TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER (Global - https://www.twilio.com)
# 3. TWOFACTOR_API_KEY (India 2Factor - https://2factor.in)

FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', '').strip()
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '').strip()
TWOFACTOR_API_KEY = os.environ.get('TWOFACTOR_API_KEY', '').strip()

def generate_otp_code(digits=6):
    """Generates a secure, cryptographically random numeric OTP code."""
    # e.g., 6 digits between 100000 and 999999
    return str(secrets.randbelow(900000) + 100000)

def sanitize_phone_number(phone):
    """Sanitizes phone input, extracting standard 10-digit Indian mobile."""
    digits = ''.join([c for c in str(phone) if c.isdigit()])
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits

def send_carrier_sms(phone, otp_code):
    """
    Attempts to dispatch a physical SMS to the mobile carrier
    using Fast2SMS, Twilio, or 2Factor depending on configured keys.
    Returns: (bool success, str gateway_name, str message)
    """
    clean_phone = sanitize_phone_number(phone)
    if len(clean_phone) != 10:
        return False, 'none', f"Invalid phone format: '{phone}'. Requires 10-digit mobile number."

    # 1. Try Fast2SMS (India Premier Bulk SMS API)
    if FAST2SMS_API_KEY:
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                "authorization": FAST2SMS_API_KEY,
                "Content-Type": "application/json"
            }
            # Fast2SMS Quick OTP Route
            payload = json.dumps({
                "variables_values": otp_code,
                "route": "otp",
                "numbers": clean_phone
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data.get('return'):
                    return True, 'Fast2SMS', f"SMS delivered to +91 {clean_phone} via Fast2SMS."
                else:
                    return False, 'Fast2SMS', res_data.get('message', ['Failed to send'])[0]
        except Exception as e:
            logger.error(f"Fast2SMS error: {e}")

    # 2. Try 2Factor.in (India Transactional OTP Gateway)
    if TWOFACTOR_API_KEY:
        try:
            url = f"https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/{clean_phone}/{otp_code}/AUTOGEN"
            req = urllib.request.Request(url, headers={"User-Agent": "ReVahan-SMS-Engine"})
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data.get('Status') == 'Success':
                    return True, '2Factor', f"SMS delivered to +91 {clean_phone} via 2Factor.in."
                else:
                    return False, '2Factor', res_data.get('Details', 'Failed to dispatch OTP')
        except Exception as e:
            logger.error(f"2Factor error: {e}")

    # 3. Try Twilio SMS Gateway
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
        try:
            import base64
            url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
            auth_str = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
            b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
            
            headers = {
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = urllib.parse.urlencode({
                "To": f"+91{clean_phone}",
                "From": TWILIO_PHONE_NUMBER,
                "Body": f"Your ReVahan Vehicle Valuation verification code is: {otp_code}. Valid for 10 minutes."
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.getcode() in [200, 201]:
                    return True, 'Twilio', f"SMS dispatched to +91 {clean_phone} via Twilio."
        except Exception as e:
            logger.error(f"Twilio error: {e}")

    # No carrier SMS gateway key is configured in the environment
    return False, 'none', "No SMS gateway API key (Fast2SMS/Twilio/2Factor) configured."
