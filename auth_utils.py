import os
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

# ===========================
# 🔐 PASSWORD HASHING
# ===========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===========================
# 🔑 JWT CONFIGURATION
# ===========================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ===========================
# 🔒 AUTH HELPERS
# ===========================
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ===========================
# 📧 EMAIL (OTP SENDING)
# ===========================
async def send_otp_email(email: str, otp: str, full_name: str = "User") -> bool:
    """
    Send OTP via Gmail SMTP using aiosmtplib.
    Requires .env with:
        SENDER_EMAIL / EMAIL_SENDER
        SENDER_PASSWORD / EMAIL_PASSWORD
    """
    try:
        # Load from .env (both naming options supported)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL") or os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("SENDER_PASSWORD") or os.getenv("EMAIL_PASSWORD")

        # Validate credentials
        if not sender_email or not sender_password:
            print("❌ Missing SENDER_EMAIL or SENDER_PASSWORD in .env")
            return False

        # Email content
        subject = "MindLens AI - Email Verification Code"
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f9fafb; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 10px; padding: 30px; border: 1px solid #eee;">
              <h2 style="color: #4A90E2; text-align: center;">Welcome to MindLens AI Wellness</h2>
              <p>Hi <strong>{full_name}</strong>,</p>
              <p>Thank you for signing up! To verify your email, please use the following one-time password (OTP):</p>
              <div style="text-align: center; margin: 25px 0;">
                <span style="font-size: 30px; letter-spacing: 6px; color: #4A90E2;"><b>{otp}</b></span>
              </div>
              <p>This OTP will expire in <strong>10 minutes</strong>.</p>
              <p>If you didn’t request this, you can safely ignore this email.</p>
              <hr style="margin-top: 40px;">
              <p style="font-size: 12px; color: #666; text-align: center;">© MindLens AI Wellness - Automated Email</p>
            </div>
          </body>
        </html>
        """

        # Compose email
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email
        message.attach(MIMEText(html_content, "html"))

        # Try sending via Gmail
        print(f"📧 Connecting to {smtp_server}:{smtp_port} as {sender_email} ...")
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=sender_email,
            password=sender_password,
        )
        print(f"✅ OTP email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False


# ===========================
# ✅ VALIDATION HELPERS
# ===========================
def validate_email_format(email: str) -> bool:
    """Simple regex email validation."""
    import re
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Ensure password is strong."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, "Password is strong."
