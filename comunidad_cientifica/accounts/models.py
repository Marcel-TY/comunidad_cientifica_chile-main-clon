from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    """Usuario personalizado con roles y estado de aprobación."""
    USER_TYPE_CHOICES = (
        ('investigador', 'Investigador'),
        ('empresa', 'Empresa'),
        ('admin', 'Administrador'),
        ('moderador', 'Moderador'),
        ('visitante', 'Visitante'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='visitante')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False, help_text="Usuario aprobado para publicar ofertas")
    verification_badge = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Advertisement(models.Model):
    """Publicidades/anuncios en carrusel y banners."""
    POSITION_CHOICES = (
        ('hero_carousel', 'Carrusel Principal'),
        ('sidebar', 'Barra Lateral'),
        ('banner_top', 'Banner Superior'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='advertisements/', blank=True, null=True)
    video = models.FileField(upload_to='advertisements/videos/', blank=True, null=True)
    link_url = models.URLField()
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='hero_carousel')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class JobOffer(models.Model):
    """Ofertas laborales publicadas por usuarios aprobados."""
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('pending', 'Pendiente Aprobación'),
        ('active', 'Activo'),
        ('closed', 'Cerrado'),
        ('rejected', 'Rechazado'),
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=[
        ('postdoc', 'Postdoctorado'),
        ('researcher', 'Investigador'),
        ('internship', 'Pasantía'),
        ('academic', 'Académico'),
        ('industry', 'Industria'),
    ])
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    published_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_offers')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=0)
    applications = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.institution}"


class BlogPost(models.Model):
    """Publicaciones de blog."""
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    excerpt = models.TextField(max_length=500, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CommunityEvent(models.Model):
    """Eventos de la comunidad científica."""
    title = models.CharField(max_length=300)
    description = models.TextField()
    location = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_url = models.URLField(blank=True)
    organized_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    attendees = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Testimonios de miembros de la comunidad."""
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Testimonial by {self.author.username}"


class JobApplication(models.Model):
    """Postulaciones a ofertas laborales."""
    STATUS_CHOICES = (
        ('submitted', 'Enviada'),
        ('reviewing', 'En revisión'),
        ('shortlisted', 'Preseleccionada'),
        ('rejected', 'Rechazada'),
        ('hired', 'Contratada/o'),
    )

    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='job_applications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_applications')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    cover_letter = models.TextField(max_length=2000)
    cv_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('job_offer', 'applicant')

    def __str__(self):
        return f"{self.full_name} -> {self.job_offer.title}"


class BulletinPost(models.Model):
    """Avisos del tablón comunitario."""
    CATEGORY_CHOICES = (
        ('mascotas', 'Mascotas perdidas'),
        ('viajes', 'Viajes compartidos'),
        ('arriendos', 'Arriendos/Deptos'),
        ('equipos', 'Intercambio equipos'),
        ('otros', 'Otros'),
    )

    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='bulletin_posts')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='otros')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1500)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class TourismRequest(models.Model):
    """Solicitudes de itinerario de turismo científico."""
    STATUS_CHOICES = (
        ('new', 'Nueva'),
        ('contacted', 'Contactada'),
        ('quoted', 'Cotizada'),
        ('closed', 'Cerrada'),
    )

    requester = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='tourism_requests')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    institution = models.CharField(max_length=200, blank=True)
    destination = models.CharField(max_length=200)
    travel_date = models.DateField(null=True, blank=True)
    participants = models.PositiveIntegerField(default=1)
    notes = models.TextField(max_length=1500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Solicitud turismo: {self.full_name}"


class Favorite(models.Model):
    """Ítems guardados por el usuario (empleos, posts, eventos)."""
    ITEM_TYPE_CHOICES = (
        ('job',   'Oferta Laboral'),
        ('post',  'Publicación de Blog'),
        ('event', 'Evento'),
    )
    user      = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id   = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'item_type', 'item_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.item_type}:{self.item_id}"
