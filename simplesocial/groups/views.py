# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views import generic
from . import models
from groups.models import Group, GroupMember
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from django.contrib import messages # to show error messages
# Create your views here.


class CreateGroup(LoginRequiredMixin, generic.CreateView):
    fields = ('name', 'description')
    model = Group
    # returns LOWER CASED name of MODEL as CONTEXT DICTIONARY


class SingleGroup(generic.DetailView):
    model = Group


class ListGroup(generic.ListView):
    model = Group


class JoinGroup(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug':self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, self.kwargs.get('slug'))

        try:
            GroupMember.objects.create(user=self.request.user, group=group)
        except IntegrityError:
            messages.warning(self.request, ('Warning already a Member.'))
        else:
            messages.success(self.request, 'you are now a Member.')
        return super().get(request, *args, **kwargs)


class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug':self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):

        try:
            membership = models.GroupMember.objects.filter(
                user=self.request.user,
                group__slug=self.kwargs.filter("slug")
            ).get()
        except models.GroupMember.DoesNotExist:
            messages.warning(self.request, ('Sorry, you are not in this Group.'))
        else:
            membership.delete()
            messages.success(self.request, 'you have left the Group.')
        return super().get(request, *args, **kwargs)
