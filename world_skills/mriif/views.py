from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import os
import json
import uuid
import re
from django.contrib import messages
from .models import Skill, ContactUs, SPOCRegistration, Proposal, EvaluatorRegistration, Course, CourseApplication, Enquiry
from django.core.exceptions import ValidationError
from .validators import validate_file_size, validate_file_extension
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from django.utils import timezone
from django.views.decorators.http import require_POST
from .utils import verify_recaptcha

# Configure Cashfree
Cashfree.XClientId = settings.CASHFREE_APP_ID
Cashfree.XClientSecret = settings.CASHFREE_SECRET_KEY
Cashfree.XEnvironment = getattr(Cashfree, settings.CASHFREE_ENVIRONMENT)
x_api_version = settings.X_API_VERSION

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

def signup(request):
    # Redirect logged-in users to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Basic form validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists. Please choose another one.")
        if not email:
            errors.append("Email is required.")
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append("Please enter a valid email address.")
        if User.objects.filter(email=email).exists():
            errors.append("Email is already registered. Please use another one.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != password_confirm:
            errors.append("Passwords do not match.")
        
        # If there are validation errors, show them to the user
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('signup')

        # Create new user account
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Log the user in immediately after registration
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to MRIIF.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('signup')

    return render(request, 'mriif/signup.html')

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
        recaptcha_token = request.POST.get('g-recaptcha-response')
        
        # Backend validation with specific error messages
        errors = []
        
        # Validate reCAPTCHA and add to errors array
        recaptcha_success, recaptcha_score = verify_recaptcha(recaptcha_token)
        if not recaptcha_success:
            errors.append("reCAPTCHA verification failed. Please try again.")
        elif recaptcha_score < 0.5:
            errors.append("Security verification failed. Please try again later.")
        
        if not first_name or len(first_name) < 2:
            errors.append("First name must be at least 2 characters long.")
        if not last_name or len(last_name) < 2:
            errors.append("Last name must be at least 2 characters long.")
        if not email:
            errors.append("Email is required.")
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append("Please enter a valid email address.")
        if not message or len(message) < 10:
            errors.append("Message must be at least 10 characters long.")
        if phone and not re.match(r'^[0-9]{10}$', phone):
            errors.append("Phone number must be exactly 10 digits.")

        # If there are validation errors, show them to the user
        if errors:
            for error in errors:
                messages.error(request, error)
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
            # Extract form data from POST request
            institute_name = request.POST.get('institute_name')
            institute_code = request.POST.get('institute_code')
            spoc_name = request.POST.get('spoc_name')
            designation = request.POST.get('designation')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            address = request.POST.get('address')
            state = request.POST.get('state')
            city = request.POST.get('city')
            pincode = request.POST.get('pincode')
            endorsement_letter = request.FILES.get('endorsement_letter')
            declaration = request.POST.get('declaration')
            recaptcha_token = request.POST.get('g-recaptcha-response')
            print(f"reCAPTCHA token: {recaptcha_token}")
            
            # Backend validation with specific error messages
            errors = []
            
            # Validate reCAPTCHA first and add to errors array
            recaptcha_success, recaptcha_score = verify_recaptcha(recaptcha_token)
            if not recaptcha_success:
                errors.append("reCAPTCHA verification failed. Please try again.")
            elif recaptcha_score < 0.5:
                errors.append("Security verification failed. Please try again later.")
            
            if not institute_name or len(institute_name) < 3:
                errors.append("Institute name must be at least 3 characters long.")
            if not institute_code:
                errors.append("Institute code is required.")
            elif not re.match(r'^[A-Z0-9-]+$', institute_code):
                errors.append("Institute code must contain only uppercase letters, numbers and hyphens.")
            if not address or len(address) < 10:
                errors.append("Address must be at least 10 characters long.")
            if not state:
                errors.append("State is required.")
            if not city or len(city) < 2:
                errors.append("City must be at least 2 characters long.")
            if not pincode:
                errors.append("Pincode is required.")
            elif not re.match(r'^[0-9]{6}$', pincode):
                errors.append("Pincode must be exactly 6 digits.")
            if not spoc_name or len(spoc_name) < 3:
                errors.append("SPOC name must be at least 3 characters long.")
            if not designation or len(designation) < 2:
                errors.append("Designation must be at least 2 characters long.")
            if not email:
                errors.append("Email is required.")
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append("Please enter a valid email address.")
            if not mobile:
                errors.append("Mobile number is required.")
            elif not re.match(r'^[0-9]{10}$', mobile):
                errors.append("Mobile number must be exactly 10 digits.")
            if not endorsement_letter:
                errors.append("Endorsement letter is required.")
            if not declaration:
                errors.append("You must agree to the declaration.")
            
            # If there are validation errors, show them to the user
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('spoc_registration')

            # Validate file
            if endorsement_letter:
                validate_file_size(endorsement_letter)
                validate_file_extension(endorsement_letter)
                
            spoc = SPOCRegistration(
                institute_name=institute_name,
                institute_code=institute_code,
                spoc_name=spoc_name,
                designation=designation,
                email=email,
                mobile=mobile,
                address=address,
                state=state,
                city=city,
                pincode=pincode,
                endorsement_letter=endorsement_letter
            )
            spoc.save()
            messages.success(request, "Registration submitted successfully! You will receive credentials via email.")
            return redirect('spoc_registration')
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('spoc_registration')
        except Exception as e:  
            messages.error(request, f"Error in registration: {str(e)}. Please ensure all fields are filled correctly.")
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
            # Extract form data
            proposal_title = request.POST.get('proposal_title')
            category = request.POST.get('category')
            institute_name = request.POST.get('institute_name')
            institute_address = request.POST.get('institute_address')
            contact_number = request.POST.get('contact_number')
            team_name = request.POST.get('team_name')
            student1_name = request.POST.get('student1_name')
            student1_email = request.POST.get('student1_email')
            student2_name = request.POST.get('student2_name')
            student2_email = request.POST.get('student2_email')
            student3_name = request.POST.get('student3_name')
            student3_email = request.POST.get('student3_email')
            student4_name = request.POST.get('student4_name')
            student4_email = request.POST.get('student4_email')
            faculty_name = request.POST.get('faculty_name')
            faculty_email = request.POST.get('faculty_email')
            proposal_file = request.FILES.get('proposal_file')
            declaration = request.POST.get('declaration')
            recaptcha_token = request.POST.get('g-recaptcha-response')
            
            # Backend validation with specific error messages
            errors = []
            
            # Validate reCAPTCHA first and add to errors array
            recaptcha_success, recaptcha_score = verify_recaptcha(recaptcha_token)
            if not recaptcha_success:
                errors.append("reCAPTCHA verification failed. Please try again.")
            elif recaptcha_score < 0.5:
                errors.append("Security verification failed. Please try again later.")
            
            if not proposal_title or len(proposal_title) < 3:
                errors.append("Proposal title must be at least 3 characters long.")
            if not category:
                errors.append("Category is required.")
            if not institute_name or len(institute_name) < 3:
                errors.append("Institute name must be at least 3 characters long.")
            if not institute_address or len(institute_address) < 10:
                errors.append("Institute address must be at least 10 characters long.")
            if not contact_number:
                errors.append("Contact number is required.")
            elif not re.match(r'^[0-9]{10}$', contact_number):
                errors.append("Contact number must be exactly 10 digits.")
            if not team_name:
                errors.append("Team name is required.")
                
            # Validate student information
            for i in range(1, 5):
                student_name = locals()[f'student{i}_name']
                student_email = locals()[f'student{i}_email']
                
                if not student_name or len(student_name) < 3:
                    errors.append(f"Student {i} name must be at least 3 characters long.")
                if not student_email:
                    errors.append(f"Student {i} email is required.")
                elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', student_email):
                    errors.append(f"Please enter a valid email address for student {i}.")
            
            # Validate faculty information
            if not faculty_name:
                errors.append("Faculty name is required.")
            if not faculty_email:
                errors.append("Faculty email is required.")
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', faculty_email):
                errors.append("Please enter a valid email address for faculty.")
                
            # Validate proposal file and declaration
            if not proposal_file:
                errors.append("Proposal file is required.")
            if not declaration:
                errors.append("You must agree to the declaration.")
                
            # If there are validation errors, show them to the user
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('submit_proposal')

            # Check proposal count before processing file
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

            if proposal_file:
                validate_file_size(proposal_file)
                validate_file_extension(proposal_file)
            
            proposal = Proposal(
                user=request.user, 
                proposal_title=proposal_title,
                institute_name=institute_name,
                institute_address=institute_address,
                contact_number=contact_number,
                proposal_file=proposal_file,
                category=category,
                team_name=team_name,
                student1_name=student1_name,
                student1_email=student1_email,
                student2_name=student2_name,
                student2_email=student2_email,
                student3_name=student3_name,
                student3_email=student3_email,
                student4_name=student4_name,
                student4_email=student4_email,
                faculty_name=faculty_name,
                faculty_email=faculty_email
            )
            proposal.save()
            messages.success(request, "Proposal submitted successfully!")
            return redirect('submit_proposal')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('submit_proposal')
        except Exception as e:
            messages.error(request, f"Error in submission: {str(e)}. Please ensure all fields are filled correctly.")
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
    
def evaluator_registration(request):
    if request.method == 'POST':
        try:
            # Extract form data
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            linkedin_url = request.POST.get('linkedin_url')
            organization = request.POST.get('organization')
            designation = request.POST.get('designation')
            experience = request.POST.get('experience')
            expertise = request.POST.getlist('expertise')  # Use getlist() for multiple select
            cv_file = request.FILES.get('cv_file')
            declaration = request.POST.get('declaration')
            recaptcha_token = request.POST.get('g-recaptcha-response')
            
            # Backend validation with specific error messages
            errors = []
            
            # Validate reCAPTCHA first and add to errors array
            recaptcha_success, recaptcha_score = verify_recaptcha(recaptcha_token)
            if not recaptcha_success:
                errors.append("reCAPTCHA verification failed. Please try again.")
            elif recaptcha_score < 0.5:
                errors.append("Security verification failed. Please try again later.")
            
            if not full_name or len(full_name) < 3:
                errors.append("Full name must be at least 3 characters long.")
            if not email:
                errors.append("Email is required.")
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append("Please enter a valid email address.")
            if not mobile:
                errors.append("Mobile number is required.")
            elif not re.match(r'^[0-9]{10}$', mobile):
                errors.append("Mobile number must be exactly 10 digits.")
            if not organization or len(organization) < 2:
                errors.append("Organization name must be at least 2 characters long.")
            if not designation or len(designation) < 2:
                errors.append("Designation must be at least 2 characters long.")
            
            # Validate experience - must be numeric and within range
            if not experience:
                errors.append("Years of experience is required.")
            else:
                try:
                    exp_value = int(experience)
                    if exp_value < 0:
                        errors.append("Experience cannot be negative.")
                    elif exp_value > 50:
                        errors.append("Experience cannot exceed 50 years.")
                except ValueError:
                    errors.append("Experience must be a valid number.")
                    
            if not expertise:
                errors.append("Please select at least one area of expertise.")
            if not cv_file:
                errors.append("CV file is required.")
            if not declaration:
                errors.append("You must agree to the declaration.")
                
            # If there are validation errors, show them to the user
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('evaluator_registration')
            
            # Validate file
            if cv_file:
                validate_file_size(cv_file)
                validate_file_extension(cv_file)
                
            evaluator = EvaluatorRegistration(
                full_name=full_name,
                email=email,
                mobile=mobile,
                linkedin_url=linkedin_url,
                organization=organization,
                designation=designation,
                experience=int(experience),
                expertise=expertise,
                cv_file=cv_file
            )
            evaluator.save()
            messages.success(request, "Thank you for your interest! Your application has been submitted successfully.")
            return redirect('evaluator_registration')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('evaluator_registration')
        except Exception as e:
            messages.error(request, f"Error in submission: {str(e)}. Please ensure all fields are filled correctly including your CV.")
            return redirect('evaluator_registration')

    # Add categories to context
    context = {
        'expertise_choices': Proposal.CATEGORY_CHOICES
    }
    return render(request, 'mriif/evaluator-registration.html', context)

def courses_list(request):
    # Get all course types first
    course_types = dict(Course.COURSE_TYPE_CHOICES)
    
    selected_course_type = request.GET.get('course_type')
    skills = []
    
    if selected_course_type:
        # Get skills that have courses of the selected type
        skills = Skill.objects.filter(
            courses__course_type=selected_course_type,
            courses__active=True
        ).distinct().order_by('job_title')
    
    return render(request, 'mriif/courses.html', {
        'skills': skills,
        'course_types': course_types,
        'selected_course_type': selected_course_type
    })

def get_course_details(request):
    if request.method == 'GET':
        skill_id = request.GET.get('skill_id')
        course_type = request.GET.get('course_type')
        
        if skill_id and course_type:
            try:
                course = Course.objects.get(skill_id=skill_id, course_type=course_type)
                return JsonResponse({
                    'success': True,
                    'training_fee': float(course.training_fee),
                    'residential_fee': float(course.residential_fee) if course.residential_fee else 0,
                    'mode': course.get_delivery_mode_display(),
                    'duration': course.duration_weeks,
                    'id': course.id,
                    'has_residential': course.residential_fee is not None and float(course.residential_fee) > 0
                })
            except Course.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Course not found'})
        
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required(login_url='login')
def course_application(request, course_id=None):
    # If course_id is provided, pre-select that course
    selected_course = None
    course_types = dict(Course.COURSE_TYPE_CHOICES)
    selected_course_type = request.GET.get('course_type')
    course_type_display = None
    courses = []
    
    # Check if residential parameter is provided
    residential_preselect = request.GET.get('residential') == '1'
    
    if course_id:
        selected_course = get_object_or_404(Course, id=course_id)
        selected_course_type = selected_course.course_type
        courses = Course.objects.filter(course_type=selected_course_type, active=True)
        course_type_display = dict(Course.COURSE_TYPE_CHOICES).get(selected_course_type)
    elif selected_course_type:
        courses = Course.objects.filter(course_type=selected_course_type, active=True)
        course_type_display = dict(Course.COURSE_TYPE_CHOICES).get(selected_course_type)
    
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            course = Course.objects.get(id=course_id)
            
            # Check if user already has a pending application for this course
            if CourseApplication.objects.filter(
                user=request.user, 
                course=course,
                status__in=['PENDING', 'PAYMENT_PENDING', 'PAYMENT_COMPLETED', 'CONFIRMED']
            ).exists():
                messages.error(request, "You already have an active application for this course.")
                return redirect('course_application_with_id', course_id=course_id)
            
            # Check if include_residential checkbox is checked
            include_residential = request.POST.get('include_residential') == 'on'
            
            # Calculate total amount based on checkbox
            amount = course.training_fee
            if include_residential and course.residential_fee:
                amount += course.residential_fee
            
            # Create application
            application = CourseApplication(
                course=course,
                user=request.user,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                organization=request.POST.get('organization'),
                designation=request.POST.get('designation'),
                address=request.POST.get('address'),
                state=request.POST.get('state'),
                city=request.POST.get('city'),
                pincode=request.POST.get('pincode'),
                include_residential=include_residential,
                amount=amount,
                status='PAYMENT_PENDING'
            )
            application.save()
            
            # Redirect to payment page
            return redirect('payment_page', application_id=application.id)
            
        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
            return redirect('course_application')
    
    return render(request, 'mriif/course_application.html', {
        'courses': courses,
        'course_types': course_types,
        'selected_course_type': selected_course_type,
        'course_type_display': course_type_display,
        'selected_course': selected_course,
        'residential_preselect': residential_preselect
    })

def payment_page(request, application_id):
    application = get_object_or_404(CourseApplication, id=application_id)
    
    if request.method == 'POST':
        try:
            # Generate a unique order ID
            order_id = str(uuid.uuid4())
            
            # Generate a valid customer_id from email
            customer_id = re.sub(r'[^a-zA-Z0-9_-]', '_', application.email)
            
            # Create customer details - keeping only required fields exactly as per reference
            customer_details = CustomerDetails(
                customer_id=customer_id,
                customer_phone=application.phone
            )
            
            # Update return_url to include the order_id as a query parameter
            return_url = request.build_absolute_uri(reverse('payment_return') + f"?order_id={order_id}")
            
            # Create order meta with the return_url
            order_meta = OrderMeta(return_url=return_url)
            
            # Create order request - exactly matching reference project structure
            create_order_request = CreateOrderRequest(
                order_id=order_id,
                order_amount=float(application.amount),
                order_currency="INR",
                customer_details=customer_details,
                order_meta=order_meta
            )
            
            # Create a payment order
            api_response = Cashfree().PGCreateOrder(x_api_version, create_order_request, None, None)
            
            # Save the order in the database with payment session ID
            application.order_id = order_id  
            application.cf_order_id = api_response.data.cf_order_id
            application.payment_id = api_response.data.payment_session_id
            application.payment_status = api_response.data.order_status
            application.save()
            
            # Return the payment details to the frontend
            return JsonResponse({
                'order_id': api_response.data.order_id,
                'payment_session_id': api_response.data.payment_session_id,
            })
        except Exception as e:
            print(f"Cashfree Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'mriif/payment_page.html', {
        'application': application
    })

def payment_return(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, "Invalid payment request")
        return redirect('home')
    
    try:
        application = CourseApplication.objects.get(order_id=order_id)
        
        # Check payment status with Cashfree
        api_response = Cashfree().PGFetchOrder(x_api_version, order_id, None)
        payment_status = api_response.data.order_status
        
        # Update application based on payment status
        if payment_status == "PAID":
            
            # remove the below lines in production as webhook will handle this   //important
            application.status = "PAYMENT_COMPLETED"
            application.payment_status = "SUCCESS"
            application.payment_date = timezone.now()
            application.save()
            
            messages.success(request, "Payment successful! Your course registration has been confirmed.")
        elif payment_status == "ACTIVE":
            messages.warning(request, "Payment is still in progress. We'll update you once confirmed.")
        else:  # EXPIRED or other status
            messages.error(request, "Payment was not successful. Please try again.")
        
        return render(request, 'mriif/payment_return.html', {
            'application': application,
            'payment_status': payment_status
        })
        
    except CourseApplication.DoesNotExist:
        messages.error(request, "Payment details not found")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

@csrf_exempt
@require_POST
def payment_callback(request):
    """
    Webhook handler for Cashfree payment status updates
    """
    if request.method == 'POST':
        try:
            signature = request.headers.get('x-webhook-signature')
            timestamp = request.headers.get('x-webhook-timestamp')
            
            raw_body = request.body.decode('utf-8')
            webhook_event = Cashfree().PGVerifyWebhookSignature(signature, raw_body, timestamp)
            
            event_data = json.loads(raw_body)
            event_type = event_data.get('type')
            
            if event_type in ['PAYMENT_SUCCESS_WEBHOOK', 'PAYMENT_FAILED_WEBHOOK', 'PAYMENT_USER_DROPPED_WEBHOOK']:
                order_id = event_data['data']['order']['order_id']
                payment_status = event_data['data']['payment']['payment_status']
                
                try:
                    application = CourseApplication.objects.get(order_id=order_id)
                    
                    if payment_status == 'SUCCESS':
                        application.status = 'PAYMENT_COMPLETED'
                        application.payment_status = payment_status
                        application.payment_date = timezone.now()
                        application.save()
                        # Send payment success notification to user
                        # TODO: Implement email notification
                        
                    elif payment_status == 'FAILED':
                        application.status = 'PAYMENT_PENDING'
                        application.payment_status = payment_status
                        application.save()
                        # Send payment failed notification to user
                        # TODO: Implement email notification
                    
                    elif payment_status == 'USER_DROPPED':
                        application.status = 'CANCELLED'
                        application.payment_status = payment_status
                        application.save()
                        # Optionally, send a notification to the user about the dropped payment
                        # TODO: Implement email or SMS notification
                        
                except CourseApplication.DoesNotExist:
                    return HttpResponse(status=404)
            
            return HttpResponse(status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.groups.filter(name='staff').exists() or u.is_superuser)
def staff_dashboard(request):
    """
    Dashboard for staff members to view contact submissions and applications
    """
    # Get data for the dashboard based on filters
    tab = request.GET.get('tab', 'overview')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Get contact submissions with filters
    contacts_query = ContactUs.objects.all().order_by('-id')
    
    if search_query:
        contacts_query = contacts_query.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            contacts_query = contacts_query.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            contacts_query = contacts_query.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Get application submissions with filters
    applications_query = CourseApplication.objects.all().order_by('-id')
    
    if search_query:
        applications_query = applications_query.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            applications_query = applications_query.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            applications_query = applications_query.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Pagination for contacts
    page = request.GET.get('page', 1)
    contacts_paginator = Paginator(contacts_query, 10)  # Show 10 contacts per page
    
    try:
        contacts_page = contacts_paginator.page(page)
    except PageNotAnInteger:
        contacts_page = contacts_paginator.page(1)
    except EmptyPage:
        contacts_page = contacts_paginator.page(contacts_paginator.num_pages)
    
    # Pagination for applications
    applications_paginator = Paginator(applications_query, 10)  # Show 10 applications per page
    
    try:
        applications_page = applications_paginator.page(page)
    except PageNotAnInteger:
        applications_page = applications_paginator.page(1)
    except EmptyPage:
        applications_page = applications_paginator.page(applications_paginator.num_pages)
    
    # Dashboard statistics
    stats = {
        'total_contacts': ContactUs.objects.count(),
        'total_applications': CourseApplication.objects.count(),
        'pending_payments': CourseApplication.objects.filter(status='PAYMENT_PENDING').count(),
        'completed_payments': CourseApplication.objects.filter(status='PAYMENT_COMPLETED').count(),
    }
    
    # Prepare context for the template
    context = {
        'contacts': contacts_query,
        'contacts_page': contacts_page,
        'applications': applications_query,
        'applications_page': applications_page,
        'all_contacts': contacts_query,  # For PDF export
        'all_applications': applications_query,  # For PDF export
        'stats': stats,
        'tab': tab,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'mriif/staff_dashboard.html', context)

def submit_enquiry(request):
    """Handle quick enquiry form submissions from the home page"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            course = request.POST.get('course')
            city = request.POST.get('city')
            traffic_source = request.POST.get('traffic_source', '')
            how_did_you_hear = request.POST.get('how_did_you_hear', '')
            recaptcha_token = request.POST.get('g-recaptcha-response')
            
            # Basic validation with errors array
            errors = []
            
            # Validate reCAPTCHA and add to errors array
            recaptcha_success, recaptcha_score = verify_recaptcha(recaptcha_token)
            if not recaptcha_success:
                errors.append("reCAPTCHA verification failed. Please try again.")
            elif recaptcha_score < 0.5:
                errors.append("Security verification failed. Please try again later.")
            
            if not name or len(name) < 2:
                errors.append("Name must be at least 2 characters long.")
            if not email:
                errors.append("Email is required.")
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append("Please enter a valid email address.")
            if not mobile:
                errors.append("Mobile number is required.")
            elif not re.match(r'^[0-9]{10}$', mobile):
                errors.append("Mobile number must be exactly 10 digits.")
            if not course:
                errors.append("Please select a course of interest.")
            if not city:
                errors.append("City is required.")
            if not how_did_you_hear:
                errors.append("Please tell us how you heard about us.")
                
            # If there are validation errors, show them to the user
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('home')
            
            # If no traffic source is passed, try to determine from HTTP_REFERER
            if not traffic_source:
                referer = request.META.get('HTTP_REFERER', '')
                if 'google' in referer.lower():
                    traffic_source = 'Google'
                elif 'facebook' in referer.lower() or 'fb.com' in referer.lower():
                    traffic_source = 'Facebook'
                elif 'instagram' in referer.lower():
                    traffic_source = 'Instagram'
                elif 'linkedin' in referer.lower():
                    traffic_source = 'LinkedIn'
                else:
                    traffic_source = 'Direct'
            
            # Save the enquiry to the database
            enquiry = Enquiry(
                name=name,
                email=email,
                mobile=mobile,
                course=course,
                city=city,
                traffic_source=traffic_source,
                how_did_you_hear=how_did_you_hear
            )
            enquiry.save()
            
            messages.success(request, "Thank you for your enquiry! Our team will get back to you shortly.")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error submitting enquiry: {str(e)}")
            return redirect('home')
            
    return redirect('home')

def check_user_exists(request):
    """Check if a username or email already exists in the system"""
    if request.method == 'GET':
        username = request.GET.get('username')
        email = request.GET.get('email')
        
        response = {'username_exists': False, 'email_exists': False}
        
        if username:
            response['username_exists'] = User.objects.filter(username=username).exists()
        
        if email:
            response['email_exists'] = User.objects.filter(email=email).exists()
            
        return JsonResponse(response)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required(login_url='login')
def user_dashboard(request):
    """
    Dashboard for users to view their applications and resume payment if needed
    """
    # Get all applications for the current user
    applications = CourseApplication.objects.filter(user=request.user).order_by('-id')
    
    # Dashboard statistics
    stats = {
        'total_applications': applications.count(),
        'pending_payments': applications.filter(status='PAYMENT_PENDING').count(),
        'completed_payments': applications.filter(status='PAYMENT_COMPLETED').count(),
        'confirmed': applications.filter(status='CONFIRMED').count(),
    }
    
    # Prepare context for the template
    context = {
        'applications': applications,
        'stats': stats,
    }
    
    return render(request, 'mriif/user_dashboard.html', context)

@login_required(login_url='login')
def resume_application(request, application_id):
    """
    Resume a pending application and redirect to payment page
    """
    application = get_object_or_404(CourseApplication, id=application_id, user=request.user)
    
    # Only allow resuming applications with payment pending
    if application.status != 'PAYMENT_PENDING':
        messages.error(request, "This application cannot be resumed as its status is not pending payment.")
        return redirect('user_dashboard')
    
    return redirect('payment_page', application_id=application.id)

def check_duplicate_application(request):
    """
    AJAX endpoint to check if a user has already applied for a specific course
    """
    if request.method == 'GET':
        course_id = request.GET.get('course_id')
        
        if course_id and request.user.is_authenticated:
            # Check if the current user already has an application for this course
            existing_application = CourseApplication.objects.filter(
                user=request.user,
                course_id=course_id,
                status__in=['PENDING', 'PAYMENT_PENDING', 'PAYMENT_COMPLETED', 'CONFIRMED']
            ).first()
            
            if existing_application:
                return JsonResponse({
                    'duplicate': True,
                    'message': f"You already have an active application for this course (Status: {existing_application.get_status_display()})"
                })
        
        return JsonResponse({'duplicate': False})
    
    return JsonResponse({'error': 'Invalid request method'})