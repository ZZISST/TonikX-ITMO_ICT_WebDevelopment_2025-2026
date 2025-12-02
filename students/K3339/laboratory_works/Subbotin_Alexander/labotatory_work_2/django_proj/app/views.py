from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count


from .models import Tour, Reservation
from .forms import ReservationForm, ReviewForm, RegisterForm


def register(request):
    # redirect already authenticated users
    if request.user.is_authenticated:
        return redirect('tour_list')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tour_list")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

class TourListView(ListView):
    model = Tour
    template_name = 'tour_list.html'
    context_object_name = 'tours'
    paginate_by = 8
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                models.Q(title__icontains=q) |
                models.Q(agency__icontains=q) |
                models.Q(country__icontains=q) |
                models.Q(description__icontains=q)
            )
        return qs.order_by('start_date')
    

class MyReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'my_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)



class TourDetailView(DetailView):
    model = Tour
    template_name = 'tour_detail.html'


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['review_form'] = ReviewForm()
        ctx['reservations_count'] = self.object.reservations.filter(confirmed=True).count()
        return ctx


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservation_form.html'


    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, pk=kwargs.get('tour_id'))
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.tour = self.tour
        form.instance.confirmed = False # admin will confirm
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('user_reservations')


class UserReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10


    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).select_related('tour').order_by('-created_at')


class ReservationOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        reservation = self.get_object()
        return reservation.user == self.request.user


class ReservationUpdateView(LoginRequiredMixin, ReservationOwnerMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservation_form.html'


    def get_success_url(self):
        return reverse('user_reservations')


class ReservationDeleteView(LoginRequiredMixin, ReservationOwnerMixin, DeleteView):
    model = Reservation
    template_name = 'reservation_confirm_delete.html'
    success_url = reverse_lazy('user_reservations')

    @login_required
    def add_review(request, pk):
        tour = get_object_or_404(Tour, pk=pk)
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.tour = tour
                review.save()
        return redirect('tour_detail', pk=pk)

class SoldByCountryView(LoginRequiredMixin, TemplateView):
    template_name = 'sold_by_country.html'

    @login_required
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        qs = Tour.objects.filter(reservations__confirmed=True).values('country').annotate(
            tours_sold=Count('reservations'),
            total_income=models.Sum(models.F('reservations__guests') * models.F('price'), output_field=models.DecimalField(max_digits=12, decimal_places=2))
        ).order_by('-tours_sold')

        ctx['data'] = qs
        return ctx  
    

class TourCreateView(UserPassesTestMixin, CreateView):
    model = Tour
    fields = ['title', 'agency', 'country', 'description', 'start_date', 'end_date', 'price', 'payment_terms']
    template_name = 'tour_form.html'
    success_url = reverse_lazy('tour_list')

    def test_func(self):
        return self.request.user.is_staff