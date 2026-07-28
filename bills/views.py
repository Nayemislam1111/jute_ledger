import csv
import json
from collections import defaultdict
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, Avg, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import GradeEntry, JuteRate, BillEntry


# ==========================================
# 1. Grade Entry View
# ==========================================
@login_required
def grade_entry_view(request):
    if request.method == 'POST':
        entry_date = request.POST.get('date') or timezone.now().date()
        
        GradeEntry.objects.create(
            user=request.user,  # 🎯 বর্তমান লগইন করা ইউজার অটো-সেভ হবে
            lot_no=request.POST.get('lot_no'),
            id_no=request.POST.get('id_no'),
            area=request.POST.get('area', '').strip(),
            under_project=request.POST.get('under_project'),
            c_pct=request.POST.get('c_pct') or 0,
            d1_pct=request.POST.get('d1_pct') or 0,
            d2_pct=request.POST.get('d2_pct') or 0,
            e1_pct=request.POST.get('e1_pct') or 0,
            e2_pct=request.POST.get('e2_pct') or 0,
            smr_pct=request.POST.get('smr_pct') or 0,
            date=entry_date, 
            total_mds=request.POST.get('total_mds') or 0
        )
        return redirect('grade_entry')

    # 👑 সুপারইউজার বনাম 🏢 সেন্টার ইউজার ডাটা ফিল্টারিং
    if request.user.is_superuser:
        grades = GradeEntry.objects.all().order_by('-id')
    else:
        grades = GradeEntry.objects.filter(user=request.user).order_by('-id')
    
    # Search Filter
    search_query = request.GET.get('search_query', '').strip()
    if search_query:
        grades = grades.filter(
            Q(lot_no__icontains=search_query) |
            Q(id_no__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(under_project__icontains=search_query)
        )

    # এরিয়ার আন্ডারে সব তারিখের রেটের লিস্ট ফ্রন্টএন্ডে পাঠানো হচ্ছে
    all_rates = JuteRate.objects.all().order_by('area', '-effect_date')
    rates_dict = {}
    for r in all_rates:
        ak = r.area.strip().lower()
        if ak not in rates_dict: 
            rates_dict[ak] = []
        
        rates_dict[ak].append({
            'effect_date': r.effect_date.strftime('%Y-%m-%d') if r.effect_date else '',
            'c': float(r.c_rate or 0),
            'd1': float(r.d1_rate or 0),
            'd2': float(r.d2_rate or 0),
            'e1': float(r.e1_rate or 0),
            'e2': float(r.e2_rate or 0),
            'smr': float(r.smr_rate or 0)
        })
            
    return render(request, 'bills/grade_entry.html', {
        'grades': grades, 
        'rates_json': json.dumps(rates_dict),
        'search_query': search_query
    })


# ==========================================
# 2. Bill Entry View
# ==========================================
@login_required
def bill_entry_view(request):
    if request.method == 'POST':
        entry_date = request.POST.get('date') or timezone.now().date()
        BillEntry.objects.create(
            user=request.user,  # 🎯 বর্তমান লগইন করা ইউজার অটো-সেভ হবে
            lot_no=request.POST.get('lot_no'),
            id_no=request.POST.get('id_no'),
            area=request.POST.get('area', '').strip(),
            name=request.POST.get('name'),
            jute_mon=request.POST.get('jute_mon') or 0,
            rate=request.POST.get('rate') or 0,
            date=entry_date,
        )
        return redirect('bill_entry')

    # 👑 সুপারইউজার বনাম 🏢 সেন্টার ইউজার ডাটা ফিল্টারিং
    if request.user.is_superuser:
        bills = BillEntry.objects.all().order_by('-id')
    else:
        bills = BillEntry.objects.filter(user=request.user).order_by('-id')
    
    # Search Filter
    search_query = request.GET.get('search_query', '').strip()
    if search_query:
        bills = bills.filter(
            Q(lot_no__icontains=search_query) |
            Q(id_no__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    return render(request, 'bills/bill_entry.html', {
        'bills': bills,
        'search_query': search_query
    })


# ==========================================
# 3. Weekly Basis View (আপডেট করা হয়েছে)
# ==========================================
# ==========================================
# 3. Weekly Basis View (ডিফল্ট অ্যাডমিন ও আগের ডাটা সাপোর্টসহ)
# ==========================================
@login_required
def weekly_basis_view(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    selected_user_id = request.GET.get('user_id', '').strip()
    search_query = request.GET.get('search_query', '').strip()
    
    # 👑 সুপারইউজার/অ্যাডমিন ফিল্টারিং লজিক
    if request.user.is_superuser:
        if selected_user_id:
            # 🎯 নির্দিষ্ট যে সেন্টার সিলেক্ট করা হবে, শুধুমাত্র সেই সেন্টারের ডাটা দেখাবে
            bills = BillEntry.objects.filter(user_id=selected_user_id).select_related('user').order_by('-id')
            grades = GradeEntry.objects.filter(user_id=selected_user_id).select_related('user').order_by('-id')
        else:
            # 🎯 ডিফল্টভাবে অ্যাডমিনের নিজস্ব ডাটা + আগের যেসব ডাটায় user=None ছিল সেগুলা একসাথে দেখাবে
            bills = BillEntry.objects.filter(
                Q(user=request.user) | Q(user__isnull=True)
            ).select_related('user').order_by('-id')
            
            grades = GradeEntry.objects.filter(
                Q(user=request.user) | Q(user__isnull=True)
            ).select_related('user').order_by('-id')
    else:
        # সাধারণ সেন্টার ইউজাররা শুধুমাত্র তাদের নিজস্ব ডাটা দেখতে পাবে
        bills = BillEntry.objects.filter(user=request.user).select_related('user').order_by('-id')
        grades = GradeEntry.objects.filter(user=request.user).select_related('user').order_by('-id')

    # 📅 তারিখ অনুযায়ী ফিল্টার
    if from_date and to_date:
        bills = bills.filter(date__range=[from_date, to_date])
        grades = grades.filter(date__range=[from_date, to_date])
    
    # 🔍 সার্চ কিউয়েরি ফিল্টার
    if search_query:
        bills = bills.filter(
            Q(lot_no__icontains=search_query) | Q(id_no__icontains=search_query) | 
            Q(area__icontains=search_query) | Q(name__icontains=search_query)
        )
        grades = grades.filter(
            Q(lot_no__icontains=search_query) | Q(id_no__icontains=search_query) | 
            Q(area__icontains=search_query) | Q(under_project__icontains=search_query)
        )
    
    bill_averages = bills.aggregate(avg_bill_rate=Avg('rate'), avg_jute=Avg('jute_mon'))
    
    total_amount_sum = 0.0
    total_mds_sum = 0.0
    
    for grade in grades:
        rate_obj = JuteRate.objects.filter(
            area__iexact=grade.area.strip(),
            effect_date__lte=grade.date
        ).order_by('-effect_date').first()
        
        if rate_obj:
            c_pct = float(grade.c_pct or 0)
            d1_pct = float(grade.d1_pct or 0)
            d2_pct = float(grade.d2_pct or 0)
            e1_pct = float(grade.e1_pct or 0)
            e2_pct = float(grade.e2_pct or 0)
            smr_pct = float(grade.smr_pct or 0)
            total_mds = float(grade.total_mds or 0)
            
            effective_rate = (
                (c_pct * float(rate_obj.c_rate or 0)) +
                (d1_pct * float(rate_obj.d1_rate or 0)) +
                (d2_pct * float(rate_obj.d2_rate or 0)) +
                (e1_pct * float(rate_obj.e1_rate or 0)) +
                (e2_pct * float(rate_obj.e2_rate or 0)) +
                (smr_pct * float(rate_obj.smr_rate or 0))
            ) / 100.0
            
            grade.calculated_rate = effective_rate  
            grade.amount = effective_rate * total_mds
            
            total_amount_sum += grade.amount
            total_mds_sum += total_mds
        else:
            grade.calculated_rate = 0
            grade.amount = 0
            total_mds_sum += float(grade.total_mds or 0)
            
    avg_admin_grade_rate = total_amount_sum / total_mds_sum if total_mds_sum > 0 else 0
    
    # 🎯 ড্রপডাউনে Admin সহ সব সেন্টার ইউজার দেখাবে
    all_users = User.objects.all().order_by('username')
    
    context = {
        'bills': bills, 
        'grades': grades,
        'all_users': all_users,
        'selected_user_id': selected_user_id,
        'avg_bill_rate': bill_averages['avg_bill_rate'] or 0,
        'avg_jute': bill_averages['avg_jute'] or 0,
        'avg_admin_grade_rate': avg_admin_grade_rate,
        'from_date': from_date, 
        'to_date': to_date, 
        'search_query': search_query,
        'grand_total_mds': total_mds_sum,
        'grand_total_amount': total_amount_sum,
    }
    return render(request, 'bills/weekly_basis.html', context)


# ==========================================
# 4. Export Functions
# ==========================================
@login_required
def export_grades_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="grade_entries_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Lot No', 'ID No', 'Area', 'Project', 'Total Mds', 'C%', 'D1%', 'D2%', 'E1%', 'E2%', 'SMR%'])
    
    search_query = request.GET.get('search_query', '').strip()
    
    if request.user.is_superuser:
        grades = GradeEntry.objects.all().order_by('-id')
    else:
        grades = GradeEntry.objects.filter(user=request.user).order_by('-id')

    if search_query:
        grades = grades.filter(
            Q(lot_no__icontains=search_query) | Q(id_no__icontains=search_query) |
            Q(area__icontains=search_query) | Q(under_project__icontains=search_query)
        )
        
    for g in grades:
        writer.writerow([g.date, g.lot_no, g.id_no, g.area, g.under_project, g.total_mds, g.c_pct, g.d1_pct, g.d2_pct, g.e1_pct, g.e2_pct, g.smr_pct])
        
    return response


@login_required
def export_bills_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="bill_entries_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Lot No', 'ID No', 'Area', 'Name', 'Jute (Mon)', 'Rate', 'Total Amount'])
    
    search_query = request.GET.get('search_query', '').strip()
    
    if request.user.is_superuser:
        bills = BillEntry.objects.all().order_by('-id')
    else:
        bills = BillEntry.objects.filter(user=request.user).order_by('-id')

    if search_query:
        bills = bills.filter(
            Q(lot_no__icontains=search_query) | Q(id_no__icontains=search_query) |
            Q(area__icontains=search_query) | Q(name__icontains=search_query)
        )
        
    for b in bills:
        total_amount = float(b.jute_mon or 0) * float(b.rate or 0)
        writer.writerow([b.date if hasattr(b, 'date') else '', b.lot_no, b.id_no, b.area, b.name, b.jute_mon, b.rate, total_amount])
        
    return response


@login_required
def export_weekly_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="weekly_area_summary_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Area (এরিয়া)', 'Total Lots (লট সংখ্যা)', 'Avg C%', 'Avg D1%', 'Avg D2%', 'Avg E1%', 'Avg E2%', 'Avg SMR%', 'Avg Rate', 'Total Mds', 'Total Amount'])
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    selected_user_id = request.GET.get('user_id', '').strip()
    search_query = request.GET.get('search_query', '').strip()
    
    if request.user.is_superuser:
        if selected_user_id:
            grades = GradeEntry.objects.filter(user_id=selected_user_id).order_by('-id')
        else:
            grades = GradeEntry.objects.filter(user=request.user).order_by('-id')
    else:
        grades = GradeEntry.objects.filter(user=request.user).order_by('-id')

    if from_date and to_date:
        grades = grades.filter(date__range=[from_date, to_date])
    if search_query:
        grades = grades.filter(
            Q(lot_no__icontains=search_query) | Q(id_no__icontains=search_query) | 
            Q(area__icontains=search_query) | Q(under_project__icontains=search_query)
        )
        
    area_summary = defaultdict(lambda: {
        'lot_count': 0,
        'c_sum': 0.0,
        'd1_sum': 0.0,
        'd2_sum': 0.0,
        'e1_sum': 0.0,
        'e2_sum': 0.0,
        'smr_sum': 0.0,
        'rate_sum': 0.0,
        'total_mds': 0.0,
        'total_amount': 0.0
    })
        
    for grade in grades:
        rate_obj = JuteRate.objects.filter(
            area__iexact=grade.area.strip(), 
            effect_date__lte=grade.date
        ).order_by('-effect_date').first()
        
        if rate_obj:
            effective_rate = ((float(grade.c_pct or 0) * float(rate_obj.c_rate or 0)) +
                              (float(grade.d1_pct or 0) * float(rate_obj.d1_rate or 0)) +
                              (float(grade.d2_pct or 0) * float(rate_obj.d2_rate or 0)) +
                              (float(grade.e1_pct or 0) * float(rate_obj.e1_rate or 0)) +
                              (float(grade.e2_pct or 0) * float(rate_obj.e2_rate or 0)) +
                              (float(grade.smr_pct or 0) * float(rate_obj.smr_rate or 0))) / 100.0
            amount = effective_rate * float(grade.total_mds or 0)
        else:
            effective_rate, amount = 0, 0
            
        area_name = grade.area.strip()
        area_summary[area_name]['lot_count'] += 1
        area_summary[area_name]['c_sum'] += float(grade.c_pct or 0)
        area_summary[area_name]['d1_sum'] += float(grade.d1_pct or 0)
        area_summary[area_name]['d2_sum'] += float(grade.d2_pct or 0)
        area_summary[area_name]['e1_sum'] += float(grade.e1_pct or 0)
        area_summary[area_name]['e2_sum'] += float(grade.e2_pct or 0)
        area_summary[area_name]['smr_sum'] += float(grade.smr_pct or 0)
        area_summary[area_name]['rate_sum'] += effective_rate
        area_summary[area_name]['total_mds'] += float(grade.total_mds or 0)
        area_summary[area_name]['total_amount'] += amount
        
    grand_lots = 0
    grand_mds = 0.0
    grand_amount = 0.0

    for area, data in area_summary.items():
        count = data['lot_count']
        
        avg_c = data['c_sum'] / count if count > 0 else 0
        avg_d1 = data['d1_sum'] / count if count > 0 else 0
        avg_d2 = data['d2_sum'] / count if count > 0 else 0
        avg_e1 = data['e1_sum'] / count if count > 0 else 0
        avg_e2 = data['e2_sum'] / count if count > 0 else 0
        avg_smr = data['smr_sum'] / count if count > 0 else 0
        avg_rate = data['rate_sum'] / count if count > 0 else 0
        
        writer.writerow([
            area, 
            count, 
            f"{avg_c:.2f}%", 
            f"{avg_d1:.2f}%", 
            f"{avg_d2:.2f}%", 
            f"{avg_e1:.2f}%", 
            f"{avg_e2:.2f}%", 
            f"{avg_smr:.2f}%", 
            f"{avg_rate:.2f}", 
            f"{data['total_mds']:.2f}", 
            f"{data['total_amount']:.2f}"
        ])
        
        grand_lots += count
        grand_mds += data['total_mds']
        grand_amount += data['total_amount']
        
    writer.writerow([])
    writer.writerow([
        'GRAND TOTAL (সর্বমোট)', 
        grand_lots, 
        '', '', '', '', '', '', '', 
        f"{grand_mds:.2f}", 
        f"{grand_amount:.2f}"
    ])
        
    return response


# ==========================================
# 5. Edit & Delete Views
# ==========================================
@login_required
def edit_grade_view(request, pk):
    if request.user.is_superuser:
        grade = get_object_or_404(GradeEntry, id=pk)
    else:
        grade = get_object_or_404(GradeEntry, id=pk, user=request.user)

    if request.method == 'POST':
        grade.lot_no = request.POST.get('lot_no')
        grade.id_no = request.POST.get('id_no')
        grade.area = request.POST.get('area', '').strip()
        grade.under_project = request.POST.get('under_project')
        grade.total_mds = request.POST.get('total_mds') or 0
        grade.c_pct = request.POST.get('c_pct') or 0
        grade.d1_pct = request.POST.get('d1_pct') or 0
        grade.d2_pct = request.POST.get('d2_pct') or 0
        grade.e1_pct = request.POST.get('e1_pct') or 0
        grade.e2_pct = request.POST.get('e2_pct') or 0
        grade.smr_pct = request.POST.get('smr_pct') or 0
        grade.date = request.POST.get('date') or grade.date
        grade.save()
        return redirect('grade_entry')
    return render(request, 'bills/edit_grade.html', {'grade': grade})

@login_required
def delete_grade_view(request, pk):
    if request.user.is_superuser:
        grade = get_object_or_404(GradeEntry, id=pk)
    else:
        grade = get_object_or_404(GradeEntry, id=pk, user=request.user)
    grade.delete()
    return redirect('grade_entry')

@login_required
def edit_bill_view(request, pk):
    if request.user.is_superuser:
        bill = get_object_or_404(BillEntry, id=pk)
    else:
        bill = get_object_or_404(BillEntry, id=pk, user=request.user)

    if request.method == 'POST':
        bill.lot_no = request.POST.get('lot_no')
        bill.id_no = request.POST.get('id_no')
        bill.area = request.POST.get('area', '').strip()
        bill.name = request.POST.get('name')
        bill.jute_mon = request.POST.get('jute_mon') or 0
        bill.rate = request.POST.get('rate') or 0
        bill.date = request.POST.get('date') or bill.date
        bill.save()
        return redirect('bill_entry')
    return render(request, 'bills/edit_bill.html', {'bill': bill})

@login_required
def delete_bill_view(request, pk):
    if request.user.is_superuser:
        bill = get_object_or_404(BillEntry, id=pk)
    else:
        bill = get_object_or_404(BillEntry, id=pk, user=request.user)
    bill.delete()
    return redirect('bill_entry')