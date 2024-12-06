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
