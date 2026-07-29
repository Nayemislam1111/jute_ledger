from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

# 🏢 ১০টি সেন্টারের তালিকা
CENTER_CHOICES = [
    ('center_1', 'সেন্টার ১'),
    ('center_2', 'সেন্টার ২'),
    ('center_3', 'সেন্টার ৩'),
    ('center_4', 'সেন্টার ৪'),
    ('center_5', 'সেন্টার ৫'),
    ('center_6', 'সেন্টার ৬'),
    ('center_7', 'সেন্টার ৭'),
    ('center_8', 'সেন্টার ৮'),
    ('center_9', 'সেন্টার ৯'),
    ('center_10', 'সেন্টার ১০'),
]

class GradeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="অপারেটর")
    center = models.CharField(max_length=50, choices=CENTER_CHOICES, verbose_name="সেন্টার", null=True, blank=True)
    lot_no = models.CharField(max_length=50)
    id_no = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    under_project = models.CharField(max_length=100)
    c_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    d1_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    d2_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    e1_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    e2_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    smr_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    date = models.DateField() 
    total_mds = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Lot: {self.lot_no} - Area: {self.area} ({self.get_center_display() if self.center else 'No Center'})"


class BillEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="অপারেটর")
    center = models.CharField(max_length=50, choices=CENTER_CHOICES, verbose_name="সেন্টার", null=True, blank=True)
    lot_no = models.CharField(max_length=50)
    id_no = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    name = models.CharField(max_length=150)
    jute_mon = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Bill Lot: {self.lot_no} - Name: {self.name} ({self.get_center_display() if self.center else 'No Center'})"


class JuteRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="অপারেটর")
    center = models.CharField(max_length=50, choices=CENTER_CHOICES, verbose_name="সেন্টার", null=True, blank=True)
    area = models.CharField(max_length=100)
    effect_date = models.DateField(default="2026-01-01", verbose_name="রেট কার্যকর হওয়ার তারিখ") 
    c_rate = models.FloatField(default=5800.0, verbose_name="C Rate")
    d1_rate = models.FloatField(default=5650.0, verbose_name="D(I) Rate")
    d2_rate = models.FloatField(default=5500.0, verbose_name="D(II) Rate")
    e1_rate = models.FloatField(default=5300.0, verbose_name="E(I) Rate")
    e2_rate = models.FloatField(default=5100.0, verbose_name="E(II) Rate")
    smr_rate = models.FloatField(default=4925.0, verbose_name="SMR Rate")
    updated_at = models.DateTimeField(auto_now=True)

    # 🎯 AI Price Forecasting
    predicted_next_rate = models.FloatField(null=True, blank=True, verbose_name="AI আনুমানিক আগামী রেট")
    ai_confidence_score = models.FloatField(null=True, blank=True, verbose_name="AI কনফিডেন্স স্কোর (%)")

    class Meta:
        ordering = ['-effect_date']

    def __str__(self):
        return f"{self.area} ({self.get_center_display() if self.center else 'No Center'})"


# 🎯 Render-এ অটোমেটিক সুপারইউজার তৈরি ও পাসওয়ার্ড সিঙ্ক করার জন্য সিগন্যাল
@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username='akijgroup').exists():
        User.objects.create_superuser('akijgroup', 'admin@example.com', '825662')
        print("Superuser 'akijgroup' created successfully!")
    else:
        user = User.objects.get(username='akijgroup')
        user.set_password('825662')
        user.save()
        print("Superuser 'akijgroup' password updated successfully!")