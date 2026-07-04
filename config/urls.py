from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from patients.views import PatientViewSet
from appointments.views import AppointmentViewSet
from therapy_sessions.views import TherapySessionViewSet
from finances.views import PaymentViewSet

#Cria automaticamente as URLs (endpoints)
router = DefaultRouter()

router.register(r"patients", PatientViewSet)
router.register(r"appointments", AppointmentViewSet)
router.register(r"therapy-sessions", TherapySessionViewSet)
router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),

    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
]
