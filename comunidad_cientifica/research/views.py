from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def catalog(request):
    return render(request, 'sections/research_catalog.html')
