"""
Email service for sending verification and notification emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings
from app.logger import logger


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or settings.SMTP_USERNAME
    
    async def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """Send email verification email with code"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Email verification disabled.")
                return True  # Return True in development to avoid blocking
            
            subject = "Verify your email address - AICompanion"
            
            body = f"""
            <html>
            <body>
                <h2>Welcome to AICompanion!</h2>
                <p>Please use the following verification code to verify your email address:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <h1 style="font-size: 32px; color: #2196F3; letter-spacing: 5px; margin: 0;">{verification_code}</h1>
                </div>
                <p>Enter this code in the app to complete your email verification.</p>
                <p><strong>This code will expire in 30 minutes.</strong></p>
                <br>
                <p>If you didn't create an account, please ignore this email.</p>
                <p style="color: #666; font-size: 12px;">For security reasons, do not share this code with anyone.</p>
            </body>
            </html>
            """
            
            return await self._send_email(to_email, subject, body, is_html=True)
            
        except Exception as e:
            logger.error(f"Error sending verification email to {to_email}: {e}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """Send password reset email with code"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Password reset email disabled.")
                return True  # Return True in development to avoid blocking
            
            subject = "Reset your password - AICompanion"
            
            body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password for AICompanion.</p>
                <p>Please use the following code to reset your password:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <h1 style="font-size: 32px; color: #FF5722; letter-spacing: 5px; margin: 0;">{reset_code}</h1>
                </div>
                <p>Enter this code in the app along with your new password.</p>
                <p><strong>This code will expire in 30 minutes.</strong></p>
                <br>
                <p>If you didn't request a password reset, please ignore this email.</p>
                <p style="color: #666; font-size: 12px;">For security reasons, do not share this code with anyone.</p>
            </body>
            </html>
            """
            
            return await self._send_email(to_email, subject, body, is_html=True)
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {to_email}: {e}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email using SMTP"""
        try:
            # Validate credentials before attempting to send
            if not self.smtp_username or not self.smtp_password or not self.from_email:
                logger.error("SMTP credentials not properly configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable encryption
                server.login(self.smtp_username, self.smtp_password)
                text = msg.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
