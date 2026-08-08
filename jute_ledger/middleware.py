import os
from django.contrib.gis.geoip2 import GeoIP2
from bills.models import VisitorLog

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ১. প্রক্সি ভেদ করে আসল ফোন বা পিসির আইপি বের করার নিয়ম
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        
        if x_forwarded_for:
            # অনেক সময় একাধিক আইপি থাকে, তাই প্রথমটি (আসল ইউজারের আইপি) নেওয়া হলো
            ip = x_forwarded_for.split(',')[0].strip()
        elif x_real_ip:
            ip = x_real_ip.strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '').strip()

        # লোকালহোস্টে টেস্ট করার জন্য ডামি আইপি
        if ip in ['127.0.0.1', '::1']:
            ip = '103.102.27.0' 

        # ২. রেন্ডারের হেলথ চেক বা ক্লাউড বট ইগনোর করা (যাতে শুধু আসল ইউজার সেভ হয়)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'Render' in user_agent or 'HealthCheck' in user_agent or ip.startswith('35.'):
            return self.get_response(request)

        country_name, region_name, city_name = "Bangladesh", "Dhaka", "Dhaka"

        # ৩. আসল আইপি অনুযায়ী লোকেশন বের করা
        try:
            g = GeoIP2()
            location_data = g.city(ip)
            if location_data:
                country_name = location_data.get('country_name') or "Bangladesh"
                region_name = location_data.get('region_name') or "Dhaka"
                city_name = location_data.get('city') or "Dhaka"
        except Exception:
            pass

        # ডাটাবেজে সেভ করা
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