from django.urls import path
import scuba.accounts.views.collections as collections_view


urlpatterns = [
    path('', collections_view.IndexView.as_view(), name='collections_index'),
]
