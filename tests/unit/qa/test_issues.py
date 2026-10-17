import io
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from notifications.models import Notification
from qa.models import Issue, IssueAttachment

from .conftest import client_for

# Built at runtime so secret scanners do not flag the fixture.
FAKE_JWT = ".".join(
    ["eyJ" + "hbGciOiJIUzI1NiJ9", "eyJ" + "zdWIiOiIxMjM0NSJ9", "abcdefghijk"]
)

pytestmark = pytest.mark.django_db


def _payload(**extra):
    data = {
        "title": "Save button does nothing",
        "description": "Clicking save on profile does nothing",
        "steps": "1. open profile 2. click save",
        "severity": "major",
        "kind": "bug",
        "page_url": "https://seim.example/seim/profile?token=abc123&tab=2",
        "route_name": "Profile",
        "viewport": "1280x720@2",
        "locale": "es",
        "app_version": "1.0.0",
        "build_commit": "abc1234",
    }
    data.update(extra)
    return data


def _post(user, data, fmt="json", **claims):
    return client_for(user, **claims).post("/api/qa/issues/", data, format=fmt)


def test_tester_creates_issue_with_screenshot(
    tools_on,
    tester,
    admin_tester,
    png_file,
    settings,
    tmp_path,
    django_capture_on_commit_callbacks,
):
    settings.MEDIA_ROOT = tmp_path
    diagnostics = {
        "consoleErrors": [
            {
                "level": "error",
                "message": "boom " + FAKE_JWT,
            }
        ],
        "failedRequests": [
            {
                "method": "GET",
                "url": "/api/x/?password=hunter2",
                "status": 500,
                "headers": {"Authorization": "x"},
            }
        ],
    }
    with django_capture_on_commit_callbacks(execute=True):
        resp = _post(
            tester,
            {**_payload(), "diagnostics": json.dumps(diagnostics), "files": [png_file]},
            "multipart",
        )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["reference"].startswith("QA-")
    assert body["reporter"]["email"] == tester.email
    assert body["reporter_role"] == "student"
    assert body["deploy_tier"] == "test"
    assert "abc123" not in body["page_url"]
    assert "tab=2" in body["page_url"]
    diag = body["diagnostics"]
    assert "redacted-jwt" in diag["consoleErrors"][0]["message"]
    assert "hunter2" not in diag["failedRequests"][0]["url"]
    assert "headers" not in diag["failedRequests"][0]
    assert len(body["attachments"]) == 1
    att = body["attachments"][0]
    assert att["content_type"] == "image/png" and att["kind"] == "screenshot"
    assert Notification.objects.filter(recipient=admin_tester).exists()


def test_non_image_with_png_extension_rejected(tools_on, tester):
    bad = SimpleUploadedFile(
        "evil.png", b"<script>alert(1)</script>", content_type="image/png"
    )
    assert _post(tester, {**_payload(), "files": [bad]}, "multipart").status_code == 400
    assert Issue.objects.count() == 0


@pytest.mark.parametrize("name", ["x.svg", "x.html", "x.exe", "x.pdf"])
def test_disallowed_types(tools_on, tester, name):
    f = SimpleUploadedFile(name, b"hello", content_type="application/octet-stream")
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_oversize_image_rejected(tools_on, tester, settings):
    settings.QA_MAX_IMAGE_MB = 0
    f = SimpleUploadedFile("a.png", b"\x89PNG....", content_type="image/png")
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_oversize_video_rejected(tools_on, tester, settings):
    settings.QA_MAX_VIDEO_MB = 0
    f = SimpleUploadedFile(
        "a.webm", b"\x1a\x45\xdf\xa3" + b"0" * 20, content_type="video/webm"
    )
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_binary_text_rejected(tools_on, tester):
    f = SimpleUploadedFile("a.log", b"abc\x00def", content_type="text/plain")
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_non_utf8_text_rejected(tools_on, tester):
    f = SimpleUploadedFile("a.txt", b"\xff\xfe\xfa\xfb" * 10, content_type="text/plain")
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_too_many_files(tools_on, tester, settings, png_file):
    settings.QA_MAX_ATTACHMENTS = 1
    f2 = SimpleUploadedFile("b.txt", b"log line", content_type="text/plain")
    assert (
        _post(tester, {**_payload(), "files": [png_file, f2]}, "multipart").status_code
        == 400
    )


def test_webm_and_text_accepted(tools_on, tester, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    webm = SimpleUploadedFile(
        "rec.webm", b"\x1a\x45\xdf\xa3" + b"\x00" * 100, content_type="video/webm"
    )
    log = SimpleUploadedFile(
        "console.log", "línea de log".encode(), content_type="text/plain"
    )
    resp = _post(tester, {**_payload(), "files": [webm, log]}, "multipart")
    assert resp.status_code == 201, resp.content
    kinds = sorted(a["kind"] for a in resp.json()["attachments"])
    assert kinds == ["log", "recording"]


def test_fake_mp4_rejected(tools_on, tester):
    f = SimpleUploadedFile("rec.mp4", b"not a video at all", content_type="video/mp4")
    assert _post(tester, {**_payload(), "files": [f]}, "multipart").status_code == 400


def test_json_create_without_files(tools_on, tester):
    assert _post(tester, _payload()).status_code == 201


def test_title_required(tools_on, tester):
    assert _post(tester, _payload(title="  ")).status_code == 400


def test_tester_sees_only_own_issues_triager_sees_all(
    tools_on, tester, admin_tester, make_user
):
    other = make_user("other.tester@example.com", role="student", is_tester=True)
    _post(tester, _payload(title="mine"))
    _post(other, _payload(title="theirs"))
    mine = client_for(tester).get("/api/qa/issues/").json()
    assert [r["title"] for r in mine.get("results", mine)] == ["mine"]
    allr = client_for(admin_tester).get("/api/qa/issues/").json()
    assert len(allr.get("results", allr)) == 2
    mine_only = client_for(admin_tester).get("/api/qa/issues/?mine=1").json()
    assert len(mine_only.get("results", mine_only)) == 0
    theirs = Issue.objects.get(title="theirs")
    assert client_for(tester).get(f"/api/qa/issues/{theirs.pk}/").status_code == 404


def test_open_filter(tools_on, tester, admin_tester):
    a = _post(tester, _payload(title="a")).json()
    _post(tester, _payload(title="b"))
    client_for(admin_tester).patch(
        f"/api/qa/issues/{a['id']}/", {"status": "closed"}, format="json"
    )
    data = client_for(tester).get("/api/qa/issues/?open=1").json()
    assert [r["title"] for r in data.get("results", data)] == ["b"]


def test_numbers_are_sequential(tools_on, tester):
    a = _post(tester, _payload(title="a")).json()
    b = _post(tester, _payload(title="b")).json()
    assert b["number"] == a["number"] + 1


def test_reporter_can_edit_only_while_new(tools_on, tester, admin_tester):
    issue = _post(tester, _payload()).json()
    url = f"/api/qa/issues/{issue['id']}/"
    r = client_for(tester).patch(
        url, {"title": "Better title", "status": "closed"}, format="json"
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Better title"
    assert r.json()["status"] == "new"
    r = client_for(admin_tester).patch(url, {"status": "triaged"}, format="json")
    assert r.status_code == 200 and r.json()["status"] == "triaged"
    assert any(c["is_system"] for c in r.json()["comments"])
    assert Notification.objects.filter(recipient=tester).exists()
    assert (
        client_for(tester).patch(url, {"title": "nope"}, format="json").status_code
        == 400
    )


def test_triager_assign_and_duplicate(tools_on, tester, admin_tester):
    a = _post(tester, _payload(title="a")).json()
    b = _post(tester, _payload(title="b")).json()
    r = client_for(admin_tester).patch(
        f"/api/qa/issues/{b['id']}/",
        {
            "status": "duplicate",
            "duplicate_of_number": a["number"],
            "assignee_id": str(admin_tester.pk),
        },
        format="json",
    )
    assert r.status_code == 200, r.content
    assert r.json()["duplicate_of_reference"] == a["reference"]
    assert r.json()["assignee"]["email"] == admin_tester.email
    r = client_for(admin_tester).patch(
        f"/api/qa/issues/{b['id']}/",
        {"duplicate_of_number": b["number"]},
        format="json",
    )
    assert r.status_code == 400
    r = client_for(admin_tester).patch(
        f"/api/qa/issues/{b['id']}/", {"duplicate_of_number": 99999}, format="json"
    )
    assert r.status_code == 400


def test_internal_comments_hidden_from_reporter(tools_on, tester, admin_tester):
    issue = _post(tester, _payload()).json()
    url = f"/api/qa/issues/{issue['id']}/comments/"
    assert (
        client_for(admin_tester)
        .post(url, {"body": "internal", "is_internal": True}, format="json")
        .status_code
        == 201
    )
    assert (
        client_for(tester)
        .post(url, {"body": "public", "is_internal": True}, format="json")
        .status_code
        == 201
    )
    assert (
        client_for(tester).post(url, {"body": "   "}, format="json").status_code == 400
    )
    seen = client_for(tester).get(f"/api/qa/issues/{issue['id']}/").json()["comments"]
    assert [c["body"] for c in seen] == ["public"]
    assert seen[0]["is_internal"] is False
    assert (
        len(
            client_for(admin_tester)
            .get(f"/api/qa/issues/{issue['id']}/")
            .json()["comments"]
        )
        == 2
    )


def test_add_attachment_and_download(
    tools_on, tester, plain_user, png_file, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    issue = _post(tester, _payload()).json()
    r = client_for(tester).post(
        f"/api/qa/issues/{issue['id']}/attachments/",
        {"files": [png_file]},
        format="multipart",
    )
    assert r.status_code == 201, r.content
    att = r.json()[0]
    dl = client_for(tester).get(att["download_url"])
    assert dl.status_code == 200
    assert dl["Content-Type"] == "image/png"
    assert dl["X-Content-Type-Options"] == "nosniff"
    assert b"".join(dl.streaming_content).startswith(b"\x89PNG")
    assert client_for(plain_user).get(att["download_url"]).status_code == 404
    empty = client_for(tester).post(
        f"/api/qa/issues/{issue['id']}/attachments/", {}, format="multipart"
    )
    assert empty.status_code == 400


def test_attachment_limit_on_add(tools_on, tester, png_file, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.QA_MAX_ATTACHMENTS = 1
    issue = _post(tester, {**_payload(), "files": [png_file]}, "multipart").json()
    more = SimpleUploadedFile("b.txt", b"x", content_type="text/plain")
    r = client_for(tester).post(
        f"/api/qa/issues/{issue['id']}/attachments/",
        {"files": [more]},
        format="multipart",
    )
    assert r.status_code == 400


def test_image_metadata_is_stripped(tools_on, tester, settings, tmp_path):
    from PIL import Image

    settings.MEDIA_ROOT = tmp_path
    buf = io.BytesIO()
    img = Image.new("RGB", (8, 8))
    exif = img.getexif()
    exif[0x010E] = "secret-description"
    img.save(buf, format="JPEG", exif=exif)
    assert b"secret-description" in buf.getvalue()
    f = SimpleUploadedFile("photo.jpeg", buf.getvalue(), content_type="image/jpeg")
    r = _post(tester, {**_payload(), "files": [f]}, "multipart")
    assert r.status_code == 201, r.content
    att = IssueAttachment.objects.get()
    assert b"secret-description" not in att.file.read()


def test_issue_from_switched_demo_session_is_attributed_to_tester(
    tools_on, tester, make_user
):
    demo = make_user("demo.partner@example.com", role="partner", is_demo_account=True)
    r = _post(demo, _payload(), qa_switched_from=str(tester.pk))
    assert r.status_code == 201
    body = r.json()
    assert body["reporter"]["email"] == tester.email
    assert body["acting_as"]["email"] == demo.email
    assert body["reporter_role"] == "partner"


def test_admin_changelist_and_actions(tools_on, admin_tester, tester, client):
    _post(tester, _payload())
    admin_tester.is_superuser = True
    admin_tester.save()
    client.force_login(admin_tester)
    assert client.get("/seim/django-admin/qa/issue/").status_code == 200
    issue = Issue.objects.get()
    assert (
        client.get(f"/seim/django-admin/qa/issue/{issue.pk}/change/").status_code == 200
    )
    r = client.post(
        "/seim/django-admin/qa/issue/",
        {"action": "mark_fixed", "_selected_action": [str(issue.pk)]},
    )
    assert r.status_code == 302
    issue.refresh_from_db()
    assert issue.status == "fixed"
    client.post(
        "/seim/django-admin/qa/issue/",
        {"action": "assign_to_me", "_selected_action": [str(issue.pk)]},
    )
    issue.refresh_from_db()
    assert issue.assignee_id == admin_tester.pk


def test_user_admin_tester_actions(admin_tester, plain_user, client):
    admin_tester.is_superuser = True
    admin_tester.save()
    client.force_login(admin_tester)
    url = "/seim/django-admin/accounts/user/"
    client.post(
        url, {"action": "mark_as_tester", "_selected_action": [str(plain_user.pk)]}
    )
    plain_user.refresh_from_db()
    assert plain_user.is_tester is True
    client.post(
        url, {"action": "remove_tester", "_selected_action": [str(plain_user.pk)]}
    )
    plain_user.refresh_from_db()
    assert plain_user.is_tester is False
    assert client.get(f"{url}?is_tester__exact=1").status_code == 200
