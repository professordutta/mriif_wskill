from django.db import models

class Skill(models.Model):
    job_img = models.ImageField(upload_to='images/')
    job_id = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_category = models.CharField(max_length=255, blank=True)
    job_description = models.TextField()
    skills_involved = models.TextField()
    career_opportunities = models.TextField()
    role_summary = models.TextField()

    def __str__(self):
        return self.job_title
class ContactUs(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email