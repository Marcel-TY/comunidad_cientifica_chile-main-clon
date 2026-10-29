from datetime import date

from django.core.management.base import BaseCommand

from research.models import Researcher, ResearchProject, ScientificPublication


class Command(BaseCommand):
    help = 'Crea registros de demostración identificados como tales para el catálogo científico.'

    def handle(self, *args, **options):
        researcher, _ = Researcher.objects.update_or_create(
            email='investigadora.demo@example.org',
            defaults={
                'full_name': 'Investigadora de demostración',
                'institution': 'Centro de Estudios Científicos (dato de ejemplo)',
                'expertise': 'Ciencias ambientales',
                'biography': 'Registro de demostración; reemplazar con información validada por el centro.',
            },
        )
        project, _ = ResearchProject.objects.update_or_create(
            slug='proyecto-demostracion-ciencia-y-territorio',
            defaults={
                'title': 'Proyecto de demostración: ciencia y territorio',
                'summary': 'Registro de ejemplo para verificar el catálogo y la persistencia.',
                'description': (
                    'Contenido demostrativo. Sustituir por un proyecto aprobado por el centro de estudios.'
                ),
                'research_area': 'Ciencias ambientales',
                'funder': 'Sin financiamiento declarado (ejemplo)',
                'status': ResearchProject.Status.ACTIVE,
                'start_date': date(2025, 1, 1),
            },
        )
        project.researchers.set([researcher])

        publication, _ = ScientificPublication.objects.update_or_create(
            doi='https://example.org/publicaciones/registro-demostrativo',
            defaults={
                'title': 'Publicación científica de demostración',
                'abstract': (
                    'Registro de ejemplo para validar relaciones y persistencia; '
                    'no corresponde a una publicación real.'
                ),
                'journal': 'Revista de demostración',
                'publication_date': date(2025, 6, 1),
                'project': project,
            },
        )
        publication.researchers.set([researcher])
        self.stdout.write(self.style.SUCCESS('Registros de demostración creados o actualizados.'))
