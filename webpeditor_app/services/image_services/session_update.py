from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.user_folder import delete_empty_folders


def update_session(request: WSGIRequest, user_id: str) -> JsonResponse:
    """
    Update session_id token expiry to 30 minutes if it is not expired yet.
    If session_id token is expired, delete the image and the folder with the image.

    Parameters:
        request (WSGIRequest): request from view
        user_id (str): user id
    Return:
        JsonResponse with information about the user_folder_name token
    """
    # try:
    #     session = Session.objects.get(session_key=session_id)
    # except Session.DoesNotExist:
    #     delete_empty_folders(settings.MEDIA_ROOT)
    #     return JsonResponse({'success': False, 'error': 'Invalid session_id'}, status=400)

    # delete_old_image_in_db_and_local(user_id)
    print(request.get_signed_cookie(
        key='sessionid'
    ))

    # session.expire_date = timezone.now() + timezone.timedelta(seconds=1800)
    # session.save()
    #
    # total_time_expiration: int = round((session.expire_date - timezone.now()).seconds / 60)
    #
    # print(f"\nSession will expire in {total_time_expiration} minute(s)\n")
    return JsonResponse(
        {'success': True, 'info': 'Session is alive', 'estimated_time_of_session_id': str(session.expire_date)},
        status=200)
