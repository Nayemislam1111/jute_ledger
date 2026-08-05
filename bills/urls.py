from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib import admin  # 👈 এডমিন কাস্টমাইজেশনের জন্য ইমপোর্ট করা হলো
from . import views

# 👑 Akij Group Admin Panel Customization
admin.site.site_header = "Akij Group Administration"   # ওপরে নীল বারে প্রদর্শিত হবে
admin.site.site_title = "Akij Group Admin Portal"      # ব্রাউজার ট্যাবে দেখাবে
admin.site.index_title = "Welcome to Akij Group Administration" # ড্যাশবোর্ডের শিরোনাম

urlpatterns = [
    # 🎯 মেইন লিংকে ঢুকলে সরাসরি grade-entry পেজে নিয়ে যাবে
    path('', RedirectView.as_view(pattern_name='grade_entry', permanent=False)), 
    
    # 🔑 Login Route
    path('accounts/login/', auth_views.LoginView.as_view(template_name='bills/login.html'), name='login'),

    # 📌 Main Features
    path('grade-entry/', views.grade_entry_view, name='grade_entry'),
    path('bill-entry/', views.bill_entry_view, name='bill_entry'),
    path('weekly-basis/', views.weekly_basis_view, name='weekly_basis'),

    # 🔑 Logout Route
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 🎯 Bill Edit/Delete 
    path('bill/edit/<int:pk>/', views.edit_bill_view, name='edit_bill'),
    path('bill/delete/<int:pk>/', views.delete_bill_view, name='delete_bill'),
    
    # 🎯 Grade Edit/Delete
    path('grade/edit/<int:pk>/', views.edit_grade_view, name='edit_grade'),
    path('grade/delete/<int:pk>/', views.delete_grade_view, name='delete_grade'),

    # 📊 Export Links
    path('export/grades/', views.export_grades_csv, name='export_grades_csv'),
    path('export/bills/', views.export_bills_csv, name='export_bills_csv'),
    path('export/weekly/', views.export_weekly_csv, name='export_weekly_csv'),
]