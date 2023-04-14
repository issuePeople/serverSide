from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'issues', views.IssuesView)

urlpatterns = router.urls
