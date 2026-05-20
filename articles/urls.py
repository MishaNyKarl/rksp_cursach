from django.urls import path

from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('create/', views.article_create, name='create'),
    path('reviewer/', views.reviewer_article_list, name='reviewer_list'),
    path('<int:pk>/', views.article_detail, name='detail'),
    path('<int:pk>/edit/', views.article_update, name='edit'),
    path('<int:pk>/submit/', views.submit_article, name='submit'),
]
