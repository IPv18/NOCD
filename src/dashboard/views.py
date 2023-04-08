from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def DashboardPage(request):
    return render(request, 'dashboard/dashboard.html')
