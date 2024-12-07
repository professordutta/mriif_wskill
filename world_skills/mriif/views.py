from django.shortcuts import render, get_object_or_404
from .models import Skill
# Create your views here.
def home(request):
    skills_card = Skill.objects.all()
    return render(request, 'mriif/home.html', {'x':skills_card})

def contact(request):
    return render(request, 'mriif/contact.html')

def about(request):
    return render(request, 'mriif/about.html')

def skill_detail(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    return render(request, 'mriif/skill_detail.html', {'skill': skill})
