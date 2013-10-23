from django.contrib.auth import get_user_model
from djaccount.models import AccountExternal

class AuthBackend(object):
    def authenticate(self, username=None, password=None):
        if password is None:
            service     = username[0]
            service_id  = username[1]

            try:
                ext = AccountExternal.objects.select_related().get(service=service, service_id=service_id)
            except AccountExternal.DoesNotExist:
                return None 

            return ext.account
        else:              
            Account = get_user_model()

            try:
                # The underlying database must be case-insensitive, at least
                # for this column.
                account = Account.objects.get_by_natural_key(username=username)
            except Account.DoesNotExist:
                return None 

            if account.has_usable_password():        
                pwd_valid = account.check_password(password)
                if pwd_valid:
                    return account 

        return None

    def get_user(self, user_id):
        Account = get_user_model()

        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None