from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('', RedirectView.as_view(url='admin/'), name='redirect-to-admin'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.accounts.api.urls')),
    path('api/v1/', include('apps.member.urls')),
    path('api/v1/', include('apps.jurisdiction.urls')),
    path('api/v1/', include('apps.shared.urls')),
]
