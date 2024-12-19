from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Skill, ContactUs
# Create your views here.
def home(request):
    skills_card = Skill.objects.all()
    return render(request, 'mriif/home.html', {'x':skills_card})

def contact(request):
    if request.method == 'POST':
        # Extract form data from POST request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Validate data (basic check for empty fields)
        if not all([first_name, last_name, email, message]):
            messages.error(request, "All required fields must be filled.")
            return redirect('contact')

        # Save the data to the database
        contact = ContactUs(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            message=message
        )
        contact.save()

        # Display success message
        messages.success(request, "Thank you for your message! We will get back to you soon.")

        # Redirect to the same page or a success page
        return redirect('contact')

    return render(request, 'mriif/contact.html')


def about(request):
    return render(request, 'mriif/about.html')

def skill_detail(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    return render(request, 'mriif/skill_detail.html', {'skill': skill})
