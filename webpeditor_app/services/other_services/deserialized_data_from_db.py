from webpeditor_app.models.database.models import OriginalImage


def get_deserialized_data_from_db():
    try:
        data = OriginalImage.objects.all().values('user_id')
    except OriginalImage.DoesNotExist as error:
        raise error

    deserialized_data = [dict(d) for d in data]
    return deserialized_data
