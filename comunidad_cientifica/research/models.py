from django.db import models


class Researcher(models.Model):
    full_name = models.CharField('nombre completo', max_length=200)
    email = models.EmailField('correo electrónico', unique=True)
    institution = models.CharField('institución', max_length=200)
    expertise = models.CharField('área de especialidad', max_length=200)
    biography = models.TextField('biografía', blank=True)
    orcid = models.CharField('ORCID', max_length=19, blank=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'investigador/a'
        verbose_name_plural = 'investigadores/as'

    def __str__(self):
        return self.full_name


class ResearchProject(models.Model):
    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Propuesto'
        ACTIVE = 'active', 'En curso'
        COMPLETED = 'completed', 'Finalizado'

    title = models.CharField('nombre del proyecto', max_length=240)
    slug = models.SlugField(unique=True)
    summary = models.CharField('resumen', max_length=400)
    description = models.TextField('descripción')
    research_area = models.CharField('área de investigación', max_length=160)
    funder = models.CharField('entidad financiadora', max_length=200, blank=True)
    status = models.CharField(
        'estado',
        max_length=12,
        choices=Status.choices,
        default=Status.PROPOSED,
    )
    start_date = models.DateField('fecha de inicio', null=True, blank=True)
    end_date = models.DateField('fecha de término', null=True, blank=True)
    researchers = models.ManyToManyField(
        Researcher,
        related_name='projects',
        verbose_name='equipo investigador',
        blank=True,
    )
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        ordering = ['-created_at', 'title']
        verbose_name = 'proyecto de investigación'
        verbose_name_plural = 'proyectos de investigación'

    def __str__(self):
        return self.title


class ScientificPublication(models.Model):
    title = models.CharField('título', max_length=300)
    abstract = models.TextField('resumen')
    journal = models.CharField('revista o editorial', max_length=240)
    doi = models.URLField('DOI o enlace permanente', blank=True)
    publication_date = models.DateField('fecha de publicación')
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.SET_NULL,
        related_name='publications',
        verbose_name='proyecto relacionado',
        null=True,
        blank=True,
    )
    researchers = models.ManyToManyField(
        Researcher,
        related_name='publications',
        verbose_name='autores/as',
    )
    created_at = models.DateTimeField('registrado', auto_now_add=True)

    class Meta:
        ordering = ['-publication_date', 'title']
        verbose_name = 'publicación científica'
        verbose_name_plural = 'publicaciones científicas'

    def __str__(self):
        return self.title
