from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountNumberBackend(ModelBackend):
    def authenticate(self, request, account_number=None, password=None, **kwargs):
        # Try to find a user with the provided account number
        try:
            user = User.objects.get(profile__account_number=account_number)
            # Check if the provided password is correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Return None if no user with the provided account number is found
            return None

    def get_user(self, user_id):
        # Retrieve a user by their user_id
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # Return None if no user with the given user_id is found
            return None
