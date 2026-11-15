from django.utils.text import slugify
from rest_framework import serializers

from .models import ResearchProject, Researcher, ScientificPublication


class ResearcherSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='full_name')
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Researcher
        fields = (
            'id',
            'fullName',
            'email',
            'institution',
            'expertise',
            'biography',
            'orcid',
        )
        read_only_fields = ('id',)


class ResearchProjectSerializer(serializers.ModelSerializer):
    researchArea = serializers.CharField(source='research_area')
    statusLabel = serializers.CharField(source='get_status_display', read_only=True)
    researcherIds = serializers.PrimaryKeyRelatedField(
        source='researchers',
        queryset=Researcher.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = ResearchProject
        fields = (
            'id',
            'title',
            'slug',
            'summary',
            'description',
            'researchArea',
            'funder',
            'status',
            'statusLabel',
            'start_date',
            'end_date',
            'researcherIds',
        )
        read_only_fields = ('id', 'statusLabel')
        extra_kwargs = {'slug': {'required': False, 'allow_blank': True}}

    def create(self, validated_data):
        if not validated_data.get('slug'):
            base_slug = slugify(validated_data['title']) or 'proyecto'
            slug = base_slug
            suffix = 2
            while ResearchProject.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{suffix}'
                suffix += 1
            validated_data['slug'] = slug
        return super().create(validated_data)


class ScientificPublicationSerializer(serializers.ModelSerializer):
    publicationDate = serializers.DateField(source='publication_date')
    projectId = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=ResearchProject.objects.all(),
        allow_null=True,
        required=False,
    )
    projectTitle = serializers.CharField(
        source='project.title',
        read_only=True,
        allow_null=True,
    )
    researcherIds = serializers.PrimaryKeyRelatedField(
        source='researchers',
        queryset=Researcher.objects.all(),
        many=True,
    )
    researcherNames = serializers.SlugRelatedField(
        source='researchers',
        many=True,
        read_only=True,
        slug_field='full_name',
    )

    class Meta:
        model = ScientificPublication
        fields = (
            'id',
            'title',
            'abstract',
            'journal',
            'doi',
            'publicationDate',
            'projectId',
            'projectTitle',
            'researcherIds',
            'researcherNames',
        )
        read_only_fields = ('id', 'projectTitle', 'researcherNames')
