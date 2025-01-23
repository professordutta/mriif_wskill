from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import os
from django.contrib import messages
from .models import Skill, ContactUs, SPOCRegistration, Proposal
from django.core.exceptions import ValidationError
from .validators import validate_file_size, validate_file_extension
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate

# Create your views here.
def home(request):
    skills_card = Skill.objects.all()
    return render(request, 'mriif/home.html', {'x':skills_card})

def login_view(request):
    # Redirect logged-in users to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'mriif/login.html')

    return render(request, 'mriif/login.html')


@login_required
def logoutuser(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

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

def spoc_registration(request):
    if request.method == 'POST':
        try:
            endorsement_letter = request.FILES.get('endorsement_letter')
            if endorsement_letter:
                validate_file_size(endorsement_letter)
                validate_file_extension(endorsement_letter)
                
            spoc = SPOCRegistration(
                institute_name=request.POST.get('institute_name'),
                institute_code=request.POST.get('institute_code'),
                spoc_name=request.POST.get('spoc_name'),
                designation=request.POST.get('designation'),
                email=request.POST.get('email'),
                mobile=request.POST.get('mobile'),
                address=request.POST.get('address'),
                state=request.POST.get('state'),
                city=request.POST.get('city'),
                pincode=request.POST.get('pincode'),
                endorsement_letter=endorsement_letter
            )
            spoc.save()
            messages.success(request, "Registration submitted successfully! You will receive credentials via email.")
            return redirect('spoc_registration')
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('spoc_registration')
        except Exception:  
            messages.error(request, "Error in registration. Please ensure all fields are filled correctly including the endorsement letter.")
            return redirect('spoc_registration')

    return render(request, 'mriif/spoc-registration.html')

def download_endorsement_template(request):
    file_path = 'static/endorsement_template.docx' 
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename=spoc_endorsement_template.docx'
            return response
    return HttpResponse("Template file not found", status=404)

def hackathon(request):
    return render(request, 'mriif/hackathon.html')

@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name='spocs').exists() or u.is_superuser)
def submit_proposal(request):
    if request.method == 'POST':
        try:
            # Check proposal count before processing file
            category = request.POST.get('category')
            user_proposals_count = Proposal.objects.filter(
                user=request.user,
                category=category
            ).count()
            
            if user_proposals_count >= 10:
                messages.error(
                    request, 
                    'You have already submitted the maximum allowed proposals (10) for this category'
                )
                return redirect('submit_proposal')

            proposal_file = request.FILES.get('proposal_file')
            if proposal_file:
                validate_file_size(proposal_file)
                validate_file_extension(proposal_file)
            
            proposal = Proposal(
                user=request.user, 
                proposal_title=request.POST.get('proposal_title'),
                institute_name=request.POST.get('institute_name'),
                institute_address=request.POST.get('institute_address'),
                contact_number=request.POST.get('contact_number'),
                proposal_file=proposal_file,
                category=request.POST.get('category'),
                team_name=request.POST.get('team_name'),
                student1_name=request.POST.get('student1_name'),
                student1_email=request.POST.get('student1_email'),
                student2_name=request.POST.get('student2_name'),
                student2_email=request.POST.get('student2_email'),
                student3_name=request.POST.get('student3_name'),
                student3_email=request.POST.get('student3_email'),
                student4_name=request.POST.get('student4_name'),
                student4_email=request.POST.get('student4_email'),
                faculty_name=request.POST.get('faculty_name'),
                faculty_email=request.POST.get('faculty_email')
            )
            proposal.save()
            messages.success(request, "Proposal submitted successfully!")
            return redirect('submit_proposal')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('submit_proposal')
        except Exception as e:
            messages.error(request, "Error in submission. Please ensure all fields are filled correctly.")
            return redirect('submit_proposal')

    # Add context data to show remaining submissions
    categories_count = {
        category[0]: 10 - Proposal.objects.filter(user=request.user, category=category[0]).count()
        for category in Proposal.CATEGORY_CHOICES
    }
    
    return render(request, 'mriif/submit_proposal.html', {
        'categories_count': categories_count,
        'form': {'fields': {'category': {'choices': Proposal.CATEGORY_CHOICES}}}
    })