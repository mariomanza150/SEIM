"""
Batch processing functionality for exchange applications.
"""

import csv
import io
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import Document, Exchange
from .notification import NotificationService
from .workflow import WorkflowService

# Setup logger
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Service for batch processing exchange applications
    """

    @classmethod
    @transaction.atomic
    def bulk_status_update(cls, exchanges, new_status, user, comment=""):
        """
        Transition multiple exchanges to a new status

        Args:
            exchanges: QuerySet of Exchange objects
            new_status: Target status
            user: User performing the transition
            comment: Optional comment for the transition

        Returns:
            dict: Summary of results with success and failure counts
        """
        if not exchanges:
            return {
                "success_count": 0,
                "failure_count": 0,
                "total": 0,
                "errors": ["No exchanges specified"],
            }

        # Use the WorkflowService for consistent transition handling
        results = WorkflowService.bulk_transition(
            exchanges=exchanges, new_status=new_status, user=user, comment=comment
        )

        # Summarize results
        summary = {
            "success_count": len(results["success"]),
            "failure_count": len(results["failed"]),
            "total": len(results["success"]) + len(results["failed"]),
            "errors": [f"{ex['exchange']}: {ex['message']}" for ex in results["failed"]],
        }

        return summary

    @classmethod
    @transaction.atomic
    def bulk_document_verification(cls, documents, is_verified, user, notes=""):
        """
        Verify or reject multiple documents at once

        Args:
            documents: QuerySet of Document objects
            is_verified: Boolean indicating approval status
            user: User performing the verification
            notes: Optional notes for the verification

        Returns:
            dict: Summary of results with success and failure counts
        """
        if not documents:
            return {
                "success_count": 0,
                "failure_count": 0,
                "total": 0,
                "errors": ["No documents specified"],
            }

        success_count = 0
        failure_count = 0
        errors = []

        for document in documents:
            try:
                if is_verified:
                    document.verify_document(user)
                else:
                    document.reject_document(user, reason=notes)
                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"{document}: {str(e)}")
                logger.error(f"Error processing document {document.id}: {str(e)}")

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "total": success_count + failure_count,
            "errors": errors,
        }

    @classmethod
    def import_exchanges_from_csv(cls, csv_file, user):
        """
        Import exchange applications from CSV file

        Args:
            csv_file: CSV file object
            user: User performing the import

        Returns:
            dict: Summary of import results
        """
        try:
            # Parse CSV
            decoded_file = csv_file.read().decode("utf-8")
            csv_data = csv.DictReader(io.StringIO(decoded_file))

            created_count = 0
            failed_count = 0
            errors = []

            # Create exchanges from CSV rows
            for row in csv_data:
                try:
                    with transaction.atomic():
                        # Map CSV fields to Exchange model fields
                        exchange = Exchange(
                            student=user,  # Default to importing user
                            first_name=row.get("first_name", ""),
                            last_name=row.get("last_name", ""),
                            email=row.get("email", ""),
                            current_university=row.get("current_university", ""),
                            current_program=row.get("current_program", ""),
                            destination_university=row.get("destination_university", ""),
                            destination_country=row.get("destination_country", ""),
                            exchange_program=row.get("exchange_program", ""),
                            start_date=row.get("start_date"),
                            end_date=row.get("end_date"),
                            status="DRAFT",
                        )

                        # Set optional fields if present
                        if "phone" in row:
                            exchange.phone = row["phone"]
                        if "date_of_birth" in row:
                            exchange.date_of_birth = row["date_of_birth"]
                        if "passport_number" in row:
                            exchange.passport_number = row["passport_number"]
                        if "student_number" in row:
                            exchange.student_number = row["student_number"]
                        if "current_year" in row:
                            exchange.current_year = row["current_year"]
                        if "gpa" in row:
                            exchange.gpa = row["gpa"]
                        if "motivation_letter" in row:
                            exchange.motivation_letter = row["motivation_letter"]
                        if "language_proficiency" in row:
                            exchange.language_proficiency = row["language_proficiency"]
                        if "special_requirements" in row:
                            exchange.special_requirements = row["special_requirements"]
                        if "emergency_contact" in row:
                            exchange.emergency_contact = row["emergency_contact"]

                        # Save exchange
                        exchange.save()
                        created_count += 1

                except Exception as e:
                    failed_count += 1
                    errors.append(f"Row {created_count + failed_count}: {str(e)}")
                    logger.error(f"Error importing row: {str(e)}")

            return {
                "created_count": created_count,
                "failed_count": failed_count,
                "total": created_count + failed_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            return {
                "created_count": 0,
                "failed_count": 0,
                "total": 0,
                "errors": [f"Failed to process CSV: {str(e)}"],
            }

    @classmethod
    def export_exchanges_to_csv(cls, exchanges, include_fields=None):
        """
        Export exchanges to CSV

        Args:
            exchanges: QuerySet of Exchange objects
            include_fields: Optional list of fields to include

        Returns:
            str: CSV data as string
        """
        if not exchanges:
            return ""

        # Define fields to export (all by default)
        if not include_fields:
            include_fields = [
                "id",
                "first_name",
                "last_name",
                "email",
                "phone",
                "current_university",
                "current_program",
                "student_number",
                "destination_university",
                "destination_country",
                "exchange_program",
                "start_date",
                "end_date",
                "status",
                "submission_date",
                "decision_date",
                "gpa",
                "created_at",
                "updated_at",
            ]

        # Create CSV output
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=include_fields)
        writer.writeheader()

        # Write exchange data
        for exchange in exchanges:
            row = {}
            for field in include_fields:
                value = getattr(exchange, field, "")
                # Format dates
                if isinstance(value, (timezone.datetime, timezone.datetime.date)):
                    value = value.isoformat()
                row[field] = value
            writer.writerow(row)

        return output.getvalue()

    @classmethod
    def send_batch_notifications(cls, exchanges, notification_type, extra_context=None):
        """
        Send notifications to multiple exchanges at once

        Args:
            exchanges: QuerySet of Exchange objects
            notification_type: Type of notification to send
            extra_context: Optional additional context for notifications

        Returns:
            dict: Summary of notification results
        """
        if not exchanges:
            return {
                "success_count": 0,
                "failure_count": 0,
                "total": 0,
                "errors": ["No exchanges specified"],
            }

        success_count = 0
        failure_count = 0
        errors = []

        for exchange in exchanges:
            try:
                if notification_type == "approval":
                    NotificationService.send_approval_notification(exchange)
                elif notification_type == "rejection":
                    NotificationService.send_rejection_notification(exchange)
                elif notification_type == "submission":
                    NotificationService.send_submission_confirmation(exchange)
                else:
                    raise ValueError(f"Unknown notification type: {notification_type}")

                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"{exchange}: {str(e)}")
                logger.error(f"Error sending notification to {exchange.id}: {str(e)}")

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "total": success_count + failure_count,
            "errors": errors,
        }
