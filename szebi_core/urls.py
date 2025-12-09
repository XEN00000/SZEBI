"""
URL configuration for szebi_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from alarms.views import AlertViewSet, AlertRuleViewSet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

router = routers.DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'alert-rules', AlertRuleViewSet, basename='alert-rule')

# mock endpointu emergency_mode
@csrf_exempt
def emergency_mode(request):
    if request.method == 'POST':
        try:
            alert_data = json.loads(request.body)
            print(f"CRITICAL ALERT ID={alert_data.get('id')}, Priority={alert_data.get('priority')}, Rule={alert_data.get('rule_name')}")
            return JsonResponse({'status': 'received'})
        except Exception as e:
            print(f"ERROR parsing alert: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST only'}, status=400)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # na potrzeby testow, mock endpointu na ktory wysylamy alert krytyczny
    path('emergency-mode', emergency_mode),
]
