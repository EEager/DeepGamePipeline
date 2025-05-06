from django.urls import path
from . import views

urlpatterns = [
    path('player_summary/', views.player_summary, name='player_summary'),
]
