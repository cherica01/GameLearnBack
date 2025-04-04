from django.urls import path
from .views import BoiSimPointsView, HistoricalDialoguesPointsView

urlpatterns = [
    path('boi-sim-points/', BoiSimPointsView.as_view(), name='boi_sim_points'),
    path('historical-dialogues-points/', HistoricalDialoguesPointsView.as_view(), name='historical_dialogues_points'),
]