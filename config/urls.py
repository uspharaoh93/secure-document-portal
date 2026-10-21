from django.urls import path

from portal import views

urlpatterns = [
    path("", views.document_list, name="documents"),
    path("login/", views.PortalLogin.as_view(), name="login"),
    path("logout/", views.PortalLogout.as_view(), name="logout"),
    path("documents/<int:pk>/", views.document_detail, name="document"),
    path("documents/<int:pk>/download/", views.document_download, name="download"),
    path("audit/", views.audit_list, name="audit"),
]
