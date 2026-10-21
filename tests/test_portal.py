import re
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.db import DatabaseError
from django.test import Client, TestCase

from portal.models import AuditEvent, Document


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user("alice", password="fictional-test-password")
        cls.bob = User.objects.create_user("bob", password="fictional-test-password")
        cls.reviewer = User.objects.create_user("reviewer", password="fictional-test-password")
        cls.reviewer.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
        cls.a = Document.objects.create(
            title="Alice private title", content="ALICE-SYNTHETIC-CONTENT"
        )
        cls.b = Document.objects.create(title="Bob private title", content="BOB-SYNTHETIC-CONTENT")
        cls.a.assigned_to.add(cls.alice)
        cls.b.assigned_to.add(cls.bob)

    def setUp(self):
        self.client.force_login(self.alice)

    def test_anonymous_routes_require_login(self):
        self.client.logout()
        for url in [
            "/",
            f"/documents/{self.a.pk}/",
            f"/documents/{self.a.pk}/download/",
            "/audit/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_list_only_contains_assignments(self):
        response = self.client.get("/")
        self.assertContains(response, self.a.title)
        self.assertNotContains(response, self.b.title)

    def test_assigned_detail(self):
        self.assertContains(self.client.get(f"/documents/{self.a.pk}/"), self.a.content)

    def test_assigned_download(self):
        response = self.client.get(f"/documents/{self.a.pk}/download/")
        self.assertEqual(response.content.decode(), self.a.content)
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertNotIn(self.a.title, response["Content-Disposition"])

    def test_direct_id_access_is_denied(self):
        for suffix in ["", "download/"]:
            with self.subTest(suffix=suffix):
                response = self.client.get(f"/documents/{self.b.pk}/{suffix}")
                self.assertEqual(response.status_code, 404)
                self.assertNotContains(response, self.b.content, status_code=404)

    def test_missing_and_unassigned_responses_match(self):
        for suffix in ["", "download/"]:
            denied = self.client.get(f"/documents/{self.b.pk}/{suffix}")
            missing = self.client.get(f"/documents/999999/{suffix}")
            self.assertEqual(denied.status_code, missing.status_code)

            def normalize(body):
                return re.sub(rb'value="[a-zA-Z0-9]{64}"', b'value="CSRF"', body)

            self.assertEqual(normalize(denied.content), normalize(missing.content))

    def test_revocation_applies_to_active_session(self):
        self.a.assigned_to.remove(self.alice)
        self.assertEqual(self.client.get(f"/documents/{self.a.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/documents/{self.a.pk}/download/").status_code, 404)

    def test_reviewer_has_no_implicit_document_access(self):
        self.client.force_login(self.reviewer)
        self.assertEqual(self.client.get(f"/documents/{self.a.pk}/").status_code, 404)

    def test_superuser_has_no_implicit_document_access(self):
        self.alice.is_superuser = True
        self.alice.save()
        self.assertEqual(self.client.get(f"/documents/{self.b.pk}/").status_code, 404)

    def test_employee_cannot_read_audit(self):
        self.assertEqual(self.client.get("/audit/").status_code, 403)

    def test_reviewer_can_read_audit(self):
        self.client.get(f"/documents/{self.a.pk}/")
        self.client.force_login(self.reviewer)
        self.assertContains(self.client.get("/audit/"), "document.view")

    def test_audit_records_access_outcomes(self):
        self.client.get(f"/documents/{self.a.pk}/")
        self.client.get(f"/documents/{self.b.pk}/download/")
        self.assertTrue(
            AuditEvent.objects.filter(
                actor_id=self.alice.pk, target_id=self.a.pk, action="document.view", outcome="allow"
            ).exists()
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                actor_id=self.alice.pk,
                target_id=self.b.pk,
                action="document.download",
                outcome="deny",
            ).exists()
        )

    def test_audit_excludes_sensitive_request_and_document_data(self):
        self.client.cookies["extra"] = "FAKE-COOKIE"
        self.client.get(
            f"/documents/{self.a.pk}/?token=FAKE-TOKEN", HTTP_AUTHORIZATION="Bearer FAKE-HEADER"
        )
        serialized = str(list(AuditEvent.objects.values()))
        self.assertTrue(AuditEvent.objects.exists())
        for forbidden in ["FAKE-TOKEN", "FAKE-HEADER", "FAKE-COOKIE", self.a.title, self.a.content]:
            self.assertNotIn(forbidden, serialized)

    def test_audit_failure_prevents_delivery(self):
        with patch(
            "portal.audit.AuditEvent.objects.create", side_effect=DatabaseError("unavailable")
        ):
            response = self.client.get(f"/documents/{self.a.pk}/download/")
        self.assertEqual(response.status_code, 503)
        self.assertNotContains(response, self.a.content, status_code=503)

    def test_document_text_is_escaped(self):
        self.a.content = '<script>alert("synthetic")</script>'
        self.a.save()
        response = self.client.get(f"/documents/{self.a.pk}/")
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_sensitive_pages_are_not_cached(self):
        for url in ["/", f"/documents/{self.a.pk}/", f"/documents/{self.a.pk}/download/"]:
            response = self.client.get(url)
            self.assertIn("no-store", response.get("Cache-Control", ""))
            self.assertEqual(response["X-Content-Type-Options"], "nosniff")
            self.assertEqual(response["X-Frame-Options"], "DENY")

    def test_logout_invalidates_session(self):
        self.assertEqual(self.client.post("/logout/").status_code, 302)
        self.assertEqual(self.client.get(f"/documents/{self.a.pk}/").status_code, 302)

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get("/logout/").status_code, 405)

    def test_csrf_blocks_login_and_logout(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(
            client.post("/login/", {"username": "alice", "password": "x"}).status_code, 403
        )
        client.force_login(self.alice)
        self.assertEqual(client.post("/logout/").status_code, 403)

    def test_read_routes_reject_post(self):
        for url in [
            "/",
            f"/documents/{self.a.pk}/",
            f"/documents/{self.a.pk}/download/",
            "/audit/",
        ]:
            self.assertEqual(self.client.post(url).status_code, 405)

    def test_login_logs_success_without_password(self):
        self.client.logout()
        response = self.client.post(
            "/login/", {"username": "alice", "password": "fictional-test-password"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AuditEvent.objects.filter(action="auth.login", outcome="allow").exists())
        self.assertNotIn("fictional-test-password", str(list(AuditEvent.objects.values())))

    def test_failed_login_logs_no_supplied_identity(self):
        self.client.logout()
        self.client.post("/login/", {"username": "UNTRUSTED-NAME", "password": "BAD-PASSWORD"})
        event = AuditEvent.objects.get(action="auth.login", outcome="deny")
        self.assertIsNone(event.actor_id)
        self.assertNotIn("UNTRUSTED-NAME", str(list(AuditEvent.objects.values())))

    def test_external_login_redirect_rejected(self):
        self.client.logout()
        response = self.client.post(
            "/login/?next=https://example.invalid/",
            {"username": "alice", "password": "fictional-test-password"},
        )
        self.assertEqual(response.url, "/")

    def test_oversized_id_does_not_crash(self):
        self.assertEqual(self.client.get("/documents/" + "9" * 80 + "/").status_code, 404)

    def test_valid_csrf_form_can_log_in(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get("/login/")
        token = (
            re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', page.content)
            .group(1)
            .decode()
        )
        response = client.post(
            "/login/",
            {
                "username": "alice",
                "password": "fictional-test-password",
                "csrfmiddlewaretoken": token,
            },
            HTTP_ORIGIN="http://testserver",
        )
        self.assertEqual(response.status_code, 302)
        self.assertContains(client.get("/"), self.a.title)

    def test_cross_origin_login_rejected_even_with_token(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get("/login/")
        token = (
            re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', page.content)
            .group(1)
            .decode()
        )
        response = client.post(
            "/login/",
            {
                "username": "alice",
                "password": "fictional-test-password",
                "csrfmiddlewaretoken": token,
            },
            HTTP_ORIGIN="https://example.invalid",
        )
        self.assertEqual(response.status_code, 403)

    def test_logout_still_works_when_audit_is_unavailable(self):
        with patch(
            "portal.audit.AuditEvent.objects.create", side_effect=DatabaseError("unavailable")
        ):
            self.assertEqual(self.client.post("/logout/").status_code, 302)
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_inactive_user_cannot_sign_in(self):
        self.client.logout()
        self.alice.is_active = False
        self.alice.save()
        response = self.client.post(
            "/login/", {"username": "alice", "password": "fictional-test-password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/").status_code, 302)
