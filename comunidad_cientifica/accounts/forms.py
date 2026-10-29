from django import forms
from .models import JobApplication, BulletinPost, TourismRequest, CustomUser


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'cover_letter', 'cv_link']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@institucion.cl'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+56 9 ...'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Describe tu experiencia y motivación'}),
            'cv_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'URL de CV o LinkedIn (opcional)'}),
        }


class BulletinPostForm(forms.ModelForm):
    class Meta:
        model = BulletinPost
        fields = ['category', 'title', 'description', 'contact_email', 'contact_phone']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Título del aviso'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Contenido del aviso'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo de contacto'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Teléfono (opcional)'}),
        }


class TourismRequestForm(forms.ModelForm):
    class Meta:
        model = TourismRequest
        fields = ['full_name', 'email', 'institution', 'destination', 'travel_date', 'participants', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo de contacto'}),
            'institution': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Institución (opcional)'}),
            'destination': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Destino de interés'}),
            'travel_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'participants': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Objetivo del viaje y requerimientos'}),
        }


class ProfileEditForm(forms.ModelForm):
    """Formulario de edición de perfil de usuario."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture', 'institution', 'user_type']
        widgets = {
            'first_name':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre'}),
            'last_name':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu apellido'}),
            'email':            forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.cl'}),
            'bio':              forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Cuéntanos sobre tu trabajo e investigación...'}),
            'institution':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Universidad o institución'}),
            'user_type':        forms.Select(attrs={'class': 'form-input'}),
            'profile_picture':  forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }
