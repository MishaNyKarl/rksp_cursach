from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('article/<int:article_pk>/', views.review_list, name='list'),
    path('article/<int:article_pk>/create/', views.review_create, name='create'),
]
