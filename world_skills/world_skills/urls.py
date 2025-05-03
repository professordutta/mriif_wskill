"""
URL configuration for world_skills project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mriif import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
admin.site.site_header = 'NSDC World Skills Academy'
admin.site.site_title = 'NSDC World Skills Academy'
admin.site.index_title = 'Welcome to NSDC World Skills Academy'
urlpatterns = [
    # your other url patterns
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logoutuser, name='logout'),
    path('', views.home, name='home'),
    path('contact', views.contact, name='contact'),
    path('about', views.about, name='about'),
    path('skill/<int:skill_id>/', views.skill_detail, name='skill_detail'),
    path('spoc_registration/', views.spoc_registration, name='spoc_registration'),
    path('hackathon/', views.hackathon, name='hackathon'),
    path('download-endorsement-template/', views.download_endorsement_template, name='download_endorsement_template'),
    path('submit-proposal/', views.submit_proposal, name='submit_proposal'),
    path('evaluator_registration/', views.evaluator_registration, name='evaluator_registration'),
    path('submit-enquiry/', views.submit_enquiry, name='submit_enquiry'),
    
    # Staff Dashboard
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # New URL patterns for course application system
    path('courses/', views.courses_list, name='courses_list'),
    path('get_course_details/', views.get_course_details, name='get_course_details'),
    path('apply/', views.course_application, name='course_application'),
    path('apply/<int:course_id>/', views.course_application, name='course_application_with_id'),
    path('payment/<int:application_id>/', views.payment_page, name='payment_page'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/return/', views.payment_return, name='payment_return'),
    
    # User account integration routes
    path('my-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('resume-application/<int:application_id>/', views.resume_application, name='resume_application'),
    path('check-duplicate-application/', views.check_duplicate_application, name='check_duplicate_application'),
    path('check-user-exists/', views.check_user_exists, name='check_user_exists'),
    
    # New URL patterns for enquiry note functionality
    path('save-enquiry-notes/', views.save_enquiry_notes, name='save_enquiry_notes'),
    path('get-enquiry-notes/', views.get_enquiry_notes, name='get_enquiry_notes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
