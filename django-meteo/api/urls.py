from django.urls import path
from .views import (
    list_stations, status, last_report, history, maxima_history, 
    last_update, receive_weather_data, receive_minmax_data, receive_status_data
)

urlpatterns = [
    path('stations/', list_stations, name="list_stations"),  # ✅ Android app only
    path('status/<str:station_id>/', status, name="status"),  # ✅ Matches /api/status/<id>/
    path('lastreport/<str:station_id>/', last_report, name="last_report"),  # ✅ Matches /api/lastreport/<id>/
    path('history/<str:station_id>/', history, name="history"),  # ✅ Matches /api/history/<id>/
    path('minmax/history/<str:station_id>/', maxima_history, name="maxima_history"),  # 🔄 FIXED path
    path('lastupdate/<str:station_id>/', last_update, name="last_update"),  # ✅ Matches /api/lastupdate/<id>/
    path('weather/upload/', receive_weather_data, name="receive_weather_data"),  # ✅ Matches /api/weather/upload/
    path('minmax/upload/', receive_minmax_data, name="receive_minmax_data"),  # ✅ Matches /api/minmax/upload/
    path('status/upload/', receive_status_data, name="receive_status_data"),  # ✅ ADDED /api/status/upload/
]
