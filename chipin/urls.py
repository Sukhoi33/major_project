from django.urls import path
from . import views

app_name = 'chipin'

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path('sensitive/', views.sensitive_area, name='sensitive'),
    path('aircraft-profiles/', views.aircraft_profiles, name='aircraft_profiles'),
    path('aircraft-profiles/add/', views.add_aircraft, name='add_aircraft'),
    path('aircraft-profiles/<int:pk>/edit/', views.edit_aircraft, name='edit_aircraft'),
    path('aircraft-profiles/<int:pk>/delete/', views.delete_aircraft, name='delete_aircraft'),
    path('new-flight/', views.new_flight, name='new_flight'),
    path('flight-log/', views.flight_log, name='flight_log'),
]
