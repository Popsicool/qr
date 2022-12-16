from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'generator'
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("aboutus", views.aboutus, name="aboutus"),
    path("faq", views.faq, name="faq"),
    path("contactus", views.contactus, name="contactus"),
    path("dashboard", views.dashboard.as_view(), name="dashboard"),
    path("logout", views.logout, name="logout"),
    path("signup", views.signup, name="signup"),
    path('genqr2', views.genqr2.as_view(), name='genqr2'),
    path('qr_design', views.qr_design.as_view(), name='qr_design'),
    path('generate-qr', views.generate_qr.as_view(), name='generate_qr'),
    path('download_qr', views.download_qr.as_view(), name='download_qr'),
    path('download-/<str:id>/<str:file_type>', views.download_file.as_view(), name='download'),
    path('delete/<str:id>', views.delete_file.as_view(), name='delete'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]