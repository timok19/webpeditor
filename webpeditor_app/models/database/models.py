from django.db import models
from django.utils import timezone
from django_extensions.db.fields.json import JSONField

from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image_url = models.ImageField(upload_to="",
                                           validators=[validate_image_file_size],
                                           null=True,
                                           blank=True)
    user_id = models.CharField(max_length=32, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Original Image'
        verbose_name_plural = 'Original Images'

    def __str__(self):
        return str(self.image_id)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image_file = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    edited_image_name = models.CharField(max_length=255, default="")
    content_type_edited = models.CharField(max_length=255)
    steps = JSONField(default=list, null=True, editable=True, blank=True, max_length=50)
    current_step = models.IntegerField(default=1)
    is_currently_editing = models.BooleanField(default=True)
    edited_image_url = models.ImageField(upload_to="",
                                         validators=[validate_image_file_size],
                                         null=True,
                                         blank=True)
    user_id = models.CharField(max_length=32, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Edited Image'
        verbose_name_plural = 'Edited Images'

    def __str__(self):
        return str(self.edited_image_id)

    def add_step(self, step_number: int, description: str, params: dict, created_at: timezone.datetime):
        new_step = {
            "step_number": step_number,
            "description": description,
            "params": params,
            "created_at": created_at,
            "is_currently_editing": False,
        }
        self.steps.insert(step_number - 1, new_step)
        self.update_steps_and_current_step()

    def update_steps_and_current_step(self):
        self.current_step = len(self.steps)
        for index, step in enumerate(self.steps):
            step["step_number"] = index + 1
            step["is_currently_editing"] = index + 1 == self.current_step
        self.save()

    def get_previous_step(self):
        return self.steps[self.current_step - 2] if self.current_step > 1 else None

    def get_next_step(self):
        return self.steps[self.current_step] if self.current_step < len(self.steps) else None

    def get_steps_number(self):
        return len(self.steps)

    def set_currently_editing(self, is_editing: bool):
        self.is_currently_editing = is_editing
        self.save()
