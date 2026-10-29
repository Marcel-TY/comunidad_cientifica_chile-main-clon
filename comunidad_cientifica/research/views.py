from django.shortcuts import render

from .models import ResearchProject, Researcher, ScientificPublication


def catalog(request):
    projects = ResearchProject.objects.prefetch_related('researchers').all()
    researchers = Researcher.objects.all()
    publications = ScientificPublication.objects.select_related(
        'project'
    ).prefetch_related('researchers')

    research_data = {
        'projects': [
            {
                'id': project.id,
                'title': project.title,
                'summary': project.summary,
                'description': project.description,
                'researchArea': project.research_area,
                'funder': project.funder,
                'status': project.get_status_display(),
                'researcherIds': [
                    researcher.id for researcher in project.researchers.all()
                ],
            }
            for project in projects
        ],
        'researchers': [
            {
                'id': researcher.id,
                'fullName': researcher.full_name,
                'institution': researcher.institution,
                'expertise': researcher.expertise,
                'biography': researcher.biography,
            }
            for researcher in researchers
        ],
        'publications': [
            {
                'id': publication.id,
                'title': publication.title,
                'abstract': publication.abstract,
                'journal': publication.journal,
                'doi': publication.doi,
                'publicationDate': publication.publication_date.isoformat(),
                'projectTitle': publication.project.title if publication.project else '',
                'researcherNames': [
                    researcher.full_name for researcher in publication.researchers.all()
                ],
            }
            for publication in publications
        ],
    }
    return render(request, 'sections/research_catalog.html', {'research_data': research_data})
