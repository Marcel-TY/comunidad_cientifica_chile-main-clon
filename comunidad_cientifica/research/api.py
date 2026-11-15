from xml.etree.ElementTree import Element, SubElement, tostring

from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import ResearchProject, Researcher, ScientificPublication
from .serializers import (
    ResearchProjectSerializer,
    ResearcherSerializer,
    ScientificPublicationSerializer,
)


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or bool(request.user and request.user.is_authenticated and request.user.is_staff)
        )


class StaffManagedModelViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsStaffOrReadOnly,)


class ResearcherViewSet(StaffManagedModelViewSet):
    queryset = Researcher.objects.all()
    serializer_class = ResearcherSerializer


class ResearchProjectViewSet(StaffManagedModelViewSet):
    queryset = ResearchProject.objects.prefetch_related('researchers').all()
    serializer_class = ResearchProjectSerializer


class ScientificPublicationViewSet(StaffManagedModelViewSet):
    queryset = ScientificPublication.objects.select_related('project').prefetch_related(
        'researchers'
    )
    serializer_class = ScientificPublicationSerializer


@api_view(('GET',))
@permission_classes((permissions.AllowAny,))
def catalog_data(request):
    return Response({
        'projects': ResearchProjectSerializer(
            ResearchProjectViewSet.queryset.all(), many=True
        ).data,
        'researchers': ResearcherSerializer(Researcher.objects.all(), many=True).data,
        'publications': ScientificPublicationSerializer(
            ScientificPublicationViewSet.queryset.all(), many=True
        ).data,
    })


@api_view(('GET',))
@permission_classes((permissions.AllowAny,))
def session_status(request):
    user = request.user
    return Response({
        'authenticated': bool(user and user.is_authenticated),
        'isStaff': bool(user and user.is_authenticated and user.is_staff),
    })


@api_view(('GET',))
@permission_classes((permissions.AllowAny,))
def export_catalog_xml(request):
    root = Element('researchCatalog')
    projects_node = SubElement(root, 'projects')
    for project in ResearchProject.objects.prefetch_related('researchers').all():
        node = SubElement(projects_node, 'project', id=str(project.pk))
        for field, value in (
            ('title', project.title),
            ('summary', project.summary),
            ('researchArea', project.research_area),
            ('status', project.get_status_display()),
        ):
            SubElement(node, field).text = value
        researchers_node = SubElement(node, 'researchers')
        for researcher in project.researchers.all():
            SubElement(researchers_node, 'researcher', id=str(researcher.pk)).text = (
                researcher.full_name
            )

    researchers_node = SubElement(root, 'researchers')
    for researcher in Researcher.objects.all():
        node = SubElement(researchers_node, 'researcher', id=str(researcher.pk))
        SubElement(node, 'fullName').text = researcher.full_name
        SubElement(node, 'institution').text = researcher.institution
        SubElement(node, 'expertise').text = researcher.expertise

    publications_node = SubElement(root, 'publications')
    for publication in ScientificPublication.objects.select_related('project').prefetch_related(
        'researchers'
    ):
        node = SubElement(publications_node, 'publication', id=str(publication.pk))
        SubElement(node, 'title').text = publication.title
        SubElement(node, 'journal').text = publication.journal
        SubElement(node, 'publicationDate').text = publication.publication_date.isoformat()
        if publication.project:
            SubElement(node, 'project').text = publication.project.title
        authors_node = SubElement(node, 'authors')
        for researcher in publication.researchers.all():
            SubElement(authors_node, 'author').text = researcher.full_name

    return HttpResponse(
        tostring(root, encoding='utf-8', xml_declaration=True),
        content_type='application/xml; charset=utf-8',
    )
