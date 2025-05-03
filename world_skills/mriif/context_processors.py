from django.conf import settings

def recaptcha_context(request):
    """
    Context processor to make reCAPTCHA public key available to all templates.
    """
    return {
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
    }