from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .audit import record
from .models import AuditEvent, Document


def audited(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except DatabaseError:
            return HttpResponse(
                "Service temporarily unavailable. Please try again later.", status=503
            )

    return wrapped


def assigned_document(request, pk, action):
    document = Document.objects.filter(pk=pk, assigned_to=request.user).first()
    record(
        actor_id=request.user.pk,
        target_id=pk,
        action=action,
        outcome="allow" if document else "deny",
    )
    return document


class PortalLogin(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        try:
            record(actor_id=form.get_user().pk, action="auth.login", outcome="allow")
        except DatabaseError:
            return HttpResponse("Service temporarily unavailable.", status=503)
        return super().form_valid(form)

    def form_invalid(self, form):
        try:
            record(actor_id=None, action="auth.login", outcome="deny")
        except DatabaseError:
            return HttpResponse("Service temporarily unavailable.", status=503)
        return super().form_invalid(form)


class PortalLogout(LogoutView):
    def post(self, request, *args, **kwargs):
        # Logout must still terminate a session if the audit store is unavailable.
        try:
            record(actor_id=request.user.pk, action="auth.logout", outcome="allow")
        except DatabaseError:
            pass
        return super().post(request, *args, **kwargs)


@require_GET
@login_required
@audited
def document_list(request):
    record(actor_id=request.user.pk, action="document.list", outcome="allow")
    return render(
        request,
        "portal/documents.html",
        {"documents": Document.objects.filter(assigned_to=request.user)},
    )


@require_GET
@login_required
@audited
def document_detail(request, pk):
    document = assigned_document(request, pk, "document.view")
    if document is None:
        return render(request, "404.html", status=404)
    return render(request, "portal/detail.html", {"document": document})


@require_GET
@login_required
@audited
def document_download(request, pk):
    document = assigned_document(request, pk, "document.download")
    if document is None:
        return render(request, "404.html", status=404)
    response = HttpResponse(document.content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="document-{document.pk}.txt"'
    return response


@require_GET
@login_required
@audited
def audit_list(request):
    allowed = request.user.has_perm("portal.view_auditevent")
    record(actor_id=request.user.pk, action="audit.view", outcome="allow" if allowed else "deny")
    if not allowed:
        return render(request, "403.html", status=403)
    return render(request, "portal/audit.html", {"events": AuditEvent.objects.all()[:100]})
