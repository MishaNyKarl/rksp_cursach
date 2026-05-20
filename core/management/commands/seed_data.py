from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import UserProfile
from articles.models import Article, Category
from reviews.models import Review


class Command(BaseCommand):
    help = 'Creates demo users, categories, articles and reviews.'

    def handle(self, *args, **options):
        admin = self._user('admin', 'admin12345', 'Администратор', UserProfile.Role.ADMIN, is_staff=True, is_superuser=True)
        author = self._user('author', 'author12345', 'Иван Авторов', UserProfile.Role.AUTHOR)
        reviewer = self._user('reviewer', 'reviewer12345', 'Мария Рецензентова', UserProfile.Role.REVIEWER)

        categories = [
            self._category('Информационные системы', 'Проектирование и разработка информационных систем.'),
            self._category('Искусственный интеллект', 'Модели, алгоритмы и практические применения ИИ.'),
            self._category('Веб-разработка', 'Клиент-серверные приложения и веб-технологии.'),
        ]

        articles_data = [
            ('Архитектура сервиса рецензирования', Article.Status.DRAFT, None, categories[0]),
            ('Применение Django в учебных проектах', Article.Status.SUBMITTED, None, categories[2]),
            ('Методы анализа текстовых данных', Article.Status.UNDER_REVIEW, reviewer, categories[1]),
            ('Проектирование базы данных статей', Article.Status.REVISION_REQUIRED, reviewer, categories[0]),
            ('Bootstrap-интерфейсы для MVP', Article.Status.ACCEPTED, reviewer, categories[2]),
        ]

        created_articles = []
        for title, status, assigned_reviewer, category in articles_data:
            article, _ = Article.objects.get_or_create(
                title=title,
                defaults={
                    'abstract': f'Краткая аннотация статьи "{title}".',
                    'content': 'Основной текст статьи содержит постановку задачи, описание решения и выводы.',
                    'author': author,
                    'category': category,
                    'status': status,
                    'reviewer': assigned_reviewer,
                    'submitted_at': timezone.now() if status != Article.Status.DRAFT else None,
                },
            )
            created_articles.append(article)

        self._review(created_articles[3], reviewer, 'Нужно подробнее описать ограничения выбранной модели данных.', Review.Decision.REVISION_REQUIRED)
        self._review(created_articles[4], reviewer, 'Статья соответствует требованиям и может быть принята.', Review.Decision.ACCEPTED)

        self.stdout.write(self.style.SUCCESS('Demo data created. Accounts: admin/admin12345, author/author12345, reviewer/reviewer12345'))

    def _user(self, username, password, full_name, role, is_staff=False, is_superuser=False):
        user, created = User.objects.get_or_create(username=username)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.email = f'{username}@example.com'
        if created or not user.has_usable_password():
            user.set_password(password)
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.full_name = full_name
        profile.role = role
        profile.save()
        return user

    def _category(self, name, description):
        category, _ = Category.objects.get_or_create(name=name, defaults={'description': description})
        return category

    def _review(self, article, reviewer, comment, decision):
        Review.objects.get_or_create(
            article=article,
            reviewer=reviewer,
            decision=decision,
            defaults={'comment': comment},
        )
