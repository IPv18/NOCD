from django.shortcuts import render

def DashboardPage(request):
    return render(request, 'dashboard.html')
    