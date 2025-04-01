from django.urls import path
from users import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.SignupPage, name = 'signup'),
    path('login/', views.LoginPage, name = 'login'), 
    path('jobseeker_dashboard', views.jobseeker_dashboard, name= "jobseeker_dashboard"),
    path('recruiter_dashboard', views.recruiter_dashboard, name= "recruiter_dashboard"),
    path('logout/', views.Logout_user, name = 'logout'),
    path('jobseeker-profile/', views.update_user_profile, name='jobseeker_profile'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="reset_pass/password_reset.html"), name="password_reset"),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="reset_pass/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset_pass/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="reset_pass/password_reset_complete.html"), name="password_reset_complete"),

]