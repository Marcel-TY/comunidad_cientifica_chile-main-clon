import json
import re
import csv
from urllib.parse import urlencode
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.core.cache import cache
from accounts.models import (
    CustomUser,
    Advertisement,
    JobOffer,
    BlogPost,
    CommunityEvent,
    JobApplication,
    BulletinPost,
    TourismRequest,
    Testimonial,
    Favorite,
)
from accounts.forms import JobApplicationForm, BulletinPostForm, TourismRequestForm, ProfileEditForm


def _portal_context(request):
    """Contexto base reutilizable para páginas del portal."""
    today = timezone.now()
    ads = Advertisement.objects.filter(is_active=True, position='hero_carousel')[:5]
    jobs = JobOffer.objects.filter(status='active').order_by('-created_at')
    events = CommunityEvent.objects.filter(start_date__gte=today).order_by('start_date')
    blog_posts = BlogPost.objects.filter(published=True).order_by('-created_at')
    approved_members = CustomUser.objects.filter(is_approved=True).order_by('-created_at')
    bulletin_posts = BulletinPost.objects.filter(is_active=True).order_by('-created_at')
    testimonials = Testimonial.objects.select_related('author').order_by('-created_at')[:6]

    return {
        'advertisements': ads,
        'featured_jobs': jobs[:6],
        'upcoming_events': events[:6],
        'blog_posts': blog_posts[:6],
        'approved_members': approved_members[:8],
        'bulletin_posts': bulletin_posts[:12],
        'testimonials': testimonials,
        'stats': {
            'members': approved_members.count(),
            'jobs': jobs.count(),
            'events': events.count(),
            'posts': blog_posts.count(),
        },
        'user': request.user,
    }

def index(request):
    """Home ejecutiva con acceso por módulos para reducir scroll."""
    context = _portal_context(request)
    context['featured_jobs'] = context['featured_jobs'][:3]
    context['upcoming_events'] = context['upcoming_events'][:3]
    context['blog_posts'] = context['blog_posts'][:3]
    return render(request, 'index.html', context)


def pwa_manifest(request):
        """Manifest PWA para instalación."""
        manifest = {
                "name": "Comunidad Científica Chile",
                "short_name": "CCC Chile",
                "description": "Portal científico profesional para comunidad, empleos, eventos, blog y publicidad.",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "background_color": "#070b1a",
                "theme_color": "#8f63ff",
                "lang": "es-CL",
                "orientation": "portrait-primary",
                "icons": [
                        {
                                "src": "/static/icons/icon-192.svg",
                                "sizes": "192x192",
                                "type": "image/svg+xml",
                                "purpose": "any maskable"
                        },
                        {
                                "src": "/static/icons/icon-512.svg",
                                "sizes": "512x512",
                                "type": "image/svg+xml",
                                "purpose": "any maskable"
                        }
                ],
                "shortcuts": [
                        {"name": "Empleos", "url": "/empleos/"},
                        {"name": "Mi panel", "url": "/mi-panel/"},
                        {"name": "Asistente IA", "url": "/ia/"}
                ]
        }
        return JsonResponse(manifest)


def service_worker(request):
        """Service worker básico para cache de shell y navegación."""
        js = """
const CACHE_NAME = 'ccc-shell-v1';
const OFFLINE_URLS = [
    '/',
    '/comunidad/',
    '/empleos/',
    '/biblioteca/',
    '/eventos/',
    '/turismo/',
    '/blog/',
    '/publicidad/',
    '/ia/',
    '/static/css/style.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        ))
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then(cached => {
            if (cached) return cached;
            return fetch(event.request)
                .then(response => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    return response;
                })
                .catch(() => caches.match('/'));
        })
    );
});
"""
        return HttpResponse(js, content_type='application/javascript')


def comunidad_page(request):
    """Módulo de comunidad con búsqueda y paginación (#8)."""
    context = _portal_context(request)
    search = request.GET.get('q', '').strip()
    members = CustomUser.objects.filter(is_approved=True).order_by('-created_at')
    if search:
        members = members.filter(
            Q(username__icontains=search) | Q(first_name__icontains=search)
            | Q(last_name__icontains=search) | Q(institution__icontains=search)
        )
    members_page = Paginator(members, 12).get_page(request.GET.get('page'))
    context['approved_members'] = members_page
    context['search_query'] = search
    context.update({
        'section_eyebrow': 'Módulo Comunidad',
        'section_title': 'Directorio científico activo',
        'section_description': 'Perfiles aprobados y colaboración verificable para investigación y alianzas.',
    })
    return render(request, 'sections/comunidad.html', context)


def empleos_page(request):
    """Módulo de empleos con búsqueda, filtro por tipo y paginación (#6 & #8)."""
    context = _portal_context(request)
    search   = request.GET.get('q', '').strip()
    job_type = request.GET.get('tipo', '').strip()
    jobs = JobOffer.objects.filter(status='active').order_by('-created_at')
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) | Q(institution__icontains=search)
            | Q(description__icontains=search)
        )
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    jobs_page = Paginator(jobs, 9).get_page(request.GET.get('page'))
    context['featured_jobs'] = jobs_page
    context['jobs_page']     = jobs_page
    context['search_query']  = search
    context['selected_tipo'] = job_type
    context['job_type_choices'] = JobOffer._meta.get_field('job_type').choices
    context.update({
        'section_eyebrow': 'Módulo Empleos',
        'section_title': 'Ofertas laborales científicas',
        'section_description': 'Vacantes para academia, industria y centros de investigación en un solo flujo.',
    })
    return render(request, 'sections/empleos.html', context)


def biblioteca_page(request):
    """Módulo de biblioteca y tablón."""
    context = _portal_context(request)
    context['bulletin_posts'] = BulletinPost.objects.filter(is_active=True).order_by('-created_at')[:20]
    context.update({
        'section_eyebrow': 'Módulo Biblioteca',
        'section_title': 'Tablón comunitario inteligente',
        'section_description': 'Avisos de utilidad para la comunidad científica organizados por contexto.',
    })
    return render(request, 'sections/biblioteca.html', context)


def eventos_page(request):
    """Módulo de eventos."""
    context = _portal_context(request)
    context['upcoming_events'] = CommunityEvent.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:20]
    context.update({
        'section_eyebrow': 'Módulo Eventos',
        'section_title': 'Agenda estratégica de ciencia',
        'section_description': 'Congresos, charlas y networking para potenciar impacto científico.',
    })
    return render(request, 'sections/eventos.html', context)


def turismo_page(request):
    """Módulo de turismo científico."""
    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Módulo Turismo',
        'section_title': 'Turismo científico y corporativo',
        'section_description': 'Experiencias premium para fortalecer vínculos entre ciencia, cultura y territorio.',
    })
    return render(request, 'sections/turismo.html', context)


@login_required(login_url='login')
def empleo_postular(request, job_id):
    """Formulario real de postulación a empleo."""
    job = get_object_or_404(JobOffer, id=job_id, status='active')
    existing_application = JobApplication.objects.filter(job_offer=job, applicant=request.user).first()

    if existing_application:
        messages.info(request, 'Ya enviaste una postulación para esta oferta.')
        return redirect('empleos')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job_offer = job
            application.applicant = request.user
            application.save()
            JobOffer.objects.filter(id=job.id).update(applications=F('applications') + 1)
            messages.success(request, 'Postulación enviada correctamente.')
            return redirect('empleos')
    else:
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = JobApplicationForm(initial=initial_data)

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Postulación laboral',
        'section_title': f'Postular a: {job.title}',
        'section_description': 'Completa tu candidatura en un flujo formal y trazable.',
        'job': job,
        'form': form,
    })
    return render(request, 'sections/empleo_postular.html', context)


@login_required(login_url='login')
def biblioteca_publicar(request):
    """Formulario real para crear avisos del tablón."""
    if request.method == 'POST':
        form = BulletinPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Aviso publicado exitosamente.')
            return redirect('biblioteca')
    else:
        form = BulletinPostForm(initial={'contact_email': request.user.email})

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Publicar aviso',
        'section_title': 'Nuevo aviso de comunidad',
        'section_description': 'Crea publicaciones claras para mantener un tablón útil y profesional.',
        'form': form,
    })
    return render(request, 'sections/biblioteca_publicar.html', context)


def blog_detail(request, slug):
    """Detalle de publicación de blog."""
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    BlogPost.objects.filter(id=post.id).update(views=F('views') + 1)
    post.refresh_from_db(fields=['views'])

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Detalle de publicación',
        'section_title': post.title,
        'section_description': 'Lectura completa de contenido científico y de innovación.',
        'post': post,
    })
    return render(request, 'sections/blog_detail.html', context)


def turismo_solicitar(request):
    """Formulario real de solicitud de itinerario turístico científico."""
    if request.method == 'POST':
        form = TourismRequestForm(request.POST)
        if form.is_valid():
            tourism_request = form.save(commit=False)
            tourism_request.requester = request.user if request.user.is_authenticated else None
            tourism_request.save()
            messages.success(request, 'Solicitud enviada. Te contactaremos con propuesta personalizada.')
            return redirect('turismo')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'institution': request.user.institution,
            }
        form = TourismRequestForm(initial=initial_data)

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Solicitud de itinerario',
        'section_title': 'Planificar experiencia de turismo científico',
        'section_description': 'Comparte tus preferencias y te enviaremos una propuesta de alto nivel.',
        'form': form,
    })
    return render(request, 'sections/turismo_solicitar.html', context)


def _safe_filter_value(value, allowed_values):
    """Normaliza filtros para evitar valores no permitidos."""
    return value if value in allowed_values else 'all'


def _csv_download_response(filename, headers, rows):
    """Construye respuesta de descarga CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    return response


def _build_query_string(request, remove_keys):
    """Construye querystring preservando filtros actuales."""
    params = request.GET.copy()
    for key in remove_keys:
        if key in params:
            del params[key]
    return urlencode(params, doseq=True)


@login_required(login_url='login')
def mi_panel(request):
    """Panel ejecutivo del usuario autenticado."""
    user = request.user
    app_allowed = {choice[0] for choice in JobApplication.STATUS_CHOICES}
    post_allowed = {choice[0] for choice in BulletinPost.CATEGORY_CHOICES}
    tourism_allowed = {choice[0] for choice in TourismRequest.STATUS_CHOICES}

    selected_app_status = _safe_filter_value(request.GET.get('app_status', 'all'), app_allowed)
    selected_post_category = _safe_filter_value(request.GET.get('post_category', 'all'), post_allowed)
    selected_tourism_status = _safe_filter_value(request.GET.get('tourism_status', 'all'), tourism_allowed)
    app_search = request.GET.get('app_q', '').strip()
    post_search = request.GET.get('post_q', '').strip()
    tourism_search = request.GET.get('tourism_q', '').strip()

    applications_queryset = JobApplication.objects.filter(applicant=user).select_related('job_offer').order_by('-created_at')
    if selected_app_status != 'all':
        applications_queryset = applications_queryset.filter(status=selected_app_status)
    if app_search:
        applications_queryset = applications_queryset.filter(
            Q(job_offer__title__icontains=app_search)
            | Q(job_offer__institution__icontains=app_search)
            | Q(full_name__icontains=app_search)
        )

    posts_queryset = BulletinPost.objects.filter(author=user).order_by('-created_at')
    if selected_post_category != 'all':
        posts_queryset = posts_queryset.filter(category=selected_post_category)
    if post_search:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=post_search)
            | Q(description__icontains=post_search)
            | Q(contact_email__icontains=post_search)
        )

    tourism_queryset = TourismRequest.objects.filter(requester=user).order_by('-created_at')
    if selected_tourism_status != 'all':
        tourism_queryset = tourism_queryset.filter(status=selected_tourism_status)
    if tourism_search:
        tourism_queryset = tourism_queryset.filter(
            Q(destination__icontains=tourism_search)
            | Q(institution__icontains=tourism_search)
            | Q(notes__icontains=tourism_search)
        )

    applications_page = Paginator(applications_queryset, 8).get_page(request.GET.get('app_page'))
    posts_page = Paginator(posts_queryset, 8).get_page(request.GET.get('post_page'))
    tourism_page = Paginator(tourism_queryset, 8).get_page(request.GET.get('tourism_page'))

    app_query_base = _build_query_string(request, ['app_page'])
    post_query_base = _build_query_string(request, ['post_page'])
    tourism_query_base = _build_query_string(request, ['tourism_page'])

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Mi panel',
        'section_title': 'Panel ejecutivo personal',
        'section_description': 'Gestiona tu actividad en empleos, tablón y turismo desde una sola vista.',
        'applications_page': applications_page,
        'posts_page': posts_page,
        'tourism_page': tourism_page,
        'selected_app_status': selected_app_status,
        'selected_post_category': selected_post_category,
        'selected_tourism_status': selected_tourism_status,
        'app_search': app_search,
        'post_search': post_search,
        'tourism_search': tourism_search,
        'app_query_base': app_query_base,
        'post_query_base': post_query_base,
        'tourism_query_base': tourism_query_base,
        'app_status_choices': JobApplication.STATUS_CHOICES,
        'post_category_choices': BulletinPost.CATEGORY_CHOICES,
        'tourism_status_choices': TourismRequest.STATUS_CHOICES,
        'user_metrics': {
            'applications_count': JobApplication.objects.filter(applicant=user).count(),
            'posts_count': BulletinPost.objects.filter(author=user).count(),
            'tourism_count': TourismRequest.objects.filter(requester=user).count(),
        },
    })
    # Rec #9 — Favoritos del usuario
    fav_job_ids = list(Favorite.objects.filter(user=user, item_type='job').values_list('item_id', flat=True))
    context['favorite_jobs']    = JobOffer.objects.filter(id__in=fav_job_ids, status='active')
    context['favorite_job_ids'] = fav_job_ids
    return render(request, 'sections/mi_panel.html', context)


@login_required(login_url='login')
def mi_panel_export_applications(request):
    """Exporta postulaciones del usuario en CSV."""
    user = request.user
    allowed = {choice[0] for choice in JobApplication.STATUS_CHOICES}
    status_filter = _safe_filter_value(request.GET.get('status', 'all'), allowed)
    search = request.GET.get('q', '').strip()

    queryset = JobApplication.objects.filter(applicant=user).select_related('job_offer').order_by('-created_at')
    if status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(
            Q(job_offer__title__icontains=search)
            | Q(job_offer__institution__icontains=search)
            | Q(full_name__icontains=search)
        )

    rows = [
        [
            item.job_offer.title,
            item.job_offer.institution,
            item.get_status_display(),
            item.created_at.strftime('%d/%m/%Y %H:%M'),
        ]
        for item in queryset
    ]

    filename = f"mi_panel_postulaciones_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = ['Oferta', 'Institución', 'Estado', 'Fecha']
    return _csv_download_response(filename, headers, rows)


@login_required(login_url='login')
def mi_panel_export_posts(request):
    """Exporta avisos del usuario en CSV."""
    user = request.user
    allowed = {choice[0] for choice in BulletinPost.CATEGORY_CHOICES}
    category_filter = _safe_filter_value(request.GET.get('category', 'all'), allowed)
    search = request.GET.get('q', '').strip()

    queryset = BulletinPost.objects.filter(author=user).order_by('-created_at')
    if category_filter != 'all':
        queryset = queryset.filter(category=category_filter)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(contact_email__icontains=search)
        )

    rows = [
        [
            item.title,
            item.get_category_display(),
            'Activo' if item.is_active else 'Inactivo',
            item.created_at.strftime('%d/%m/%Y %H:%M'),
        ]
        for item in queryset
    ]

    filename = f"mi_panel_avisos_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = ['Título', 'Categoría', 'Estado', 'Fecha']
    return _csv_download_response(filename, headers, rows)


@login_required(login_url='login')
def mi_panel_export_tourism(request):
    """Exporta solicitudes de turismo del usuario en CSV."""
    user = request.user
    allowed = {choice[0] for choice in TourismRequest.STATUS_CHOICES}
    status_filter = _safe_filter_value(request.GET.get('status', 'all'), allowed)
    search = request.GET.get('q', '').strip()

    queryset = TourismRequest.objects.filter(requester=user).order_by('-created_at')
    if status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(
            Q(destination__icontains=search)
            | Q(institution__icontains=search)
            | Q(notes__icontains=search)
        )

    rows = [
        [
            item.destination,
            item.participants,
            item.get_status_display(),
            item.created_at.strftime('%d/%m/%Y %H:%M'),
        ]
        for item in queryset
    ]

    filename = f"mi_panel_turismo_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = ['Destino', 'Participantes', 'Estado', 'Fecha']
    return _csv_download_response(filename, headers, rows)


def blog_page(request):
    """Módulo de blog con búsqueda y paginación (#6 & #8)."""
    context = _portal_context(request)
    search = request.GET.get('q', '').strip()
    posts = BlogPost.objects.filter(published=True).order_by('-created_at')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | Q(excerpt__icontains=search)
            | Q(tags__icontains=search)
        )
    posts_page = Paginator(posts, 9).get_page(request.GET.get('page'))
    context['blog_posts']   = posts_page
    context['search_query'] = search
    context.update({
        'section_eyebrow': 'Módulo Blog',
        'section_title': 'Publicaciones y divulgación',
        'section_description': 'Contenido científico curado para difusión, reputación y transferencia de conocimiento.',
    })
    return render(request, 'sections/blog.html', context)


def publicidad_page(request):
    """Módulo de publicidades y carrusel."""
    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Módulo Publicidad',
        'section_title': 'Carrusel comercial de alto valor',
        'section_description': 'Gestión profesional de anuncios con enfoque en rendimiento y visibilidad.',
    })
    return render(request, 'sections/publicidad.html', context)


def ia_page(request):
    """Módulo dedicado al asistente IA."""
    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Módulo IA',
        'section_title': 'Asistente científico inteligente',
        'section_description': 'Soporte inmediato para fondos, carrera científica y decisiones estratégicas.',
    })
    return render(request, 'sections/ia.html', context)


def _build_ai_answer(user_message: str) -> dict:
    """Respuesta IA local (fallback inteligente por contexto científico)."""
    text = user_message.lower().strip()

    knowledge_base = {
        "fondos": {
            "keywords": ["fondo", "fondos", "financiamiento", "grant", "beca", "fondecyt"],
            "answer": (
                "Para financiamiento científico en Chile te recomiendo priorizar: "
                "Fondecyt Regular, Iniciación ANID, y convocatorias CORFO I+D. "
                "Si quieres, te preparo una hoja de ruta por etapa (pregrado, magíster, doctorado o postdoc)."
            ),
            "actions": ["Ver convocatorias ANID", "Checklist postulación", "Calendario de fondos"]
        },
        "empleo": {
            "keywords": ["empleo", "trabajo", "vacante", "postdoc", "postdoctorado", "oferta"],
            "answer": (
                "Para empleos científicos competitivos, optimiza tu CV en 1 página técnica, "
                "destaca publicaciones Q1/Q2 y proyectos reproducibles con GitHub. "
                "Puedo sugerirte un formato ideal para industria o academia."
            ),
            "actions": ["Plantilla CV científico", "Ofertas destacadas", "Simular entrevista"]
        },
        "ia": {
            "keywords": ["ia", "inteligencia artificial", "machine learning", "modelo", "llm"],
            "answer": (
                "Si quieres aplicar IA en investigación, empieza con un pipeline: "
                "limpieza de datos, baseline interpretable, validación cruzada y reporte de sesgos. "
                "Te puedo proponer stack por área: bio, astro o ciencias sociales."
            ),
            "actions": ["Stack recomendado", "Buenas prácticas", "Ejemplo de pipeline"]
        },
        "eventos": {
            "keywords": ["evento", "congreso", "seminario", "networking", "charla"],
            "answer": (
                "Para networking de alto impacto, enfócate en congresos con sesiones de póster + rondas B2B. "
                "Te conviene llegar con un one-pager técnico y propuesta de colaboración en 3 líneas."
            ),
            "actions": ["Eventos próximos", "Guion networking", "One-pager template"]
        },
    }

    best_topic = None
    best_score = 0
    for topic, data in knowledge_base.items():
        score = sum(1 for kw in data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", text))
        if score > best_score:
            best_score = score
            best_topic = topic

    if not text:
        return {
            "reply": "Cuéntame tu objetivo científico (empleo, fondos, IA o eventos) y te doy una guía precisa.",
            "actions": ["Buscar fondos", "Ver empleos", "Plan IA"]
        }

    if best_topic:
        return {
            "reply": knowledge_base[best_topic]["answer"],
            "actions": knowledge_base[best_topic]["actions"]
        }

    return {
        "reply": (
            "Entendido. Te puedo ayudar con estrategia científica, empleabilidad, grants o IA aplicada. "
            "Si me dices tu área y objetivo en 1 línea, te doy un plan accionable inmediato."
        ),
        "actions": ["Definir objetivo", "Plan 30 días", "Recursos recomendados"]
    }


@require_POST
def ai_chat(request):
    """Endpoint de chat IA con rate limiting — 20 req/hora por IP (#13)."""
    client_ip = request.META.get(
        'HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')
    ).split(',')[0].strip()
    cache_key     = f'ai_rate_{client_ip}'
    request_count = cache.get(cache_key, 0)
    if request_count >= 20:
        return JsonResponse(
            {"ok": False, "error": "Límite de 20 consultas/hora alcanzado. Inténtalo más tarde."},
            status=429,
        )
    cache.set(cache_key, request_count + 1, timeout=3600)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Payload inválido"}, status=400)

    message = str(payload.get("message", "")).strip()
    if len(message) > 1000:
        return JsonResponse({"ok": False, "error": "Mensaje demasiado largo"}, status=400)

    response = _build_ai_answer(message)
    return JsonResponse({"ok": True, **response})


def login_view(request):
    """Página de login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if is_admin(user):
                return redirect('admin_dashboard')
            return redirect('index')
        else:
            return render(request, 'auth/login.html', {'error': 'Usuario o contraseña inválidos'})
    return render(request, 'auth/login.html')


def register_view(request):
    """Página de registro."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'investigador')
        
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': 'Usuario ya existe'})
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            is_approved=False
        )
        login(request, user)
        return redirect('index')
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """Logout."""
    logout(request)
    return redirect('index')


def is_admin(user):
    """Verifica si el usuario es admin."""
    return user.is_superuser or user.user_type == 'admin'


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Panel de administración."""
    pending_users = CustomUser.objects.filter(is_approved=False, user_type__in=['investigador', 'empresa'])
    pending_jobs = JobOffer.objects.filter(status='pending')
    pending_ads = Advertisement.objects.filter(is_active=False)
    latest_users = CustomUser.objects.order_by('-created_at')[:8]
    latest_jobs = JobOffer.objects.order_by('-created_at')[:8]
    latest_posts = BlogPost.objects.order_by('-created_at')[:8]
    latest_events = CommunityEvent.objects.order_by('-created_at')[:8]
    latest_tourism = TourismRequest.objects.order_by('-created_at')[:8]
    
    context = {
        'pending_users': pending_users,
        'pending_jobs': pending_jobs,
        'pending_ads': pending_ads,
        'latest_users': latest_users,
        'latest_jobs': latest_jobs,
        'latest_posts': latest_posts,
        'latest_events': latest_events,
        'latest_tourism': latest_tourism,
        'total_users': CustomUser.objects.count(),
        'total_jobs': JobOffer.objects.filter(status='active').count(),
        'total_ads': Advertisement.objects.filter(is_active=True).count(),
        'total_posts': BlogPost.objects.filter(published=True).count(),
        'total_events': CommunityEvent.objects.count(),
        'total_tourism': TourismRequest.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_user(request, user_id):
    """Aprobar usuario para publicar ofertas."""
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_job(request, job_id):
    """Aprobar oferta de trabajo."""
    job = get_object_or_404(JobOffer, id=job_id)
    job.status = 'active'
    job.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_ad(request, ad_id):
    """Activar publicidad pendiente."""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.is_active = True
    ad.save(update_fields=['is_active'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


# ───────────────────────────────────────────────────────────────
# NUEVAS VISTAS — 25 Mejoras Profesionales
# ───────────────────────────────────────────────────────────────


def global_search(request):
    """Búsqueda global en empleos, blog, eventos y comunidad (#5)."""
    query = request.GET.get('q', '').strip()
    results = {'jobs': [], 'posts': [], 'events': [], 'members': []}
    total = 0

    if query and len(query) >= 2:
        jobs = JobOffer.objects.filter(status='active').filter(
            Q(title__icontains=query) | Q(institution__icontains=query)
            | Q(description__icontains=query)
        )[:6]
        posts = BlogPost.objects.filter(published=True).filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query)
            | Q(tags__icontains=query)
        )[:6]
        events = CommunityEvent.objects.filter(
            start_date__gte=timezone.now()
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
            | Q(organized_by__icontains=query)
        )[:4]
        members = CustomUser.objects.filter(is_approved=True).filter(
            Q(username__icontains=query) | Q(first_name__icontains=query)
            | Q(last_name__icontains=query) | Q(institution__icontains=query)
        )[:6]
        results = {'jobs': jobs, 'posts': posts, 'events': events, 'members': members}
        total = len(jobs) + len(posts) + len(events) + len(members)

    context = {
        'query': query,
        'results': results,
        'total': total,
        'section_eyebrow': 'Búsqueda',
        'section_title': 'Resultados de búsqueda',
        'section_description': 'Encuentra empleos, publicaciones, eventos y miembros en toda la plataforma.',
    }
    return render(request, 'sections/search.html', context)


def ad_click(request, ad_id):
    """Registra clic en publicidad y redirige al enlace (#17)."""
    ad = get_object_or_404(Advertisement, id=ad_id, is_active=True)
    Advertisement.objects.filter(id=ad_id).update(clicks=F('clicks') + 1)
    return redirect(ad.link_url)


def robots_txt(request):
    """robots.txt para control de rastreadores SEO (#19 & #25)."""
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /admin-dashboard/',
        'Disallow: /api/',
        'Disallow: /mi-panel/',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


@login_required(login_url='login')
def profile_edit(request):
    """Edición del perfil del usuario autenticado (#4)."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=request.user)

    context = _portal_context(request)
    context.update({
        'section_eyebrow': 'Mi cuenta',
        'section_title': 'Editar mi perfil',
        'section_description': 'Mantén tu información actualizada para mayor visibilidad en la comunidad científica.',
        'form': form,
    })
    return render(request, 'sections/profile_edit.html', context)


@login_required(login_url='login')
@require_POST
def toggle_favorite(request):
    """Agrega o quita un ítem de la lista de favoritos (#9)."""
    # Accept both JSON body (from fetch API) and form-encoded data
    if request.content_type and 'application/json' in request.content_type:
        import json as _json
        try:
            payload = _json.loads(request.body)
        except (ValueError, TypeError):
            return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)
        item_type   = payload.get('item_type', '')
        item_id_raw = payload.get('item_id', '')
    else:
        item_type   = request.POST.get('item_type', '').strip()
        item_id_raw = request.POST.get('item_id', '')

    if item_type not in ('job', 'post', 'event'):
        return JsonResponse({'ok': False, 'error': 'Tipo inválido'}, status=400)
    try:
        item_id = int(item_id_raw)
    except (ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'ID inválido'}, status=400)

    fav, created = Favorite.objects.get_or_create(
        user=request.user, item_type=item_type, item_id=item_id
    )
    if not created:
        fav.delete()
        return JsonResponse({'ok': True, 'action': 'removed'})
    return JsonResponse({'ok': True, 'action': 'added'})
