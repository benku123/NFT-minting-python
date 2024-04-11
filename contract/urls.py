from django.urls import path, include
from . import views

app_name = 'contract'
urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),  # Adds paths for the auth system
    path('signup/', views.signup_view, name='signup'),
    path('api/save_account/', views.save_account, name='save_account'),
]
