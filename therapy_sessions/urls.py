from rest_framework.routers import DefaultRouter
from .views import TherapySessionViewSet

router = DefaultRouter()
router.register (
    "therapy-sessions",
    TherapySessionViewSet
)

urlspatterns = router.urls