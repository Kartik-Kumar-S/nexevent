from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet, CertificateTemplateViewSet

router = DefaultRouter()
router.register(r'templates', CertificateTemplateViewSet, basename='certificate-template')
router.register(r'', CertificateViewSet, basename='certificate')

urlpatterns = [
    path('', include(router.urls)),
]