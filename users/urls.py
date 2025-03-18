from django.urls import path
from users import views

urlpatterns = [
    path('signup/', views.SignupPage, name = 'signup'),
    path('login/', views.LoginPage, name = 'login'), 
    path('jobseeker_dashboard', views.jobseeker_dashboard, name= "jobseeker_dashboard"),
    path('recruiter_dashboard', views.recruiter_dashboard, name= "recruiter_dashboard"),
    path('logout/', views.Logout_user, name = 'logout'),
    path('jobseeker-profile/', views.update_user_profile, name='jobseeker_profile'),
]