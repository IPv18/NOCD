from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from firewall.models import FirewallRule
from .forms import FirewallRuleForm
import subprocess, ipaddress, socket

def get_id(ip_family, traffic_direction):
    if ip_family == 'IPv4' and traffic_direction == 'Inbound':
        return '1'
    elif ip_family == 'IPv4' and traffic_direction == 'Outbound':
        return '2'
    elif ip_family == 'IPv6' and traffic_direction == 'Inbound':
        return '3'
    elif ip_family == 'IPv6' and traffic_direction == 'Outbound':
        return '4'

def check_address(address):
    if address == '':
        return address

    if address.startswith('127'):
        return '127.0.0.0/8'
    
    try:
        ip = ipaddress.ip_interface(address)
        if '/' in address:
            return ip.network
        else:
            return address
    except ValueError:
        return ''

def update_ip_tables(ip_family, traffic_direction):
    iptables_family = 'iptables' if ip_family == 'IPv4' else 'ip6tables'
    iptables_direction = 'INPUT' if traffic_direction == 'Inbound' else 'OUTPUT'
    cmd = f'sudo {iptables_family} --flush {iptables_direction}'
    subprocess.run(cmd.split(), check=True)
    table = FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction).order_by('rule_priority')
    rule_dicts = [rule.to_dict() for rule in table]
    for rule in rule_dicts:
        if rule['rule_priority'] == 1000:
            cmd = f'sudo {iptables_family} -P {iptables_direction} {rule["action"]}'
            subprocess.run(cmd.split(), check=True)
        else:
            cmd = f'sudo {iptables_family} -t filter -A {iptables_direction}'
            if 'source_address' in rule and rule['source_address'] is not None:
                cmd += f' -s {rule["source_address"]}'
            if 'destination_address' in rule and rule['destination_address'] is not None:
                cmd += f' -d {rule["destination_address"]}'
            if 'protocol' in rule and rule['protocol'] is not None:
                cmd += f' -p {rule["protocol"]}'
            if 'source_port' in rule and rule['source_port'] is not None:
                cmd += f' --sport {rule["source_port"]}'
            if 'destination_port' in rule and rule['destination_port'] is not None:
                cmd += f' --dport {rule["destination_port"]}'
            cmd  += f' -j {rule["action"]}'
            if rule['action'] == 'LOG':
                log_prefix = rule["description"][:29].replace(" ", "_")
                cmd += f' --log-prefix {log_prefix}'
            subprocess.run(cmd.split(), check=True)
  
def home(request):
    if request.method == 'GET':
        if 'id' in request.GET:
            id_value = request.GET.get('id')
            if id_value == '':
                id_value = 1
        else:
            id_value = 1

        context = {
            "tables": [
                FirewallRule.objects.filter(ip_family='IPv4', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(ip_family='IPv4', traffic_direction='Outbound').order_by('rule_priority'),
                FirewallRule.objects.filter(ip_family='IPv6', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(ip_family='IPv6', traffic_direction='Outbound').order_by('rule_priority'),
            ],
            "id": id_value
        }
        return render(request, 'firewall/firewall.html', context)
  
def check_rule_uniqueness(request):
    if request.method == 'GET':
        rule_priority = request.GET.get('rule_priority')
        traffic_direction = request.GET.get('traffic_direction')
        ip_family = request.GET.get('ip_family')
        try:
            FirewallRule.objects.get(
                rule_priority=rule_priority, traffic_direction=traffic_direction, ip_family=ip_family)
            exists = True
        except FirewallRule.DoesNotExist:
            exists = False
        return JsonResponse({'exists': exists})
    
def check_domain_validity(request):
    if request.method == 'GET':
        ip_family = request.GET.get('ip_family')
        domain = request.GET.get('domain')
        socket_ip_family = socket.AF_INET if ip_family == 'IPv4' else socket.AF_INET6
        try:
            ip_address = socket.getaddrinfo(domain, None, family=socket_ip_family)[0][4][0]
        except:
            ip_address = None
        return JsonResponse({'response':ip_address})

def rule(request):
    if request.method  == 'GET':
        form = FirewallRuleForm()
        update_or_submit = 'SUBMIT'
        ip_family = request.GET.get('ip_family')
        traffic_direction = request.GET.get('traffic_direction')
        context = {'form':form, 'update_or_submit':update_or_submit, 
                    'ip_family':ip_family , 'traffic_direction':traffic_direction}
        return render(request, 'firewall/addrule.html', context)
    
    elif request.method == 'POST':
        form = FirewallRuleForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data 
            ip_family = cleaned_data['ip_family']
            traffic_direction = cleaned_data['traffic_direction']
            rule_priority = cleaned_data['rule_priority']
            src_adr = dst_adr = ''
            if cleaned_data.get('source_address'):
                src_adr = check_address(cleaned_data['source_address'])
            if cleaned_data.get('destination_address'):
                dst_adr = check_address(cleaned_data['destination_address'])
            form.save()
            if src_adr != '':
                FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority).update(
                source_address = src_adr)
            if dst_adr != '':
                FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority).update(
                destination_address = dst_adr)
            update_ip_tables(ip_family, traffic_direction)
            message = 'Rule has been added successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            return redirect(reverse('firewall:home') + f'?id={int(get_id(ip_family, traffic_direction))}')

def rule_handler(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    if request.method == 'GET':
        rule = FirewallRule.objects.get(id=pk)
        ip_family = rule.ip_family
        traffic_direction = rule.traffic_direction
        form = FirewallRuleForm(instance=rule)
        update_or_submit = 'UPDATE'
        context = {'form':form, 'update_or_submit':update_or_submit, 'instance':rule, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
        return render(request, 'firewall/addrule.html', context)
  
    elif request.method == 'POST':
        form = FirewallRuleForm(request.POST, instance=rule)
        if form.is_valid():
            cleaned_data = form.cleaned_data 
            ip_family = cleaned_data['ip_family']
            traffic_direction = cleaned_data['traffic_direction']
            rule_priority = cleaned_data['rule_priority']
            src_adr = dst_adr = ''
            if cleaned_data.get('source_address'):
                src_adr = check_address(cleaned_data['source_address'])
            if cleaned_data.get('destination_address'):
                dst_adr = check_address(cleaned_data['destination_address'])
            form.save()
            if src_adr != '':
                FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority).update(
                source_address = src_adr)
            if dst_adr != '':
                FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority).update(
                destination_address = dst_adr)
            update_ip_tables(ip_family, traffic_direction)
            message = 'Rule has been modified successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            return redirect(reverse('firewall:home') + f'?id={int(get_id(ip_family, traffic_direction))}')
    
    elif request.method == 'PATCH':
        ip_family = rule.ip_family
        traffic_direction = rule.traffic_direction
        last_rule = FirewallRule.objects.get(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=1000)
        try: 
            if last_rule.action == 'ACCEPT':
                if ip_family == 'IPv4':
                    if not FirewallRule.objects.filter(ip_family='IPv4', traffic_direction='Inbound', destination_address='127.0.0.0/8', action='ACCEPT').exists() or not FirewallRule.objects.filter(ip_family='IPv4', traffic_direction='Outbound', source_address='127.0.0.0/8', action='ACCEPT').exists():
                        message = 'Error has occured, cannot change table policy until there are Inbound/Outbound rules allowing traffic from and to 127.0.0.0/8.'
                        messages.warning(request, message, extra_tags='warning')
                        request.session['alert-message'] = message
                        return JsonResponse({'success': False, 'id':int(get_id(last_rule.ip_family, last_rule.traffic_direction))}, status=400)
                last_rule.action = 'DROP'
            else:
                last_rule.action = 'ACCEPT'
            last_rule.save()
            message = 'Table policy has been changed successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            update_ip_tables(ip_family, traffic_direction)
            return JsonResponse({'success': True, 'id':int(get_id(last_rule.ip_family, last_rule.traffic_direction))}, status=200)
        except:
            message = 'Error has occured during the proccess of changing the table policy!'
            messages.error(request, message, extra_tags='danger')
            request.session['alert-message'] = message
            return JsonResponse({'success': False})
        
    elif request.method == 'DELETE':
        ip_family = rule.ip_family
        traffic_direction = rule.traffic_direction
        rule.delete()
        update_ip_tables(ip_family, traffic_direction)
        message = 'Rule has been removed successfully!'
        messages.success(request, message)
        request.session['alert-message'] = message
        return JsonResponse({'success': True, 'id':int(get_id(ip_family, traffic_direction))}, status=200)
