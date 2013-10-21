from djbase.exceptions import BaseError

class AccountError(BaseError):
    pass 

class AccountLoginError(AccountError):
    """ Raised when the login email or password is invalid. """
    pass 

class AccountMissingError(AccountError):
    """ Raised when the login email does not exist. """
    pass 

class AccountNoPasswordError(AccountError):
    """ Raised when the account has no password set which happens
        when the user logins using an external account.
    """
    pass 

class AccountEmailTakenError(AccountError):
    """ Raised when the chosen email is already taken. """
    pass 

class AccountExternalTakenError(AccountError):
    """ Raised when the chosen external account is already taken. """
    pass 

class AccountExternalSameEmailError(AccountError):
    """ Raised when the chosen external account's email is already taken. """
    pass 

class AccountExternalNoEmailError(AccountError):
    """ Raised when the chosen external account does not have an email. """
    pass 

class AccountNoCookieError(AccountError):
    pass