from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from patients.views import PatientViewSet
from appointments.views import AppointmentViewSet
from therapy_sessions.views import TherapySessionViewSet
from finances.views import PaymentViewSet

from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "ok"})

from patients.views import PatientViewSet, ChangePasswordView

#Cria automaticamente as URLs (endpoints)
router = DefaultRouter()

router.register(r"patients", PatientViewSet)
router.register(r"appointments", AppointmentViewSet)
router.register(r"therapy-sessions", TherapySessionViewSet)
router.register(r"payments", PaymentViewSet)

from rest_framework.throttling import ScopedRateThrottle

class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),

    path("api/token/", ThrottledTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/change-password/", ChangePasswordView.as_view()),

    path("health/", health_check),
]
