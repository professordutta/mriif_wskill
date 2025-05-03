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

class EvaluatorRegistration(models.Model):
    # Use the same categories as Proposal model
    EXPERTISE_CHOICES = Proposal.CATEGORY_CHOICES

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    linkedin_url = models.URLField(blank=True)
    organization = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    experience = models.IntegerField()
    expertise = models.JSONField()  # Store multiple selections as JSON array
    cv_file = models.FileField(
        upload_to='evaluator_cvs/',
        validators=[validate_file_size, validate_file_extension],
        help_text='Upload your CV (Max 5MB, Allowed formats: PDF, DOC, DOCX)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.organization}"

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('FDP', 'Faculty Development Program'),
        ('RTP', 'Refresher Training Program'),
        ('ORT', 'Online Refresher Training'),
        ('SBP', 'Semester Blended Program'),
        ('LTP', 'Long term Program'),
    ]
    
    DELIVERY_MODE_CHOICES = [
        ('OFFLINE', 'Offline'),
        ('ONLINE', 'Online'),
        ('BLENDED', 'Blended'),
    ]
    
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='courses')
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_MODE_CHOICES)
    duration_weeks = models.IntegerField()
    training_fee = models.DecimalField(max_digits=10, decimal_places=2)
    residential_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nsdc_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    mrei_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=85.00)
    requires_industry_cert = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('course_type', 'skill')
    
    def __str__(self):
        return f"{self.get_course_type_display()} - {self.skill.job_title}"
    
    def get_total_fee(self):
        if self.residential_fee:
            return self.training_fee + self.residential_fee
        return self.training_fee

class CourseApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAYMENT_PENDING', 'Payment Pending'),
        ('PAYMENT_COMPLETED', 'Payment Completed'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    organization = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    include_residential = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=200, blank=True, null=True)
    cf_order_id = models.CharField(max_length=200, blank=True, null=True)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    payment_status = models.CharField(max_length=50, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course}"

class Enquiry(models.Model):
    HEARD_FROM_CHOICES = [
        ('SEARCH', 'Search Engine'),
        ('SOCIAL', 'Social Media'),
        ('FRIEND', 'Friend or Colleague'),
        ('EVENT', 'Event or Workshop'),
        ('ADVERTISEMENT', 'Advertisement'),
        ('COLLEGE', 'College/University'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    course = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    traffic_source = models.CharField(max_length=100, blank=True, null=True, help_text="Source of the enquiry (e.g., Google, Facebook, Direct)")
    how_did_you_hear = models.CharField(max_length=20, choices=HEARD_FROM_CHOICES, blank=True, null=True, help_text="How did you hear about us?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.course} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name_plural = "Enquiries"
        ordering = ['-created_at']