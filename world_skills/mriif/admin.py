from django.contrib import admin
from .models import Skill, ContactUs, SPOCRegistration, Proposal, EvaluatorRegistration
# Register your models here.
admin.site.register(Skill)
admin.site.register(ContactUs)
admin.site.register(SPOCRegistration)
admin.site.register(Proposal)
admin.site.register(EvaluatorRegistration)