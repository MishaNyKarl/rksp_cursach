from django.contrib import admin

from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'reviewer', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'abstract', 'author__username', 'reviewer__username')
    autocomplete_fields = ('author', 'reviewer', 'category')
