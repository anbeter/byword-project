from rest_framework.routers import DefaultRouter
from .views import WordSearchViewSet

router = DefaultRouter()
router.register(r'wordsearch', WordSearchViewSet)

urlpatterns = router.urls