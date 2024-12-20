from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from .forms import SignUpForm, ProfileForm


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("welcome")
    template_name = "registration/signup.html"


class ProfileView(UpdateView):
    form_class = ProfileForm
    template_name="registration/profile.html"
    success_url = reverse_lazy('profile')

    def get_object(self, queryset = ...):
        return self.request.user
    
    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        messages.success(request, "Updated Profile Successfully!")
        return result
