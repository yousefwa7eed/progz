from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Communication


@login_required
def communication_list(request):
    comms = Communication.objects.all().order_by('-sent_at')
    return render(request, 'communications/list.html', {'communications': comms})
