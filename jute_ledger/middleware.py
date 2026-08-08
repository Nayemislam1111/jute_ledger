from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError
from bills.models import VisitorLog
import os

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # লোকালহোস্টে টেস্ট করার জন্য ডামি আইপি
        if ip in ['127.0.0.1', '::1']:
            ip = '103.102.27.0' 

        country_name, region_name, city_name = "Bangladesh", "Dhaka", "Dhaka"

        # সার্ভারে GeoIP ডাটাবেজ ফাইল বা লাইব্রেরি না থাকলে যাতে ক্র্যাশ না করে
        try:
            g = GeoIP2()
            location_data = g.city(ip)
            if location_data:
                country_name = location_data.get('country_name') or "Bangladesh"
                region_name = location_data.get('region_name') or "Dhaka"
                city_name = location_data.get('city') or "Dhaka"
        except Exception:
            # রেন্ডার বা প্রোডাকশনে GeoIP সেটআপ না থাকলেও সাইট সচল থাকবে
            pass

        # ডাটাবেজে সেভ করার সময় যেন কোনো কারণে এরর না দেয়
        try:
            VisitorLog.objects.create(
                ip_address=ip,
                country=country_name,
                region=region_name,
                city=city_name
            )
        except Exception:
            pass

        response = self.get_response(request)
        return response