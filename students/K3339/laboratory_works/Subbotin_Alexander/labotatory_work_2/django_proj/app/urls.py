from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.TourListView.as_view(), name='tour_list'),
    path('tour/<int:pk>/', views.TourDetailView.as_view(), name='tour_detail'),
    
    # autorithation
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),


    path('tour/add/', views.TourCreateView.as_view(), name='tour_create'),

    # Reservation CRUD for logged-in users
    path('reservation/add/<int:tour_id>/', views.ReservationCreateView.as_view(), name='reservation_add'),
    path('reservation/', views.UserReservationListView.as_view(), name='user_reservations'),
    path('reservation/<int:pk>/edit/', views.ReservationUpdateView.as_view(), name='reservation_edit'),
    path('reservation/<int:pk>/delete/', views.ReservationDeleteView.as_view(), name='reservation_delete'),


    # Reviews
    path('tour/<int:pk>/review/', views.ReservationDeleteView.add_review, name='add_review'),


    # Sold tours by country
    path('sold-by-country/', views.SoldByCountryView.as_view(), name='sold_by_country'),

    path('my-reservations/', views.MyReservationsView.as_view(), name='my_reservations'),
]