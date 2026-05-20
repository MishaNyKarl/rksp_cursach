from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('article', 'reviewer', 'decision', 'created_at')
    list_filter = ('decision', 'created_at')
    search_fields = ('article__title', 'reviewer__username', 'comment')
