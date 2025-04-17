from django.urls import path
from jobs import views

urlpatterns = [
    path('details/<int:job_id>/', views.job_details, name="job_details"),
    path('view_applications/<int:job_id>',views.view_appliaction, name = "view_applications"),
    path('create_company_profile/', views.create_company_profile, name="create_company_profile"), 
    path('post_new_job/', views.post_job, name = "post_new_job"),
    path('job_list/', views.job_list, name = "job_list"),
    path('job_edit/<int:job_id>', views.update_job, name = 'update_job'),
    path('job_delete/<int:job_id>', views.delete_job, name = "delete_job"),
    path('apply_job/<int:job_id>', views.apply_job, name = "apply_job"),
    path('view_all_applications/', views.view_all_applications, name="view_all_applications"),
    path("update-application-status/<int:app_id>/<str:status>/", views.update_application_status, name="update_application_status"),
    path("update-application/<int:app_id>/<str:status>/", views.update_job_application, name="update_job_application"),
    path("my-application/", views.my_application, name="my_application"),
    path('withdraw-application/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    path('job-recommendation/', views.recommended_jobs, name='job_recommendation'),
]
