"""Custom authentication backend for email-based login."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that authenticates users by email address.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Also support 'username' parameter for compatibility
        if email is None:
            email = kwargs.get('username')
        
        if email is None or password is None:
            return None
        
        try:
            user = UserModel.objects.get(email=email.lower().strip())
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            UserModel().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            # Set the backend path on user for login() function
            user.backend = 'accounts.backends.EmailBackend'
            return user
        
        return None
    
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
