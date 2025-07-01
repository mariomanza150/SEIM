from datetime import datetime

from django.db import transaction
from django.utils import timezone

from ..models import Exchange, WorkflowLog


class WorkflowService:
    """Service class for handling exchange workflow transitions"""

    @staticmethod
    @transaction.atomic
    def transition(exchange, new_status, user=None, comment=""):
        """
        Transition an exchange to a new status

        Args:
            exchange: Exchange instance
            new_status: Target status
            user: User performing the transition
            comment: Optional comment for the transition

        Returns:
            tuple: (success, message)
        """
        old_status = exchange.status

        # Check if transition is allowed
        if not exchange.can_transition_to(new_status):
            return False, f"Cannot transition from {old_status} to {new_status}"

        try:
            # Perform the transition
            exchange.transition_to(new_status, user=user)

            # Note: WorkflowLog is now created in the Exchange.transition_to method,
            # so we don't need to create it here.

            # Trigger post-transition actions
            WorkflowService._post_transition_actions(
                exchange, old_status, new_status, user
            )

            return True, f"Successfully transitioned from {old_status} to {new_status}"

        except Exception as e:
            return False, f"Error during transition: {str(e)}"

    @staticmethod
    def _post_transition_actions(exchange, old_status, new_status, user):
        """Handle actions that should occur after a transition"""

        # Import here to avoid circular imports
        from .document_generator import DocumentGenerator
        from .notification import NotificationService

        # Generate acceptance letter when approved
        if new_status == "APPROVED":
            generator = DocumentGenerator()
            pdf_buffer = generator.generate_acceptance_letter(exchange)
            generator.save_generated_document(
                exchange=exchange,
                document_type="acceptance_letter",
                title="Acceptance Letter",
                pdf_buffer=pdf_buffer,
            )

            # Send notification
            NotificationService.send_approval_notification(exchange)

        # Generate progress report on completion
        elif new_status == "COMPLETED":
            generator = DocumentGenerator()
            pdf_buffer = generator.generate_progress_report(exchange)
            generator.save_generated_document(
                exchange=exchange,
                document_type="progress_report",
                title="Final Progress Report",
                pdf_buffer=pdf_buffer,
            )

        # Send rejection notification
        elif new_status == "REJECTED":
            NotificationService.send_rejection_notification(exchange)

        # Send submission confirmation
        elif new_status == "SUBMITTED":
            NotificationService.send_submission_confirmation(exchange)

    @staticmethod
    def get_available_transitions(exchange, user):
        """Get list of available transitions for current user"""
        transitions = []

        for status in exchange.TRANSITIONS.get(exchange.status, []):
            # Check permissions
            if status in ["APPROVED", "REJECTED"] and not user.has_perm(
                "exchange.can_approve_exchange"
            ):
                continue
            if status == "UNDER_REVIEW" and not user.has_perm(
                "exchange.can_review_exchange"
            ):
                continue

            # Get the display name for the status
            status_display = dict(Exchange.STATUS_CHOICES).get(status, status)

            transitions.append({"status": status, "display": status_display})

        return transitions

    @staticmethod
    def get_workflow_history(exchange):
        """Get complete workflow history for an exchange"""
        return exchange.workflow_logs.select_related("user").order_by("-timestamp")

    @staticmethod
    def bulk_transition(exchanges, new_status, user, comment=""):
        """Transition multiple exchanges at once"""
        results = {"success": [], "failed": []}

        for exchange in exchanges:
            success, message = WorkflowService.transition(
                exchange=exchange, new_status=new_status, user=user, comment=comment
            )

            if success:
                results["success"].append({"exchange": exchange, "message": message})
            else:
                results["failed"].append({"exchange": exchange, "message": message})

        return results

    @staticmethod
    def validate_documents(exchange):
        """Check if all required documents are uploaded"""
        # Align with Exchange.has_required_documents required categories
        required_docs = ["passport", "transcript", "motivation_letter"]
        uploaded_types = exchange.documents.values_list("category", flat=True)

        missing = [doc for doc in required_docs if doc not in uploaded_types]

        return len(missing) == 0, missing

    @staticmethod
    def can_submit(exchange):
        """Enhanced submission validation"""
        errors = []

        # Status check
        if exchange.status != "DRAFT":
            errors.append("Application must be in draft status")

        # Required fields validation
        required_fields = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "student_number": "Student ID",
            "current_university": "Current university",
            "current_program": "Current program",
            "destination_university": "Host university",
            "destination_country": "Host country",
            "exchange_program": "Exchange program",
            "start_date": "Start date",
            "end_date": "End date",
            "motivation_letter": "Statement of purpose",
        }

        for field, label in required_fields.items():
            value = getattr(exchange, field, None)
            if not value:
                errors.append(f"{label} is required")

        # Validate motivation letter word count
        if exchange.motivation_letter:
            word_count = len(exchange.motivation_letter.split())
            if word_count < 200:
                errors.append(
                    f"Statement of purpose must be at least 200 words (current: {word_count})"
                )

        # Date validation
        if exchange.start_date and exchange.end_date:
            if exchange.end_date <= exchange.start_date:
                errors.append("End date must be after start date")

            from datetime import date

            if exchange.start_date < date.today():
                errors.append("Start date cannot be in the past")

        # Document validation - temporarily skip for basic functionality
        # if not exchange.has_required_documents():
        #     docs_valid, missing_docs = WorkflowService.validate_documents(exchange)
        #     if missing_docs:
        #         errors.append(f"Missing required documents: {', '.join(missing_docs)}")

        if errors:
            return False, "; ".join(errors)

        return True, "Application can be submitted"
