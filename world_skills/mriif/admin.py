from django.contrib import admin
from .models import Skill, ContactUs, SPOCRegistration, Proposal, EvaluatorRegistration, Course, CourseApplication

# Register your models here.
admin.site.register(Skill)
admin.site.register(ContactUs)
admin.site.register(SPOCRegistration)
admin.site.register(Proposal)
admin.site.register(EvaluatorRegistration)
admin.site.register(Course)
admin.site.register(CourseApplication)