from django.shortcuts import render

from articles.models import Article, Category


def home(request):
    context = {
        'articles_count': Article.objects.count(),
        'categories_count': Category.objects.count(),
        'accepted_count': Article.objects.filter(status=Article.Status.ACCEPTED).count(),
    }
    return render(request, 'core/home.html', context)
