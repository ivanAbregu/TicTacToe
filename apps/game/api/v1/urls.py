from rest_framework.routers import SimpleRouter

from .views import gameViewSet

router = SimpleRouter()

router.register("game", gameViewSet)

urlpatterns = router.urls
