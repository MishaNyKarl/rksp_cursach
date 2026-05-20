from django.contrib.auth.models import User
from django.db import models

from articles.models import Article


class Review(models.Model):
    class Decision(models.TextChoices):
        ACCEPTED = 'accepted', 'Принять'
        REVISION_REQUIRED = 'revision_required', 'На доработку'
        REJECTED = 'rejected', 'Отклонить'

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    decision = models.CharField(max_length=30, choices=Decision.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рецензия'
        verbose_name_plural = 'Рецензии'

    def __str__(self):
        return f'{self.article}: {self.get_decision_display()}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.article.status != self.decision:
            self.article.status = self.decision
            self.article.save(update_fields=['status', 'updated_at'])
