from rest_framework import routers, permissions
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Issue People",
      default_version='v1',
      description="API desenvolupada pel segon lliurament del projecte d'ASW",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register(r'issues', views.IssuesView)

urlpatterns = [
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += router.urls
