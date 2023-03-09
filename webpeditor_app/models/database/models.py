from django.db import models
from django.utils import timezone
from django_extensions.db.fields.json import JSONField

from cropperjs.models import CropperImageField

from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_file = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image_url = CropperImageField(upload_to="",
                                           validators=[validate_image_file_size],
                                           default=None,
                                           null=False,
                                           blank=False)
    user_id = models.CharField(max_length=120, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.image_id)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image_file = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    edited_image_file = models.CharField(max_length=255, default="")
    content_type_edited = models.CharField(max_length=255)
    steps = JSONField(default=list, null=True, editable=True, blank=True, max_length=50, validators=[])
    current_step = models.IntegerField(default=0)
    edited_image_url = CropperImageField(upload_to="edited/",
                                         validators=[validate_image_file_size],
                                         null=False,
                                         blank=False,
                                         default=None)
    user_id = models.CharField(max_length=120, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.edited_image_id)

    def add_step(self, step_number, description, params, created_at):
        self.steps.append({
            "step_number": step_number,
            "description": description,
            "params": params,
            "created_at": created_at
        })
        self.current_step = step_number
        self.save()

    def get_previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.save()
            return self.steps[self.current_step]
        else:
            return None

    def get_next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.save()
            return self.steps[self.current_step]
        else:
            return None
