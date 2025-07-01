"""
Email service for sending notifications using AWS SES or SMTP.
"""

import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for handling email notifications.
    Supports both AWS SES and SMTP backends.
    """

    def __init__(self):
        self.use_aws_ses = getattr(settings, "USE_AWS_SES", False)
        if self.use_aws_ses:
            self.ses_client = boto3.client(
                "ses",
                region_name=getattr(settings, "AWS_SES_REGION", "us-east-1"),
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
            )

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[tuple]] = None,
    ) -> bool:
        """
        Send email using configured backend.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            template_name: Name of the email template
            context: Context dictionary for template rendering
            from_email: Sender email address
            cc_emails: List of CC recipients
            bcc_emails: List of BCC recipients
            attachments: List of (filename, content, mimetype) tuples

        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Use default from email if not provided
            from_email = from_email or settings.DEFAULT_FROM_EMAIL

            # Render email content
            html_content = render_to_string(f"email/{template_name}.html", context)
            text_content = strip_tags(html_content)

            if self.use_aws_ses:
                return self._send_via_ses(
                    to_emails=to_emails,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                )
            else:
                return self._send_via_smtp(
                    to_emails=to_emails,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                    attachments=attachments,
                )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def _send_via_ses(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email using AWS SES.
        """
        try:
            destination = {
                "ToAddresses": to_emails,
            }

            if cc_emails:
                destination["CcAddresses"] = cc_emails

            if bcc_emails:
                destination["BccAddresses"] = bcc_emails

            response = self.ses_client.send_email(
                Source=from_email,
                Destination=destination,
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_content, "Charset": "UTF-8"},
                        "Html": {"Data": html_content, "Charset": "UTF-8"},
                    },
                },
            )

            logger.info(f"Email sent via SES. MessageId: {response['MessageId']}")
            return True

        except ClientError as e:
            logger.error(f"AWS SES error: {e}")
            return False

    def _send_via_smtp(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[tuple]] = None,
    ) -> bool:
        """
        Send email using Django's SMTP backend.
        """
        try:
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_emails,
                cc=cc_emails or [],
                bcc=bcc_emails or [],
            )

            # Attach HTML version
            email.attach_alternative(html_content, "text/html")

            # Add attachments if any
            if attachments:
                for filename, content, mimetype in attachments:
                    email.attach(filename, content, mimetype)

            # Send email
            email.send()
            logger.info(f"Email sent via SMTP to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
