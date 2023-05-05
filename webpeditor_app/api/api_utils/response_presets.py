from django.http import HttpResponseRedirect


def unauthorized_access_response() -> HttpResponseRedirect:
    response = HttpResponseRedirect(redirect_to='/unauthorized_access/')
    response.content = "Unauthorized access"
    response.status_code = 401

    return response
