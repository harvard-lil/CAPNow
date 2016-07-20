from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from api.views import FrontMatterViewSet, BackMatterViewSet, CaseProofViewSet
from . import views

router = routers.DefaultRouter()
router.register(r'volumes', views.VolumeViewSet, 'volumes')
router.register(r'cases', views.CaseViewSet, 'cases')

nested_routers = []

nested_routers.append(NestedSimpleRouter(router, r'volumes', lookup='parent'))
nested_routers[-1].register(r'front_matter_proofs', FrontMatterViewSet)

nested_routers.append(NestedSimpleRouter(router, r'volumes', lookup='parent'))
nested_routers[-1].register(r'back_matter_proofs', BackMatterViewSet)

nested_routers.append(NestedSimpleRouter(router, r'cases', lookup='parent'))
nested_routers[-1].register(r'proofs', CaseProofViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
] + [url(r'^', include(router.urls)) for router in nested_routers]

# Additionally, we include login URLs for the browsable API.
# urlpatterns += [
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
