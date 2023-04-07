from django.shortcuts import render, redirect
from firewall.models import FirewallRule
from .forms import FirewallRuleForm
import subprocess

# django ALL=(ALL) NOPASSWD:/sbin/iptables need to be added to the /etc/sudoers file 

#def iptables_command(command):
#    full_command = f'sudo /sbin/iptables {command}'
#    subprocess.run(full_command.split(), check=True)

def index(request):
    if request.method == 'GET':
        context = {
            "tables": [
                FirewallRule.objects.filter(IP_family='IPv4', traffic_direction='Inbound').order_by('rule_num'),
                FirewallRule.objects.filter(IP_family='IPv4', traffic_direction='Outbound').order_by('rule_num'),
                FirewallRule.objects.filter(IP_family='IPv6', traffic_direction='Inbound').order_by('rule_num'),
                FirewallRule.objects.filter(IP_family='IPv6', traffic_direction='Outbound').order_by('rule_num'),
            ]
        }
        return render(request, 'firewall/firewall.html', context)
    elif request.method == 'POST':
        pass 
        # TODO add iptables control here

def AddRule(request):
    form = FirewallRuleForm()
    UpdateOrSubmit = 'SUBMIT'
    #if 'ip_family' in request.GET and 'traffic_direction' in request.GET:
    ip_family = request.GET.get('ip_family')
    traffic_direction = request.GET.get('traffic_direction')
    print(ip_family)
    print(traffic_direction)
    context = {'form':form, 'UpdateOrSubmit':UpdateOrSubmit, 'ip_family':ip_family , 'traffic_direction':traffic_direction}
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

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
            return redirect('home')

    context = {'form':form, 'UpdateOrSubmit':UpdateOrSubmit, 'instance':rule, 'ip_family':ip_family , 'traffic_direction':traffic_direction}
    return render(request, 'firewall/addrule.html', context)

def RemoveRule(request, pk):
    rule = FirewallRule.objects.get(ID=pk)
    if request.method == "POST":
        rule.delete()
        return redirect('home')
    context = {'rule':rule}
    return render(request, 'firewall/removerule.html', context)
