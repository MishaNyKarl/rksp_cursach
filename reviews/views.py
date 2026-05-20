from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserProfile
from articles.models import Article

from .forms import ReviewForm


@login_required
def review_create(request, article_pk):
    article = get_object_or_404(Article.objects.select_related('author', 'category', 'reviewer'), pk=article_pk)
    if request.user.profile.role != UserProfile.Role.REVIEWER:
        raise PermissionDenied('Только рецензент может оставлять рецензии.')
    if article.reviewer_id != request.user.id:
        raise PermissionDenied('Можно рецензировать только назначенные статьи.')
    if article.status in {Article.Status.ACCEPTED, Article.Status.REJECTED}:
        messages.error(request, 'Финальное решение по статье уже принято.')
        return redirect('articles:detail', pk=article.pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.article = article
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Рецензия сохранена, статус статьи обновлен.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'article': article})


@login_required
def review_list(request, article_pk):
    article = get_object_or_404(Article.objects.select_related('author', 'reviewer'), pk=article_pk)
    if not (request.user.is_staff or article.author_id == request.user.id or article.reviewer_id == request.user.id):
        raise PermissionDenied('Нет доступа к рецензиям.')
    reviews = article.reviews.select_related('reviewer')
    return render(request, 'reviews/review_list.html', {'article': article, 'reviews': reviews})
