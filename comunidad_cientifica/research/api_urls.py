from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register('projects', api.ResearchProjectViewSet, basename='research-project')
router.register('researchers', api.ResearcherViewSet, basename='researcher')
router.register('publications', api.ScientificPublicationViewSet, basename='publication')

urlpatterns = [
    path('', api.catalog_data, name='catalog-data'),
    path('session/', api.session_status, name='session-status'),
    path('export.xml', api.export_catalog_xml, name='export-catalog-xml'),
    path('', include(router.urls)),
]
