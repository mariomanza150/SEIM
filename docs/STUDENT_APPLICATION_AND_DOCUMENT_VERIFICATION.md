# Student Application Management & Document Verification

## Purpose
This document describes the core features and workflows for student application management and secure document verification in SEIM.

---

## Overview
SEIM enables students to submit exchange applications using dynamic forms and securely upload required documents. The system ensures data integrity, multi-stage approvals, and robust file validation.

---

## 1. Application Workflow
- Students create and submit applications via dynamic forms.
- Each application is tracked as an `Exchange` record.
- Applications progress through multiple workflow stages (submission, review, approval, completion).
- Coordinators and managers review, approve, or reject applications at each stage.
- All actions are logged in the `Timeline` and can be commented on via the `Comment` model.

---

## 2. Dynamic Forms
- Forms are generated based on program requirements.
- Validation is enforced both client-side (Bootstrap) and server-side (Django forms).
- Form schemas can be updated without code changes for flexibility.

---

## 3. Document Upload & Verification
- Students upload required documents (PDF, images, etc.) as part of their application.
- Uploaded files are stored as `Document` records and saved in `/app/media/exchanges/`.
- File validation includes:
  - MIME type checking (libmagic)
  - SHA-256 hash verification
  - Content scanning for malicious files
- Only valid, non-malicious files are accepted.
- All document actions are logged for auditability.

---

## 4. Access Control
- Only authenticated users can submit or view applications.
- Role-based permissions:
  - Students: manage their own applications
  - Coordinators: review all applications
  - Managers: approve/reject applications
  - Admins: full access

---

## 5. Notifications
- Email notifications are sent at key workflow stages (submission, review, approval, rejection).
- Notification templates are customizable.

---

## 6. Best Practices
- Always validate files on both client and server.
- Use strong, unique filenames to prevent collisions.
- Regularly review audit logs for suspicious activity.

---

## References
- [API: Exchanges](api/exchanges.md)
- [API: Documents](api/documents.md)
- [Authentication & Permissions](AUTHENTICATION_AND_PERMISSIONS.md)
- [Media Storage Quickstart](MEDIA_STORAGE_QUICKSTART.md)

---

## Revision History
- 2025-05-31: Initial comprehensive draft for SEIM documentation update.
