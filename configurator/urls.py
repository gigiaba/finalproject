from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('build/', views.index_view, name='index'),
    path('toggle/<int:comp_id>/', views.toggle_component, name='toggle_component'),
    path('save/', views.save_build, name='save_build'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
