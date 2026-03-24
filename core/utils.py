"""
Shared utility functions.
"""


def get_client_ip(request):
    """
    Extract client IP address from request, checking proxy headers.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip
