from celery import shared_task
from django.utils import timezone


@shared_task
def scan_document_virus(document_id, validator_id):
    """Scan document for viruses using the configured virus scanner."""
    from .models import Document, DocumentValidation
    from .virus_scanner import scan_file_for_viruses

    try:
        document = Document.objects.get(id=document_id)

        # Check if file exists
        if not document.file or not document.file.path:
            result = "error"
            details = "File not found"
        else:
            try:
                # Scan the file
                is_clean, threat_name = scan_file_for_viruses(document.file.path)
                result = "valid" if is_clean else "infected"
                details = f"Scanned by async task. Threat: {threat_name}" if threat_name else "Scanned by async task"
            except Exception as e:
                result = "error"
                details = f"Scan failed: {str(e)}"

        # Create validation record
        DocumentValidation.objects.create(
            document=document,
            validator_id=validator_id,
            result=result,
            details=details,
            validated_at=timezone.now(),
        )

        # Update document status
        document.is_valid = result == "valid"
        document.validated_at = timezone.now()
        document.save()

        return f"Document {document_id} scanned: {result}"

    except Document.DoesNotExist:
        return f"Document {document_id} not found"
    except Exception as e:
        # Log error and mark as error
        from .models import DocumentValidation
        try:
            document = Document.objects.get(id=document_id)
            DocumentValidation.objects.create(
                document=document,
                validator_id=validator_id,
                result="error",
                details=f"Task failed: {str(e)}",
                validated_at=timezone.now(),
            )
            document.validated_at = timezone.now()
            document.save()
        except Exception:
            pass  # Avoid secondary errors

        return f"Virus scan task failed for document {document_id}: {str(e)}"
