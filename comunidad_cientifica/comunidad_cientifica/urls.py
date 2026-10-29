"""
URL configuration for comunidad_cientifica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .views import (
    ai_chat,
    index,
    login_view,
    register_view,
    logout_view,
    admin_dashboard,
    approve_user,
    approve_job,
    approve_ad,
    comunidad_page,
    empleos_page,
    biblioteca_page,
    eventos_page,
    turismo_page,
    blog_page,
    publicidad_page,
    ia_page,
    empleo_postular,
    biblioteca_publicar,
    blog_detail,
    turismo_solicitar,
    mi_panel,
    mi_panel_export_applications,
    mi_panel_export_posts,
    mi_panel_export_tourism,
    pwa_manifest,
    service_worker,
    global_search,
    ad_click,
    robots_txt,
    profile_edit,
    toggle_favorite,
)

urlpatterns = [
    path('', index, name='index'),
    path('manifest.webmanifest', pwa_manifest,  name='pwa_manifest'),
    path('service-worker.js',    service_worker, name='service_worker'),
    path('robots.txt',           robots_txt,     name='robots_txt'),      # Rec #19
    path('sitemap.xml', sitemap, {'sitemaps': {}}, name='django.contrib.sitemaps.views.sitemap'),  # Rec #19
    # ── Modules ──
    path('comunidad/',  comunidad_page,  name='comunidad'),
    path('empleos/',    empleos_page,    name='empleos'),
    path('empleos/<int:job_id>/postular/', empleo_postular, name='empleo_postular'),
    path('biblioteca/', biblioteca_page, name='biblioteca'),
    path('investigacion/', include('research.urls')),
    path('biblioteca/publicar/', biblioteca_publicar, name='biblioteca_publicar'),
    path('eventos/',   eventos_page,    name='eventos'),
    path('turismo/',   turismo_page,    name='turismo'),
    path('turismo/solicitar/', turismo_solicitar, name='turismo_solicitar'),
    path('blog/',      blog_page,       name='blog'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    path('publicidad/', publicidad_page, name='publicidad'),
    path('publicidad/<int:ad_id>/click/', ad_click, name='ad_click'),     # Rec #17
    path('ia/',        ia_page,         name='ia_page'),
    # ── Mi Panel ──
    path('mi-panel/', mi_panel, name='mi_panel'),
    path('mi-panel/export/postulaciones/', mi_panel_export_applications, name='mi_panel_export_applications'),
    path('mi-panel/export/avisos/',        mi_panel_export_posts,        name='mi_panel_export_posts'),
    path('mi-panel/export/turismo/',       mi_panel_export_tourism,      name='mi_panel_export_tourism'),
    # ── Perfil ──
    path('perfil/editar/',  profile_edit,     name='profile_edit'),       # Rec #4
    # ── API ──
    path('api/ai-chat/',    ai_chat,          name='ai_chat'),
    path('api/favoritos/',  toggle_favorite,  name='toggle_favorite'),    # Rec #9
    # ── Búsqueda ──
    path('buscar/', global_search, name='global_search'),                 # Rec #5
    # ── Admin ──
    path('admin/', admin.site.urls),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('panel-admin/', admin_dashboard, name='admin_dashboard_alias'),
    path('admin/approve-user/<int:user_id>/', approve_user, name='approve_user'),
    path('admin/approve-job/<int:job_id>/',  approve_job,  name='approve_job'),
    path('admin/approve-ad/<int:ad_id>/',    approve_ad,   name='approve_ad'),
    path('panel-admin/approve-user/<int:user_id>/', approve_user, name='approve_user_alias'),
    path('panel-admin/approve-job/<int:job_id>/',  approve_job,  name='approve_job_alias'),
    path('panel-admin/approve-ad/<int:ad_id>/',    approve_ad,   name='approve_ad_alias'),
    # ── Auth ──
    path('login/',    login_view,    name='login'),
    path('register/', register_view, name='register'),
    path('logout/',   logout_view,   name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
