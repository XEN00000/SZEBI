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
from core.views import LoginView

# ---- alarms router + mock endpoint (from alarms branch) ----
from rest_framework import routers
from alarms.views import AlertViewSet, AlertRuleViewSet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

router = routers.DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'alert-rules', AlertRuleViewSet, basename='alert-rule')

@csrf_exempt
def emergency_mode(request):
    try:
        if request.method == 'POST':
            alert_data = json.loads(request.body or '{}')
        else:
            alert_data = request.GET.dict()

        print(
            "CRITICAL ALERT",
            f"ID={alert_data.get('id')}",
            f"Priority={alert_data.get('priority')}",
            f"Rule={alert_data.get('rule_name')}",
            f"Metric={alert_data.get('rule_metric')}"
        )
        return JsonResponse({'status': 'received'})
    except Exception as e:
        print(f"ERROR parsing alert: {e}")
        return JsonResponse({'error': str(e)}, status=400)

# ---- urlpatterns merged from alarms + optimization + analysis ----
urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/login/', LoginView.as_view(), name='login'),

    # optimization API
    path('api/optimization/', include('optimization.api.urls')),

    # alarms API
    path('api/', include(router.urls)),
    path('api/optimalization/alarm/', emergency_mode),

    # analysis module
    path("analysis/", include("analysis.urls")),
]