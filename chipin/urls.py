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

    # Documents (checklists / maintenance / manuals)
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/', views.document_list, name='document_list'),
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/add/', views.add_document, name='add_document'),
    path('aircraft-profiles/<int:pk>/docs/<str:doc_type>/<int:doc_pk>/delete/', views.delete_document, name='delete_document'),

    path('new-flight/', views.new_flight, name='new_flight'),
    path('flight-log/', views.flight_log, name='flight_log'),
]
