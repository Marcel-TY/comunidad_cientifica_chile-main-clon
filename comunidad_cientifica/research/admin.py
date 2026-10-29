from django.contrib import admin

from .models import Researcher, ResearchProject, ScientificPublication


@admin.register(Researcher)
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'institution', 'expertise', 'email')
    search_fields = ('full_name', 'institution', 'expertise', 'email')


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'research_area', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'research_area')
    search_fields = ('title', 'summary', 'funder')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('researchers',)


@admin.register(ScientificPublication)
class ScientificPublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'journal', 'publication_date', 'project')
    list_filter = ('publication_date', 'journal')
    search_fields = ('title', 'abstract', 'journal', 'doi')
    filter_horizontal = ('researchers',)
