from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserProfile

from .forms import ArticleForm
from .models import Article


def _is_reviewer(user):
    return user.is_authenticated and user.profile.role == UserProfile.Role.REVIEWER


def _can_view_article(user, article):
    return (
        user.is_staff
        or article.author_id == user.id
        or article.reviewer_id == user.id
    )


@login_required
def article_list(request):
    articles = Article.objects.filter(author=request.user).select_related('category', 'reviewer')
    return render(request, 'articles/article_list.html', {'articles': articles})


@login_required
def article_create(request):
    if request.user.profile.role != UserProfile.Role.AUTHOR:
        raise PermissionDenied('Только автор может создавать статьи.')
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Статья создана.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/article_form.html', {'form': form, 'title': 'Создание статьи'})


@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author_id != request.user.id:
        raise PermissionDenied('Нельзя редактировать чужую статью.')
    if not article.can_be_edited:
        messages.error(request, 'Статью нельзя редактировать в текущем статусе.')
        return redirect('articles:detail', pk=article.pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/article_form.html', {'form': form, 'title': 'Редактирование статьи'})


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article.objects.select_related('author', 'category', 'reviewer'), pk=pk)
    if not _can_view_article(request.user, article):
        raise PermissionDenied('Нет доступа к статье.')
    reviews = article.reviews.select_related('reviewer')
    return render(request, 'articles/article_detail.html', {'article': article, 'reviews': reviews})


@login_required
def submit_article(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method != 'POST':
        return redirect('articles:detail', pk=article.pk)
    if not article.can_be_submitted:
        messages.error(request, 'Отправить можно только черновик или статью на доработке.')
        return redirect('articles:detail', pk=article.pk)
    article.submit()
    messages.success(request, 'Статья отправлена на рецензирование.')
    return redirect('articles:detail', pk=article.pk)


@login_required
def reviewer_article_list(request):
    if not _is_reviewer(request.user):
        raise PermissionDenied('Раздел доступен только рецензентам.')
    articles = Article.objects.filter(reviewer=request.user).select_related('author', 'category')
    return render(request, 'articles/reviewer_article_list.html', {'articles': articles})
