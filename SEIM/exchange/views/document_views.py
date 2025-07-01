"""
Views for document management functionality
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..models import Document, Exchange
from ..services.secure_file_validator import SecureFileValidator


@login_required
def upload_document(request, pk):
    """View for uploading documents"""
    # Get exchange and validate ownership first
    exchange = get_object_or_404(Exchange, id=pk)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        file = request.FILES.get("document_file")

        # Check permission
        if exchange.student != request.user and not request.user.has_perm("exchange.can_upload_any_document"):
            messages.error(
                request,
                "You don't have permission to upload documents for this exchange.",
            )
            return redirect("exchange:exchange-detail", pk=pk)

        # Validate file
        try:
            # Use the secure file validator
            file_hash = SecureFileValidator.validate_file(file)

            # Check for existing documents of the same category
            existing_docs = exchange.documents.filter(category=category)
            supersedes = None
            version = 1

            if existing_docs.exists():
                # This is a new version of an existing document
                latest_doc = existing_docs.order_by("-version").first()
                supersedes = latest_doc
                version = latest_doc.version + 1

            # Create the document
            document = Document.objects.create(
                exchange=exchange,
                title=title,
                description=description,
                category=category,
                file=file,
                file_size=file.size,
                file_hash=file_hash,
                version=version,
                supersedes=supersedes,
            )

            # Log the document upload
            from ..models.applications.timeline import Timeline

            Timeline.log_document_upload(document, request.user)

            messages.success(request, f"Document '{title}' uploaded successfully.")
            return redirect("exchange:document-list", pk=pk)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("exchange:document-list", pk=pk)

    # GET request - show upload form
    # Check user can upload
    if exchange.student != request.user and not request.user.has_perm("exchange.can_upload_any_document"):
        messages.error(request, "You don't have permission to upload documents for this exchange.")
        return redirect("exchange:exchange-detail", pk=pk)

    return render(
        request,
        "exchange/document_upload.html",
        {"exchange": exchange, "document_types": Document.DOCUMENT_TYPES},
    )


@login_required
def document_list(request, pk):
    """View for listing all documents for an exchange"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Check permission
    if not (exchange.student == request.user or request.user.has_perm("exchange.can_review_exchange")):
        messages.error(request, "You don't have permission to view these documents.")
        return redirect("exchange:dashboard")

    # Get documents, grouping by category and showing only latest version
    documents = {}
    for doc in exchange.documents.all():
        category = doc.category
        if category not in documents or doc.version > documents[category].version:
            documents[category] = doc

    # Convert to list and sort by category
    document_list = sorted(documents.values(), key=lambda d: d.category)

    return render(
        request,
        "exchange/document_list.html",
        {
            "exchange": exchange,
            "documents": document_list,
            "document_types": Document.DOCUMENT_TYPES,
        },
    )


@login_required
def document_detail(request, pk, doc_id):
    """View for document details"""
    exchange = get_object_or_404(Exchange, id=pk)
    document = get_object_or_404(Document, id=doc_id, exchange=exchange)

    # Check permission
    if not (exchange.student == request.user or request.user.has_perm("exchange.can_review_exchange")):
        messages.error(request, "You don't have permission to view this document.")
        return redirect("exchange:dashboard")

    # Check file integrity
    integrity_valid = SecureFileValidator.verify_file_integrity(document)

    # Get previous versions
    previous_versions = []
    current = document.supersedes
    while current:
        previous_versions.append(current)
        current = current.supersedes

    return render(
        request,
        "exchange/document_detail.html",
        {
            "exchange": exchange,
            "document": document,
            "previous_versions": previous_versions,
            "integrity_valid": integrity_valid,
        },
    )


@login_required
def download_document(request, pk):
    """View for downloading a document"""
    document = get_object_or_404(Document, id=pk)

    # Check permission
    if not (document.exchange.student == request.user or request.user.has_perm("exchange.can_review_exchange")):
        messages.error(request, "You don't have permission to download this document.")
        return redirect("exchange:dashboard")

    # Verify file integrity before download
    if not SecureFileValidator.verify_file_integrity(document):
        messages.error(request, "Document integrity check failed. Cannot download.")
        return redirect("exchange:document-detail", pk=document.exchange.id, doc_id=document.id)

    # Serve the file
    response = HttpResponse(document.file.read(), content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{document.title}"'
    return response


@login_required
@permission_required("exchange.can_verify_documents", raise_exception=True)
@require_POST
def verify_document(request, pk):
    """View for verifying a document"""
    document = get_object_or_404(Document, id=pk)

    # Perform security scan
    is_safe, reason = SecureFileValidator.scan_file_content(document.file.path)

    if not is_safe:
        messages.error(request, f"Document failed security scan: {reason}")
        return redirect("exchange:document-detail", pk=document.exchange.id, doc_id=document.id)

    # Check integrity
    if not SecureFileValidator.verify_file_integrity(document):
        messages.error(
            request,
            "Document integrity check failed. The file may have been tampered with.",
        )
        return redirect("exchange:document-detail", pk=document.exchange.id, doc_id=document.id)

    # Verify the document
    result = document.verify_document(request.user)

    if result:
        messages.success(request, f"Document '{document.title}' has been verified.")
    else:
        messages.warning(request, "This document is already verified.")

    return redirect("exchange:document-detail", pk=document.exchange.id, doc_id=document.id)


@login_required
@permission_required("exchange.can_verify_documents", raise_exception=True)
@require_POST
def reject_document(request, pk):
    """View for rejecting a document"""
    document = get_object_or_404(Document, id=pk)
    reason = request.POST.get("rejection_reason", "")

    result = document.reject_document(request.user, reason=reason)

    if result:
        messages.success(request, f"Document '{document.title}' has been rejected.")

    return redirect("exchange:document-detail", pk=document.exchange.id, doc_id=document.id)


@login_required
def document_list_api(request):
    """API view for getting documents as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    exchange_id = request.GET.get("exchange_id")
    if not exchange_id:
        return JsonResponse({"error": "No exchange ID provided"}, status=400)

    try:
        exchange = Exchange.objects.get(id=exchange_id)

        # Check permission
        if not (exchange.student == request.user or request.user.has_perm("exchange.can_review_exchange")):
            return JsonResponse({"error": "Permission denied"}, status=403)

        documents = []
        for doc in exchange.documents.all():
            documents.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "category": doc.category,
                    "category_display": doc.get_category_display(),
                    "status": doc.status,
                    "status_display": doc.get_status_display(),
                    "verified": doc.verified,
                    "version": doc.version,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "file_size": doc.get_human_readable_size(),
                    "url": doc.get_absolute_url(),
                }
            )

        return JsonResponse({"documents": documents})

    except Exchange.DoesNotExist:
        return JsonResponse({"error": "Exchange not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
