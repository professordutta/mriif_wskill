from django.db import models
from django.contrib.auth.models import User
from mriif.utils import get_proposal_file_path
from mriif.validators import validate_file_size, validate_file_extension
from django.core.exceptions import ValidationError

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

class SPOCRegistration(models.Model):
    institute_name = models.CharField(max_length=200)
    institute_code = models.CharField(max_length=50)
    spoc_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    endorsement_letter = models.FileField(
        upload_to='endorsement_letters/',
        validators=[validate_file_size, validate_file_extension],
        help_text='Upload signed endorsement letter from institution head (Max 5MB, Allowed formats: PDF, DOC, DOCX)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institute_name} - {self.spoc_name}"

class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    CATEGORY_CHOICES = [
        ('CONSTRUCTION', 'Digital Construction & Design'),
        ('MEDIA', 'Creative Media & Digital Arts'),
        ('AUTOMOTIVE', 'Automotive Engineering & Technologies'),
        ('HEALTHCARE', 'Healthcare & Medical Technologies'),
        ('IT', 'IT Software Solutions for Business'),
        ('MECHATRONICS', 'Mechatronics & Robotics'),
        ('HOSPITALITY', 'Hospitality & Tourism'),
        ('FASHION', 'Fashion Technology & Design'),
        ('ELECTRONICS', 'Electronics & Electrical Engineering'),
        ('SUSTAINABILITY', 'Sustainability & Green Technologies'),
        ('AGRICULTURE', 'Agriculture & Agribusiness'),
        ('EDUCATION', 'Education & Training Technologies'),
        ('LOGISTICS', 'Logistics & Supply Chain Management'),
        ('DESIGN', 'Design & Innovation'),
        ('CYBERSECURITY', 'Cybersecurity & Digital Forensics'),
    ]
    
    proposal_title = models.CharField(max_length=200)
    institute_name = models.CharField(max_length=200)
    institute_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    proposal_file = models.FileField(upload_to=get_proposal_file_path,validators=[validate_file_size, validate_file_extension],
        help_text='Upload signed endorsement letter from institution head (Max 5MB, Allowed formats: PDF, DOC, DOCX)')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    team_name = models.CharField(max_length=100)
    
    # Team Members
    student1_name = models.CharField(max_length=100)
    student1_email = models.EmailField()
    student2_name = models.CharField(max_length=100)
    student2_email = models.EmailField()
    student3_name = models.CharField(max_length=100)
    student3_email = models.EmailField()
    student4_name = models.CharField(max_length=100)
    student4_email = models.EmailField()
    
    faculty_name = models.CharField(max_length=100)
    faculty_email = models.EmailField()
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.proposal_title

    def clean(self):
        # Check if user has already submitted 10 proposals in this category
        if not self.pk:  # Only check on new proposals
            user_proposals_count = Proposal.objects.filter(
                user=self.user,
                category=self.category
            ).count()
            
            if user_proposals_count >= 10:
                raise ValidationError(
                    f'You have already submitted the maximum allowed proposals (10) for the category {self.get_category_display()}'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)