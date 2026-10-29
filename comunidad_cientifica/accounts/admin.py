from django.contrib import admin
from .models import (
	CustomUser,
	Advertisement,
	JobOffer,
	BlogPost,
	CommunityEvent,
	Testimonial,
	JobApplication,
	BulletinPost,
	TourismRequest,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'user_type', 'is_approved', 'is_active')
	list_filter = ('user_type', 'is_approved', 'is_active')
	search_fields = ('username', 'email', 'institution')


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
	list_display = ('title', 'position', 'is_active', 'price', 'created_at')
	list_filter = ('position', 'is_active')
	search_fields = ('title', 'description')


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
	list_display = ('title', 'institution', 'job_type', 'status', 'created_at')
	list_filter = ('status', 'job_type')
	search_fields = ('title', 'institution', 'location')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'published', 'created_at')
	list_filter = ('published',)
	search_fields = ('title', 'slug', 'tags')


@admin.register(CommunityEvent)
class CommunityEventAdmin(admin.ModelAdmin):
	list_display = ('title', 'organized_by', 'location', 'start_date')
	list_filter = ('start_date',)
	search_fields = ('title', 'organized_by', 'location')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ('author', 'rating', 'created_at')
	list_filter = ('rating',)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'job_offer', 'status', 'created_at')
	list_filter = ('status',)
	search_fields = ('full_name', 'email', 'job_offer__title')


@admin.register(BulletinPost)
class BulletinPostAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'is_active', 'created_at')
	list_filter = ('category', 'is_active')
	search_fields = ('title', 'description', 'contact_email')


@admin.register(TourismRequest)
class TourismRequestAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'destination', 'participants', 'status', 'created_at')
	list_filter = ('status',)
	search_fields = ('full_name', 'email', 'destination', 'institution')
