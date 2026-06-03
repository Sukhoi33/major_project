from django.urls import path
from . import views

app_name = 'chipin'

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path('sensitive/', views.sensitive_area, name='sensitive'),

    # Aircraft CRUD
    path('aircraft-profiles/', views.aircraft_profiles, name='aircraft_profiles'),
    path('aircraft-profiles/add/', views.add_aircraft, name='add_aircraft'),
    path('aircraft-profiles/<int:pk>/', views.view_aircraft, name='view_aircraft'),
    path('aircraft-profiles/<int:pk>/edit/', views.edit_aircraft, name='edit_aircraft'),
    path('aircraft-profiles/<int:pk>/delete/', views.delete_aircraft, name='delete_aircraft'),

    # Documents
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/', views.document_list, name='document_list'),
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/add/', views.add_document, name='add_document'),
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/<int:doc_pk>/delete/', views.delete_document, name='delete_document'),

    # Flight logger
    path('new-flight/', views.new_flight, name='new_flight'),
    path('flight/<int:pk>/current/', views.current_flight, name='current_flight'),
    path('flight/<int:pk>/post-landing/', views.post_landing, name='post_landing'),
    path('flight/<int:pk>/summary/', views.flight_summary, name='flight_summary'),
    path('flight-log/', views.flight_log, name='flight_log'),
]
