"""
DataTables API Views for SGII
Provides server-side processing endpoints for DataTables integration
"""

import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ..models import Comment, Document, Exchange, Timeline


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class ExchangeDataTableView(View):
    """
    DataTables server-side processing endpoint for Exchange list
    """

    def post(self, request):
        try:
            # DataTables parameters
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            order_column = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            # Column mapping for ordering
            columns = [
                "id",
                "student__first_name",
                "destination_university",
                "destination_country",
                "exchange_program",
                "start_date",
                "status",
                "created_at",
            ]

            # Base queryset with permission filtering
            queryset = Exchange.objects.select_related("student").all()

            # Apply user-based filtering
            if request.user.profile.role == "STUDENT":
                queryset = queryset.filter(student=request.user)
            elif request.user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                # For other roles, return empty queryset
                queryset = queryset.none()

            # Advanced filters processing
            advanced_filters = request.GET.get("advanced_filters") or request.POST.get("advanced_filters")
            if advanced_filters:
                try:
                    filters = json.loads(advanced_filters)
                    queryset = self.apply_advanced_filters(queryset, filters)
                except (json.JSONDecodeError, Exception) as e:
                    # Log error but continue with basic filtering
                    print(f"Advanced filters error: {e}")

            # Search filtering (basic DataTables search)
            if search_value:
                queryset = queryset.filter(
                    Q(student__first_name__icontains=search_value)
                    | Q(student__last_name__icontains=search_value)
                    | Q(destination_university__icontains=search_value)
                    | Q(destination_country__icontains=search_value)
                    | Q(exchange_program__icontains=search_value)
                    | Q(status__icontains=search_value)
                )

            # Record counts
            records_total = Exchange.objects.count()
            records_filtered = queryset.count()

            # Ordering
            if order_column < len(columns):
                order_field = columns[order_column]
                if order_dir == "desc":
                    order_field = f"-{order_field}"
                queryset = queryset.order_by(order_field)

            # Pagination
            queryset = queryset[start : start + length]

            # Data formatting
            data = []
            for exchange in queryset:
                row = [
                    exchange.id,
                    f"{exchange.student.get_full_name()}",
                    exchange.destination_university or "-",
                    exchange.destination_country or "-",
                    exchange.exchange_program or "-",
                    self.format_duration(exchange.start_date, exchange.end_date),
                    self.get_status_badge(exchange.status, exchange.get_status_display()),
                    exchange.created_at.strftime("%b %d, %Y"),
                    self.get_actions_html(exchange, request.user),
                ]
                data.append(row)

            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": records_total,
                    "recordsFiltered": records_filtered,
                    "data": data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                    "error": str(e),
                },
                status=500,
            )

    def format_duration(self, start_date, end_date):
        """Format date range for display"""
        if start_date and end_date:
            return f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"
        return '<span class="text-muted">Not specified</span>'

    def get_status_badge(self, status, display_name):
        """Generate status badge HTML"""
        status_colors = {
            "DRAFT": "bg-light text-muted border",
            "SUBMITTED": "bg-warning-subtle text-warning border border-warning-subtle",
            "UNDER_REVIEW": "bg-info-subtle text-info border border-info-subtle",
            "APPROVED": "bg-success-subtle text-success border border-success-subtle",
            "REJECTED": "bg-danger-subtle text-danger border border-danger-subtle",
            "COMPLETED": "bg-secondary-subtle text-secondary border border-secondary-subtle",
        }
        color_class = status_colors.get(status, "bg-light text-muted border")
        return f'<span class="badge {color_class}">{display_name}</span>'

    def get_actions_html(self, exchange, user):
        """Generate action buttons HTML"""
        actions = []

        # View action (always available)
        actions.append(
            f"""
            <a href="{reverse('exchange:exchange-detail', args=[exchange.id])}"
               class="btn btn-outline-primary btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="View Details">
                <i class="bi bi-eye"></i>
            </a>
        """
        )

        # Edit action (conditional)
        if (user == exchange.student and exchange.status in ["DRAFT", "SUBMITTED"]) or (
            user.profile.role in ["COORDINATOR", "MANAGER", "ADMIN"]
        ):
            actions.append(
                f"""
                <a href="{reverse('exchange:edit-exchange', args=[exchange.id])}"
                   class="btn btn-outline-secondary btn-sm"
                   data-bs-toggle="tooltip"
                   data-bs-title="Edit">
                    <i class="bi bi-pencil"></i>
                </a>
            """
            )

        return f'<div class="btn-group btn-group-sm">{"".join(actions)}</div>'

    def apply_advanced_filters(self, queryset, filters):
        """Apply advanced filtering logic"""
        # Date range filtering
        if filters.get("date_range"):
            date_range = filters["date_range"]
            if date_range.get("start"):
                try:
                    start_date = datetime.strptime(date_range["start"], "%Y-%m-%d").date()
                    queryset = queryset.filter(created_at__date__gte=start_date)
                except ValueError:
                    pass

            if date_range.get("end"):
                try:
                    end_date = datetime.strptime(date_range["end"], "%Y-%m-%d").date()
                    queryset = queryset.filter(created_at__date__lte=end_date)
                except ValueError:
                    pass

        # Status multi-select
        if filters.get("statuses"):
            statuses = filters["statuses"]
            if isinstance(statuses, list) and statuses:
                queryset = queryset.filter(status__in=statuses)

        # Country multi-select
        if filters.get("countries"):
            countries = filters["countries"]
            if isinstance(countries, list) and countries:
                queryset = queryset.filter(destination_country__in=countries)

        # Program filtering
        if filters.get("programs"):
            programs = filters["programs"]
            if isinstance(programs, list) and programs:
                queryset = queryset.filter(exchange_program__in=programs)

        # Global search across all fields
        if filters.get("global_search"):
            search_term = filters["global_search"]
            queryset = queryset.filter(
                Q(student__first_name__icontains=search_term)
                | Q(student__last_name__icontains=search_term)
                | Q(student__email__icontains=search_term)
                | Q(destination_university__icontains=search_term)
                | Q(destination_country__icontains=search_term)
                | Q(exchange_program__icontains=search_term)
                | Q(status__icontains=search_term)
                | Q(notes__icontains=search_term)
            )

        return queryset


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class BulkActionView(View):
    """
    Handle bulk actions for exchange applications (approve/reject multiple)
    """

    def post(self, request):
        try:
            # Check permissions
            if request.user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                return JsonResponse({"error": "Insufficient permissions"}, status=403)

            action_type = request.POST.get("action_type")
            exchange_ids = request.POST.get("exchange_ids", "").split(",")
            comment = request.POST.get("bulk_comment", "")

            if not action_type or not exchange_ids:
                return JsonResponse({"error": "Missing required parameters"}, status=400)

            # Validate action type
            if action_type not in ["approve", "reject"]:
                return JsonResponse({"error": "Invalid action type"}, status=400)

            # For rejection, require a comment
            if action_type == "reject" and not comment.strip():
                return JsonResponse({"error": "Comment is required for rejection"}, status=400)

            # Filter valid exchange IDs and get exchanges
            valid_ids = [id.strip() for id in exchange_ids if id.strip().isdigit()]
            exchanges = Exchange.objects.filter(id__in=valid_ids, status__in=["SUBMITTED", "UNDER_REVIEW"])

            if not exchanges.exists():
                return JsonResponse({"error": "No valid exchanges found for bulk action"}, status=400)

            success_count = 0
            error_count = 0
            errors = []

            # Process each exchange
            for exchange in exchanges:
                try:
                    if action_type == "approve":
                        new_status = "APPROVED"
                        # Create approval timeline entry
                        from ..models import Timeline

                        Timeline.objects.create(
                            exchange=exchange,
                            action="APPROVED",
                            description=(
                                f"Bulk approved by {request.user.get_full_name()}. Comment: {comment}"
                                if comment
                                else f"Bulk approved by {request.user.get_full_name()}"
                            ),
                            created_by=request.user,
                        )
                    else:  # reject
                        new_status = "REJECTED"
                        # Create rejection timeline entry
                        from ..models import Timeline

                        Timeline.objects.create(
                            exchange=exchange,
                            action="REJECTED",
                            description=f"Bulk rejected by {request.user.get_full_name()}. Reason: {comment}",
                            created_by=request.user,
                        )

                    # Update exchange status
                    exchange.status = new_status
                    exchange.decision_date = timezone.now()
                    exchange.reviewed_by = request.user
                    if comment:
                        exchange.notes = (
                            f"{exchange.notes}\n\nBulk {action_type}: {comment}"
                            if exchange.notes
                            else f"Bulk {action_type}: {comment}"
                        )
                    exchange.save()

                    success_count += 1

                    # Send notification email (optional)
                    try:
                        from ..services.email_notifications import send_status_change_notification

                        send_status_change_notification(exchange, new_status, comment)
                    except Exception as email_error:
                        # Log email error but don't fail the bulk action
                        print(f"Email notification failed for exchange {exchange.id}: {email_error}")

                except Exception as e:
                    error_count += 1
                    errors.append(f"Exchange #{exchange.id}: {str(e)}")

            # Prepare response
            response_data = {
                "success": True,
                "message": f"Bulk {action_type} completed.",
                "success_count": success_count,
                "error_count": error_count,
                "total_processed": success_count + error_count,
            }

            if errors:
                response_data["errors"] = errors

            # Redirect back to pending approvals with success message
            from django.contrib import messages

            if success_count > 0:
                messages.success(
                    request,
                    f'Successfully {action_type}d {success_count} application{"s" if success_count != 1 else ""}',
                )
            if error_count > 0:
                messages.warning(
                    request,
                    f'{error_count} application{"s" if error_count != 1 else ""} could not be processed',
                )

            # Return JSON response for AJAX or redirect for form submission
            if request.content_type == "application/json":
                return JsonResponse(response_data)
            else:
                from django.shortcuts import redirect

                return redirect("exchange:pending-approvals")

        except Exception as e:
            if request.content_type == "application/json":
                return JsonResponse(
                    {"success": False, "error": f"Bulk action failed: {str(e)}"},
                    status=500,
                )
            else:
                from django.contrib import messages
                from django.shortcuts import redirect

                messages.error(request, f"Bulk action failed: {str(e)}")
                return redirect("exchange:pending-approvals")


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class DocumentDataTableView(View):
    """
    DataTables server-side processing endpoint for Document list
    """

    def post(self, request):
        try:
            # DataTables parameters
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            order_column = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            # Column mapping
            columns = [
                "id",
                "original_name",
                "category",
                "exchange__student__first_name",
                "status",
                "file_size",
                "uploaded_at",
            ]

            # Base queryset
            queryset = Document.objects.select_related("exchange__student").all()

            # Apply user-based filtering
            if request.user.profile.role == "STUDENT":
                queryset = queryset.filter(exchange__student=request.user)
            elif request.user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

            # Search filtering
            if search_value:
                queryset = queryset.filter(
                    Q(original_name__icontains=search_value)
                    | Q(category__icontains=search_value)
                    | Q(exchange__student__first_name__icontains=search_value)
                    | Q(exchange__student__last_name__icontains=search_value)
                    | Q(status__icontains=search_value)
                )

            # Record counts
            records_total = Document.objects.count()
            records_filtered = queryset.count()

            # Ordering
            if order_column < len(columns):
                order_field = columns[order_column]
                if order_dir == "desc":
                    order_field = f"-{order_field}"
                queryset = queryset.order_by(order_field)

            # Pagination
            queryset = queryset[start : start + length]

            # Data formatting
            data = []
            for document in queryset:
                row = [
                    document.id,
                    document.original_name,
                    document.get_category_display(),
                    document.exchange.student.get_full_name(),
                    self.get_document_status_badge(document.status, document.get_status_display()),
                    self.format_file_size(document.file_size),
                    document.uploaded_at.strftime("%b %d, %Y"),
                    self.get_document_actions_html(document, request.user),
                ]
                data.append(row)

            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": records_total,
                    "recordsFiltered": records_filtered,
                    "data": data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                    "error": str(e),
                },
                status=500,
            )

    def get_document_status_badge(self, status, display_name):
        """Generate document status badge HTML"""
        status_colors = {
            "PENDING": "bg-warning-subtle text-warning border border-warning-subtle",
            "VERIFIED": "bg-success-subtle text-success border border-success-subtle",
            "REJECTED": "bg-danger-subtle text-danger border border-danger-subtle",
            "UPLOADED": "bg-info-subtle text-info border border-info-subtle",
        }
        color_class = status_colors.get(status, "bg-light text-muted border")
        return f'<span class="badge {color_class}">{display_name}</span>'

    def format_file_size(self, size_bytes):
        """Format file size for display"""
        if not size_bytes:
            return "-"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def get_document_actions_html(self, document, user):
        """Generate document action buttons HTML"""
        actions = []

        # View action
        actions.append(
            f"""
            <a href="{reverse('exchange:document-detail', args=[document.exchange.id, document.id])}"
               class="btn btn-outline-primary btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="View Document">
                <i class="bi bi-eye"></i>
            </a>
        """
        )

        # Download action if file exists
        if document.file:
            actions.append(
                f"""
                <a href="{document.file.url}"
                   class="btn btn-outline-secondary btn-sm"
                   data-bs-toggle="tooltip"
                   data-bs-title="Download"
                   target="_blank">
                    <i class="bi bi-download"></i>
                </a>
            """
            )

        return f'<div class="btn-group btn-group-sm">{"".join(actions)}</div>'


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class PendingApprovalsDataTableView(View):
    """
    DataTables server-side processing endpoint for Pending Approvals
    """

    def get(self, request):
        try:
            # DataTables parameters
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            order_column = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            # Column mapping
            columns = [
                "id",
                "student__first_name",
                "destination_university",
                "exchange_program",
                "status",
                "created_at",
            ]

            # Base queryset - only pending approvals
            queryset = Exchange.objects.select_related("student").filter(status__in=["SUBMITTED", "UNDER_REVIEW"])

            # Permission check
            if request.user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

            # Search filtering
            if search_value:
                queryset = queryset.filter(
                    Q(student__first_name__icontains=search_value)
                    | Q(student__last_name__icontains=search_value)
                    | Q(destination_university__icontains=search_value)
                    | Q(exchange_program__icontains=search_value)
                )

            # Record counts
            records_total = Exchange.objects.filter(status__in=["SUBMITTED", "UNDER_REVIEW"]).count()
            records_filtered = queryset.count()

            # Ordering
            if order_column < len(columns):
                order_field = columns[order_column]
                if order_dir == "desc":
                    order_field = f"-{order_field}"
                queryset = queryset.order_by(order_field)

            # Pagination
            queryset = queryset[start : start + length]

            # Data formatting
            data = []
            for exchange in queryset:
                row = [
                    exchange.id,
                    f"{exchange.student.get_full_name()}",
                    exchange.destination_university or "-",
                    exchange.exchange_program or "-",
                    self.get_status_badge(exchange.status, exchange.get_status_display()),
                    exchange.created_at.strftime("%b %d, %Y"),
                    self.get_approval_actions_html(exchange),
                ]
                data.append(row)

            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": records_total,
                    "recordsFiltered": records_filtered,
                    "data": data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                    "error": str(e),
                },
                status=500,
            )

    def get_status_badge(self, status, display_name):
        """Generate status badge HTML"""
        status_colors = {
            "SUBMITTED": "bg-warning-subtle text-warning border border-warning-subtle",
            "UNDER_REVIEW": "bg-info-subtle text-info border border-info-subtle",
        }
        color_class = status_colors.get(status, "bg-light text-muted border")
        return f'<span class="badge {color_class}">{display_name}</span>'

    def get_approval_actions_html(self, exchange):
        """Generate approval action buttons HTML"""
        actions = []

        # View action
        actions.append(
            f"""
            <a href="{reverse('exchange:exchange-detail', args=[exchange.id])}"
               class="btn btn-outline-primary btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="View Details">
                <i class="bi bi-eye"></i>
            </a>
        """
        )

        # Review action
        actions.append(
            f"""
            <a href="{reverse('exchange:review-exchange', args=[exchange.id])}"
               class="btn btn-outline-info btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="Review">
                <i class="bi bi-clipboard-check"></i>
            </a>
        """
        )

        # Approve action
        actions.append(
            f"""
            <a href="{reverse('exchange:approve-exchange', args=[exchange.id])}"
               class="btn btn-outline-success btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="Approve">
                <i class="bi bi-check-circle"></i>
            </a>
        """
        )

        # Reject action
        actions.append(
            f"""
            <a href="{reverse('exchange:reject-exchange', args=[exchange.id])}"
               class="btn btn-outline-danger btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="Reject">
                <i class="bi bi-x-circle"></i>
            </a>
        """
        )

        return f'<div class="btn-group btn-group-sm">{"".join(actions)}</div>'


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class ActivityDataTableView(View):
    """
    DataTables server-side processing endpoint for Activity/Timeline
    """

    def post(self, request):
        try:
            # DataTables parameters
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            order_column = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "desc")  # Default to newest first

            # Column mapping
            columns = [
                "id",
                "exchange__student__first_name",
                "action",
                "description",
                "created_by__first_name",
                "created_at",
            ]

            # Base queryset
            queryset = Timeline.objects.select_related("exchange__student", "created_by").all()

            # Permission filtering
            if request.user.profile.role == "STUDENT":
                queryset = queryset.filter(exchange__student=request.user)
            elif request.user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

            # Search filtering
            if search_value:
                queryset = queryset.filter(
                    Q(exchange__student__first_name__icontains=search_value)
                    | Q(exchange__student__last_name__icontains=search_value)
                    | Q(action__icontains=search_value)
                    | Q(description__icontains=search_value)
                    | Q(created_by__first_name__icontains=search_value)
                    | Q(created_by__last_name__icontains=search_value)
                )

            # Record counts
            records_total = Timeline.objects.count()
            records_filtered = queryset.count()

            # Ordering
            if order_column < len(columns):
                order_field = columns[order_column]
                if order_dir == "desc":
                    order_field = f"-{order_field}"
                queryset = queryset.order_by(order_field)

            # Pagination
            queryset = queryset[start : start + length]

            # Data formatting
            data = []
            for timeline in queryset:
                row = [
                    timeline.id,
                    f"{timeline.exchange.student.get_full_name()}",
                    self.get_action_badge(timeline.action),
                    timeline.description or "-",
                    (timeline.created_by.get_full_name() if timeline.created_by else "System"),
                    timeline.created_at.strftime("%b %d, %Y %H:%M"),
                    self.get_activity_actions_html(timeline),
                ]
                data.append(row)

            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": records_total,
                    "recordsFiltered": records_filtered,
                    "data": data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                    "error": str(e),
                },
                status=500,
            )

    def get_action_badge(self, action):
        """Generate action badge HTML"""
        action_colors = {
            "CREATED": "bg-primary-subtle text-primary border border-primary-subtle",
            "SUBMITTED": "bg-warning-subtle text-warning border border-warning-subtle",
            "APPROVED": "bg-success-subtle text-success border border-success-subtle",
            "REJECTED": "bg-danger-subtle text-danger border border-danger-subtle",
            "UPDATED": "bg-info-subtle text-info border border-info-subtle",
            "COMPLETED": "bg-secondary-subtle text-secondary border border-secondary-subtle",
        }
        color_class = action_colors.get(action, "bg-light text-muted border")
        return f'<span class="badge {color_class}">{action.title()}</span>'

    def get_activity_actions_html(self, timeline):
        """Generate activity action buttons HTML"""
        actions = []

        # View exchange action
        actions.append(
            f"""
            <a href="{reverse('exchange:exchange-detail', args=[timeline.exchange.id])}"
               class="btn btn-outline-primary btn-sm"
               data-bs-toggle="tooltip"
               data-bs-title="View Exchange">
                <i class="bi bi-eye"></i>
            </a>
        """
        )

        return f'<div class="btn-group btn-group-sm">{"".join(actions)}</div>'
