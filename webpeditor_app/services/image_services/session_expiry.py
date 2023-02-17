from django.core.handlers.wsgi import WSGIRequest


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 30 minutes
    request.session.set_expiry(30 * 60)
