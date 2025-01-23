from django.core.exceptions import ValidationError

def validate_file_extension(value):
    allowed_extensions = ['.pdf', '.doc', '.docx']
    import os
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions are: pdf, doc, docx')

def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("The maximum file size that can be uploaded is 5MB")