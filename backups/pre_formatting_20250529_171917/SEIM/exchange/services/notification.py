from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class NotificationService:
    """Service for handling email notifications"""

    @staticmethod
    def send_approval_notification(exchange):
        """Send email notification when exchange is approved"""
        subject = f"Exchange Application Approved - {exchange.destination_university}"

        # Prepare context for email template
        context = {
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "start_date": exchange.start_date,
            "end_date": exchange.end_date,
            "exchange": exchange,
            "settings": settings,
        }

        # Render email templates
        html_message = render_to_string("email/exchange_approved.html", context)
        plain_message = f"""
        Dear {exchange.first_name} {exchange.last_name},
        
        Congratulations! Your exchange application to {exchange.destination_university} 
        has been approved.
        
        Your exchange period: {exchange.start_date} to {exchange.end_date}
        
        Please check your dashboard for the acceptance letter and next steps.
        
        Best regards,
        International Exchange Office
        """

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[exchange.email],
            fail_silently=False,
            html_message=html_message,
        )

    @staticmethod
    def send_rejection_notification(exchange):
        """Send email notification when exchange is rejected"""
        subject = f"Exchange Application Update - {exchange.destination_university}"

        # Prepare context for email template
        context = {
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "exchange": exchange,
            "settings": settings,
        }

        # Render email templates
        html_message = render_to_string("email/exchange_rejected.html", context)
        plain_message = f"""
        Dear {exchange.first_name} {exchange.last_name},
        
        Thank you for your interest in the exchange program to {exchange.destination_university}.
        
        Unfortunately, we are unable to approve your application at this time. 
        You may reapply in the next application period.
        
        If you have any questions, please contact our office.
        
        Best regards,
        International Exchange Office
        """

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[exchange.email],
            fail_silently=False,
            html_message=html_message,
        )

    @staticmethod
    def send_submission_confirmation(exchange):
        """Send email confirmation when application is submitted"""
        subject = "Exchange Application Received"

        # Prepare context for email template
        context = {
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "submitted_at": exchange.submission_date,
            "exchange": exchange,
            "settings": settings,
        }

        # Render email templates
        html_message = render_to_string("email/exchange_submitted.html", context)
        plain_message = f"""
        Dear {exchange.first_name} {exchange.last_name},
        
        We have received your exchange application for {exchange.destination_university}.
        
        Application ID: {exchange.id}
        Submitted on: {exchange.submission_date.strftime('%B %d, %Y') if exchange.submission_date else 'Unknown'}
        
        We will review your application and notify you of our decision soon.
        
        Best regards,
        International Exchange Office
        """

        # Send email to student
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[exchange.email],
            fail_silently=False,
            html_message=html_message,
        )

        # Send notification to administrators
        admin_emails = (
            [admin.email for admin in settings.EXCHANGE_ADMIN_EMAILS]
            if hasattr(settings, "EXCHANGE_ADMIN_EMAILS")
            else []
        )
        if admin_emails:
            admin_subject = f"New Exchange Application Submitted - {exchange.destination_university}"
            admin_context = {
                "student_name": f"{exchange.first_name} {exchange.last_name}",
                "destination": exchange.destination_university,
                "submitted_at": exchange.submission_date,
                "exchange": exchange,
                "settings": settings,
            }
            admin_html_message = render_to_string(
                "email/exchange_submitted_admin.html", admin_context
            )
            admin_plain_message = f"""
            A new exchange application has been submitted.
            
            Student: {exchange.first_name} {exchange.last_name}
            Destination: {exchange.destination_university}
            Application ID: {exchange.id}
            Submitted on: {exchange.submission_date.strftime('%B %d, %Y') if exchange.submission_date else 'Unknown'}
            
            Please review the application at your earliest convenience.
            """

            send_mail(
                subject=admin_subject,
                message=admin_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
                html_message=admin_html_message,
            )

    @staticmethod
    def send_document_verification_notification(document):
        """Send notification when a document is verified"""
        exchange = document.exchange
        subject = f"Document Verified - {document.get_document_type_display()}"

        # Prepare context for email template
        context = {
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "document_title": document.title,
            "document_type": document.get_document_type_display(),
            "verified_at": document.verified_at,
            "exchange": exchange,
            "document": document,
            "settings": settings,
        }

        # Render email templates
        html_message = render_to_string("email/document_verified.html", context)
        plain_message = f"""
        Dear {exchange.first_name} {exchange.last_name},
        
        Your {document.get_document_type_display()} has been verified by our office.
        
        Document: {document.title}
        Verified on: {document.verified_at.strftime('%B %d, %Y') if document.verified_at else 'Unknown'}
        
        Best regards,
        International Exchange Office
        """

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[exchange.email],
            fail_silently=False,
            html_message=html_message,
        )
