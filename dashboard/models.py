import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class NewsArticle(models.Model):
    """News articles for the site's news section."""

    CATEGORY_CHOICES = [
        ('market_update', 'Market Update'),
        ('platform_news', 'Platform News'),
        ('crypto', 'Crypto'),
        ('education', 'Education'),
        ('announcement', 'Announcement'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary shown in article list')
    content = models.TextField(help_text='Full article content (HTML allowed)')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='platform_news')
    image_url = models.URLField(blank=True, help_text='URL of the article cover image')
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text='Show as featured/large card')
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while NewsArticle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news_article', args=[self.slug])


class NewsletterSubscription(models.Model):
    """Newsletter email subscriptions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Messages submitted through the contact form."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} – {self.subject}'


class Dispute(models.Model):
    """Dispute / appeal submissions from users."""

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    APPEAL_TYPE_CHOICES = [
        ('deposit', 'Deposit Issue'),
        ('withdrawal', 'Withdrawal Issue'),
        ('investment', 'Investment Issue'),
        ('account', 'Account Issue'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Allow both authenticated and guest submissions
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disputes',
    )
    # Guest contact info (used when user is not authenticated)
    guest_name = models.CharField(max_length=150, blank=True)
    guest_email = models.EmailField(blank=True)

    appeal_type = models.CharField(max_length=20, choices=APPEAL_TYPE_CHOICES, default='other')
    category = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=250)
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True, default='USD')
    transaction_id = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dispute / Appeal'
        verbose_name_plural = 'Disputes / Appeals'
        ordering = ['-created_at']

    def __str__(self):
        user_label = self.user.email if self.user else self.guest_email or 'Guest'
        return f'#{str(self.id)[:8].upper()} – {self.subject} ({user_label})'

    @property
    def reference(self):
        return f'APL-{str(self.id)[:8].upper()}'
