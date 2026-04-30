from rest_framework.routers import DefaultRouter
from .views import WordSearchViewSet, ScrambleWordViewSet

router = DefaultRouter()
router.register(r'wordsearch', WordSearchViewSet)
router.register(r'scrambleword', ScrambleWordViewSet)


urlpatterns = router.urls