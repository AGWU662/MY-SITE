"""Context processors for Elite Wealth Capital."""
from django.conf import settings


def site_context(request):
    """Inject common site settings into every template context."""
    return {
        'SITE_NAME': 'Elite Wealth Capital',
    }
