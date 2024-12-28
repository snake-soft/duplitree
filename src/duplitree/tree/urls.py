from django.urls import path

from .views import TreeDetailView, TreeListView, TreePathView, FileDeleteView, FileDetailView

app_name = 'tree'


urlpatterns = [
    path('tree/', TreeListView.as_view(), name='list'),
    path('tree/<int:pk>/', TreeDetailView.as_view(), name='detail'),
    path('tree/<int:pk>/<path:path>/', TreePathView.as_view(), name='directory'),
    path('file/<int:pk>/', FileDetailView.as_view(), name='file'),
    path('file/<int:pk>/delete/', FileDeleteView.as_view(), name='file-delete'),
]
