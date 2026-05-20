from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from articles.models import Article
from reviews.models import Review

from .forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация выполнена. Роль по умолчанию: автор.')
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    profile = request.user.profile
    context = {
        'profile': profile,
        'my_articles_count': Article.objects.filter(author=request.user).count(),
        'assigned_articles_count': Article.objects.filter(reviewer=request.user).count(),
        'reviews_count': Review.objects.filter(reviewer=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)
