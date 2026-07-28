from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import GradeEntry, BillEntry, JuteRate
from .ai_helpers import update_area_forecasting  # 🤖 এআই হেল্পার ফাংশনটি ইম্পোর্ট করা হলো


@admin.register(GradeEntry)
class GradeEntryAdmin(admin.ModelAdmin):
    list_display = ('lot_no', 'area', 'id_no', 'under_project', 'center', 'user')
    list_filter = ('center', 'area')
    search_fields = ('lot_no', 'area')

    # 👑 সেন্ট্রাল ইউজার বনাম 🏢 সেন্টার ইউজারের ফিল্টারিং
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সেন্ট্রাল ইউজার ১০টি সেন্টারের সব ডেটা দেখতে পাবে
        return qs.filter(user=request.user)  # সাধারণ ইউজার শুধু নিজের সেন্টারের ডেটা দেখতে পাবে

    # ✍️ সেভ করার সময় ইউজার অটো-অ্যাসাইন লজিক
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(BillEntry)
class BillEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'lot_no', 'jute_mon', 'rate', 'center', 'user')
    list_filter = ('center', 'area')
    search_fields = ('name', 'area', 'lot_no')

    # 👑 সেন্ট্রাল ইউজার বনাম 🏢 সেন্টার ইউজারের ফিল্টারিং
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # ✍️ সেভ করার সময় ইউজার অটো-অ্যাসাইন লজিক
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)


# 🎯 অ্যাকশন বাটন, ১০ সেন্টার কন্ট্রোল এবং AI ফোরকাস্ট কলামসহ জুট রেট অ্যাডমিন কনফিগারেশন
@admin.register(JuteRate)
class JuteRateAdmin(admin.ModelAdmin):
    list_display = (
        'area', 'center', 'effect_date', 'c_rate', 'd1_rate', 'd2_rate', 
        'e1_rate', 'e2_rate', 'smr_rate', 
        'predicted_next_rate', 'ai_confidence_score', 'user', # 🤖 AI & User কলামসমূহ
        'edit_link', 'delete_link'
    )
    
    list_filter = ('center', 'area', 'effect_date')
    search_fields = ('area',)

    # 👑 সেন্ট্রাল ইউজার বনাম 🏢 সেন্টার ইউজারের ফিল্টারিং
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সেন্ট্রাল ইউজার ১০টি সেন্টারের সব ডেটা দেখতে পাবে
        return qs.filter(user=request.user)  # সেন্টার ইউজার শুধু নিজের ডেটা দেখতে পাবে

    # 🤖 জ্যাঙ্গো অ্যাডমিনে রেট সেভ হওয়ার পর অটো-ইউজার ও AI ফোরকাস্ট রান করার লজিক
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        # প্রথমে নরমাল ডেটাবেস সেভ সম্পন্ন হবে
        super().save_model(request, obj, form, change)
        # সেভ হওয়ার পর ওই নির্দিষ্ট এরিয়ার জন্য এআই প্রেডিকশন রান হবে
        update_area_forecasting(obj.area)

    # ✏️ কাস্টম ইডিট বাটন লিংক
    def edit_link(self, obj):
        url = reverse('admin:bills_juterate_change', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background-color: #447e9b; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold; text-decoration: none; font-size: 11px;">✏️ Edit</a>', 
            url
        )
    edit_link.short_description = 'Edit'

    # ❌ কাস্টম ডিলিট বাটন লিংক
    def delete_link(self, obj):
        url = reverse('admin:bills_juterate_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background-color: #ba2121; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold; text-decoration: none; font-size: 11px;">🗑️ Delete</a>', 
            url
        )
    delete_link.short_description = 'Delete'