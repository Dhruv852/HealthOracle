"""
URL configuration for HealthOracle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from . import views, chatbot_views
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('heart/', views.heart_prediction, name='heart'),
    path('lung/', views.lung_prediction, name='lung'),
    path('diabetes/', views.diabetes_prediction, name='diabetes'),
    path('liver/', views.liver_prediction, name='liver'),
    
    # Authentication URLs
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('history/', user_views.patient_history, name='history'),
    path('prediction/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),
    path('chatbot/', chatbot_views.chatbot_view, name='chatbot'),
    path('chatbot/query/', chatbot_views.handle_chatbot_query, {'prediction_id': None}, name='chatbot_query_general'),
    path('chatbot/<int:prediction_id>/', chatbot_views.chatbot_view, name='chatbot_prediction'),
    path('chatbot/<int:prediction_id>/query/', chatbot_views.handle_chatbot_query, name='chatbot_query_prediction'),
    path('chatbot/<int:prediction_id>/suggestions/', chatbot_views.get_suggestions, name='get_suggestions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
