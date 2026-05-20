from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        SUBMITTED = 'submitted', 'Отправлена'
        UNDER_REVIEW = 'under_review', 'На рецензировании'
        REVISION_REQUIRED = 'revision_required', 'Требует доработки'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'

    title = models.CharField(max_length=255)
    abstract = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_articles',
    )
    file = models.FileField(upload_to='articles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

    @property
    def can_be_edited(self):
        return self.status in {self.Status.DRAFT, self.Status.REVISION_REQUIRED}

    @property
    def can_be_submitted(self):
        return self.status in {self.Status.DRAFT, self.Status.REVISION_REQUIRED}

    def submit(self):
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=['status', 'submitted_at', 'updated_at'])
