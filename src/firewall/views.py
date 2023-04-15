from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from firewall.models import FirewallRule
from .forms import FirewallRuleForm
import subprocess

# django ALL=(ALL) NOPASSWD:/sbin/iptables need to be added to the /etc/sudoers file 
# def iptables_command(command):
#    full_command = f'sudo /sbin/iptables {command}'
#    subprocess.run(full_command.split(), check=True)


def index(request):
    if request.method == 'GET':
        if 'ip_family' in request.GET and 'traffic_direction' in request.GET and 'new_action_index' in request.GET:
            new_action = ['DROP', 'ACCEPT']
            ip_family = request.GET['ip_family']
            traffic_direction = request.GET['traffic_direction']
            new_action_index = request.GET['new_action_index']
            FirewallRule.objects.filter(IP_family=ip_family, traffic_direction=traffic_direction, rule_num=1000).update(
                action=new_action[int(new_action_index)])

        context = {
            "tables": [
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Inbound').order_by('rule_num'),
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Outbound').order_by('rule_num'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Inbound').order_by('rule_num'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Outbound').order_by('rule_num'),
            ]
        }

        if 'success_message' in request.GET:
            success_message = request.GET['success_message']
            messages.success(request, success_message)
        return render(request, 'firewall/firewall.html', context)
    elif request.method == 'POST':
        pass # TODO add iptables control here

def check_rule_uniqueness(request):
    rule_num = request.GET.get('rule_num')
    traffic_direction = request.GET.get('traffic_direction')
    IP_family = request.GET.get('IP_family')
    try:
        FirewallRule.objects.get(
            rule_num=rule_num, traffic_direction=traffic_direction, IP_family=IP_family)
        exists = True
    except FirewallRule.DoesNotExist:
        exists = False
    return JsonResponse({'exists': exists})

def AddRule(request):
    form = FirewallRuleForm()
    UpdateOrSubmit = 'SUBMIT'
    ip_family = request.GET.get('ip_family')
    traffic_direction = request.GET.get('traffic_direction')
    context = {'form':form, 'UpdateOrSubmit':UpdateOrSubmit, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST)
        if form.is_valid():
            form.save()
            success_message = "Rule added successfully!"
            return redirect(reverse('home') + "?success_message=" + success_message)

    return render(request, 'firewall/addrule.html', context)


def UpdateRule(request, pk):
    rule = FirewallRule.objects.get(ID=pk)
    ip_family = rule.IP_family
    traffic_direction = rule.traffic_direction
    form = FirewallRuleForm(instance=rule)
    UpdateOrSubmit = 'UPDATE'
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            success_message = "Rule updated successfully!"
            return redirect(reverse('home') + "?success_message=" + success_message)

    context = {'form':form, 'UpdateOrSubmit':UpdateOrSubmit, 'instance':rule, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
    return render(request, 'firewall/addrule.html', context)

def RemoveRule(request, pk):
    rule = FirewallRule.objects.get(ID=pk)
    rule.delete()
    success_message = "Rule removed successfully!"
    return redirect(reverse('home') + "?success_message=" + success_message)
