from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'), 
    path('issue-book/<int:book_id>/', views.issue_book, name='issue_book'),
    path('profile/', views.profile, name='profile'),
    path('reserve-book/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('return-book/<int:issue_id>/', views.return_book, name='return_book'),
    path('review/<int:book_id>/', views.add_review, name='add_review'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password-verify/', views.reset_password_verify_otp, name='reset_password_verify_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    # library/urls.py

    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # library/urls.py

    path('pay-fine/', views.pay_fine, name='pay_fine'),
    # library/urls.py
    path('lost-and-found/', views.lost_and_found, name='lost_and_found'),
    path('digital-hub/', views.digital_hub, name='digital_hub'),
]
