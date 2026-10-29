from datetime import date

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

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

    def test_catalog_renders_orm_data_for_angular(self):
        response = self.client.get(reverse('research:catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'app-root')
        self.assertContains(response, 'research-data')
        data = response.context['research_data']
        self.assertEqual(data['projects'][0]['title'], self.project.title)
        self.assertEqual(data['projects'][0]['researcherIds'], [self.researcher.id])
        self.assertEqual(data['publications'][0]['researcherNames'], [self.researcher.full_name])

    def test_catalog_handles_empty_database(self):
        ScientificPublication.objects.all().delete()
        ResearchProject.objects.all().delete()
        Researcher.objects.all().delete()

        response = self.client.get(reverse('research:catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['research_data'], {
            'projects': [],
            'researchers': [],
            'publications': [],
        })


class ResearchAdminTests(TestCase):
    def test_models_are_available_in_admin(self):
        self.assertIn(Researcher, admin.site._registry)
        self.assertIn(ResearchProject, admin.site._registry)
        self.assertIn(ScientificPublication, admin.site._registry)
