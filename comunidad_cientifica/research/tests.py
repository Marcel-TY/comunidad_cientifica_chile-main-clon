from datetime import date
from xml.etree import ElementTree

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Researcher, ResearchProject, ScientificPublication


class ResearchCatalogTests(TestCase):
    def setUp(self):
        self.researcher = Researcher.objects.create(
            full_name='Investigadora de prueba',
            email='researcher@example.org',
            institution='Institución de prueba',
            expertise='Ecología',
        )
        self.project = ResearchProject.objects.create(
            title='Proyecto de prueba',
            slug='proyecto-de-prueba',
            summary='Resumen de prueba.',
            description='Descripción de prueba.',
            research_area='Ecología',
            status=ResearchProject.Status.ACTIVE,
        )
        self.project.researchers.add(self.researcher)
        self.publication = ScientificPublication.objects.create(
            title='Publicación de prueba',
            abstract='Resumen científico de prueba.',
            journal='Revista de prueba',
            doi='https://example.org/doi/1',
            publication_date=date(2025, 5, 1),
            project=self.project,
        )
        self.publication.researchers.add(self.researcher)

    def test_research_models_keep_domain_relationships(self):
        self.assertEqual(list(self.project.researchers.all()), [self.researcher])
        self.assertEqual(self.publication.project, self.project)
        self.assertEqual(list(self.publication.researchers.all()), [self.researcher])

    def test_catalog_renders_angular_shell_and_sets_csrf_cookie(self):
        response = self.client.get(reverse('research:catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'app-root')
        self.assertIn('csrftoken', response.cookies)

    def test_rest_catalog_returns_orm_data_as_json(self):
        response = self.client.get('/api/research/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['projects'][0]['title'], self.project.title)
        self.assertEqual(response.json()['projects'][0]['researcherIds'], [self.researcher.id])
        self.assertEqual(
            response.json()['publications'][0]['researcherNames'],
            [self.researcher.full_name],
        )


class ResearchAdminTests(TestCase):
    def test_models_are_available_in_admin(self):
        self.assertIn(Researcher, admin.site._registry)
        self.assertIn(ResearchProject, admin.site._registry)
        self.assertIn(ScientificPublication, admin.site._registry)


class ResearchApiPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.project_payload = {
            'title': 'Nuevo proyecto',
            'summary': 'Resumen.',
            'description': 'Descripción.',
            'researchArea': 'Ecología',
            'status': ResearchProject.Status.PROPOSED,
            'researcherIds': [],
        }

    def test_anonymous_users_can_read_but_cannot_create(self):
        response = self.client.get('/api/research/projects/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/api/research/projects/',
            self.project_payload,
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_non_staff_users_cannot_write(self):
        user = get_user_model().objects.create_user(
            username='member',
            password='test-password',
        )
        self.client.force_login(user)
        csrf_response = self.client.get(reverse('research:catalog'))
        csrf_token = csrf_response.cookies['csrftoken'].value

        response = self.client.post(
            '/api/research/projects/',
            self.project_payload,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_writes_require_csrf_and_create_project(self):
        admin_user = get_user_model().objects.create_user(
            username='editor',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            '/api/research/projects/',
            self.project_payload,
            format='json',
        )
        self.assertEqual(response.status_code, 403)

        csrf_response = self.client.get(reverse('research:catalog'))
        csrf_token = csrf_response.cookies['csrftoken'].value
        response = self.client.post(
            '/api/research/projects/',
            self.project_payload,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ResearchProject.objects.filter(slug='nuevo-proyecto').exists()
        )

    def test_staff_can_create_researcher_and_publication_through_api(self):
        admin_user = get_user_model().objects.create_user(
            username='scientific-editor',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(admin_user)
        csrf_response = self.client.get(reverse('research:catalog'))
        csrf_token = csrf_response.cookies['csrftoken'].value

        researcher_response = self.client.post(
            '/api/research/researchers/',
            {
                'fullName': 'Investigador API',
                'email': 'api-researcher@example.org',
                'institution': 'Centro de estudios',
                'expertise': 'Ciencia de datos',
                'biography': '',
                'orcid': '',
            },
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(researcher_response.status_code, 201)
        researcher_id = researcher_response.json()['id']
        self.assertNotIn('email', researcher_response.json())

        publication_response = self.client.post(
            '/api/research/publications/',
            {
                'title': 'Publicación API',
                'abstract': 'Resumen.',
                'journal': 'Revista científica',
                'doi': '',
                'publicationDate': '2026-01-15',
                'projectId': None,
                'researcherIds': [researcher_id],
            },
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(publication_response.status_code, 201)
        self.assertEqual(
            publication_response.json()['researcherNames'],
            ['Investigador API'],
        )

    def test_staff_can_update_and_delete_project(self):
        admin_user = get_user_model().objects.create_user(
            username='manager',
            password='test-password',
            is_staff=True,
        )
        project = ResearchProject.objects.create(
            title='Proyecto editable',
            slug='proyecto-editable',
            summary='Resumen.',
            description='Descripción.',
            research_area='Ecología',
        )
        self.client.force_login(admin_user)
        csrf_response = self.client.get(reverse('research:catalog'))
        csrf_token = csrf_response.cookies['csrftoken'].value

        response = self.client.patch(
            f'/api/research/projects/{project.pk}/',
            {'summary': 'Resumen actualizado.'},
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.summary, 'Resumen actualizado.')

        response = self.client.delete(
            f'/api/research/projects/{project.pk}/',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ResearchProject.objects.filter(pk=project.pk).exists())

    def test_xml_export_is_valid_and_does_not_expose_researcher_email(self):
        researcher = Researcher.objects.create(
            full_name='Autora XML',
            email='autora@example.org',
            institution='Institución',
            expertise='Ciencia',
        )
        project = ResearchProject.objects.create(
            title='Proyecto & ciencia',
            slug='proyecto-ciencia',
            summary='Resumen.',
            description='Descripción.',
            research_area='Ciencia',
        )
        project.researchers.add(researcher)
        response = self.client.get('/api/research/export.xml')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml; charset=utf-8')
        document = ElementTree.fromstring(response.content)
        self.assertEqual(document.tag, 'researchCatalog')
        self.assertEqual(
            document.findtext('./projects/project/title'),
            'Proyecto & ciencia',
        )
        self.assertNotIn(researcher.email.encode(), response.content)
