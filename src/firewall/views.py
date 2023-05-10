from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.core import serializers
from firewall.models import FirewallRule
from .forms import FirewallRuleForm
import subprocess, ipaddress, json

# django ALL=(ALL) NOPASSWD:/sbin/iptables need to be added to the /etc/sudoers file 
# def iptables_command(command):
#    full_command = f'sudo /sbin/iptables {command}'
#    subprocess.run(full_command.split(), check=True)

def check_address(address):
    if address == '':
        return address
    
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
    table = FirewallRule.objects.filter(
                    ip_family=ip_family, traffic_direction=traffic_direction).order_by('rule_priority')
    cmd = f'sudo {iptables_family} --flush {iptables_direction}'
    subprocess.run(cmd.split(), check=True)
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
                cmd  += f' -j {rule["action"]} --log-prefix \"{rule["description"]}\"'
            subprocess.run(cmd.split(), check=True)
            
"""
def index(request):
    if request.method == 'GET':
        if 'ip_family' in request.GET and 'traffic_direction' in request.GET and 'new_action_index' in request.GET:
            new_action = ['DROP', 'ACCEPT']
            ip_family = request.GET['ip_family']
            traffic_direction = request.GET['traffic_direction']
            new_action_index = request.GET['new_action_index']
            FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=1000).update(
                action=new_action[int(new_action_index)])
            message = 'Table policy changed successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            #update_ip_tables(ip_family, traffic_direction)
            return redirect('home')
            

        context = {
            "tables": [
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Outbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Outbound').order_by('rule_priority'),
            ]
        }

        return render(request, 'firewall/firewall.html', context)
    elif request.method == 'POST':
        pass # TODO add iptables control here
    
def check_rule_uniqueness(request):
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

def add_rule(request):
    form = FirewallRuleForm()
    update_or_submit = 'SUBMIT'
    ip_family = request.GET.get('ip_family')
    traffic_direction = request.GET.get('traffic_direction')
    context = {'form':form, 'update_or_submit':update_or_submit, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
    if request.method == 'POST':
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
            #update_ip_tables(ip_family, traffic_direction)
            message = 'Rule added successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            return redirect('home')

    return render(request, 'firewall/addrule.html', context)


def update_rule(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    ip_family = rule.ip_family
    traffic_direction = rule.traffic_direction
    form = FirewallRuleForm(instance=rule)
    update_or_submit = 'UPDATE'
    if request.method == 'POST':
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
            #update_ip_tables(ip_family, traffic_direction)
            message = 'Rule modified successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            return redirect('home')

    context = {'form':form, 'update_or_submit':update_or_submit, 'instance':rule, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
    return render(request, 'firewall/addrule.html', context)

def remove_rule(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    ip_family = rule.ip_family
    traffic_direction = rule.traffic_direction
    #update_ip_tables(ip_family, traffic_direction)
    rule.delete()
    message = 'Rule deleted successfully!'
    messages.success(request, message)
    request.session['alert-message'] = message
    return redirect('home')
"""













def index_RESTful(request):
    if request.method == 'GET':
        context = {
            "tables": [
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv4', traffic_direction='Outbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Inbound').order_by('rule_priority'),
                FirewallRule.objects.filter(
                    ip_family='IPv6', traffic_direction='Outbound').order_by('rule_priority'),
            ]
        }
        return render(request, 'firewall/firewall.html', context)
    elif request.method == 'POST':
        form = FirewallRuleForm(request.POST)
        print(request.POST)
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

            # Check if the rule already exists in the database
            rule_exists = FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority).exists()

            # If the rule already exists, update its fields with the submitted data
            if rule_exists:
                firewall_rule = FirewallRule.objects.get(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=rule_priority)
                for field in form.fields:
                    if field in ['source_address', 'destination_address']:
                        continue  # We handle these fields separately
                    setattr(firewall_rule, field, cleaned_data[field])
                if src_adr != '':
                    firewall_rule.source_address = src_adr
                if dst_adr != '':
                    firewall_rule.destination_address = dst_adr
                firewall_rule.save()
                message = 'Rule updated successfully!'
            else:
                # If the rule does not already exist, create a new FirewallRule instance and save it to the database
                firewall_rule = form.save(commit=False)
                firewall_rule.source_address = src_adr
                firewall_rule.destination_address = dst_adr
                firewall_rule.save()
                message = 'Rule added successfully!'

            #update_ip_tables(ip_family, traffic_direction)
            messages.success(request, message)
            request.session['alert-message'] = message
            return JsonResponse({'success': True}, status=200)
        else:
            print(form.errors)
            return JsonResponse({'success': False})

def check_rule_uniqueness(request):
    rule_priority = request.GET.get('rule_priority')
    traffic_direction = request.GET.get('traffic_direction')
    ip_family = request.GET.get('ip_family')
    try:
        FirewallRule.objects.get(
            rule_priority=rule_priority, traffic_direction=traffic_direction, ip_family=ip_family)
        exists = True
    except FirewallRule.DoesNotExist:
        exists = False
    return JsonResponse({'exists': exists}, status=200)

def rule_handler_RESTFUL(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    if request.method == 'GET':
        return JsonResponse({'instance': rule.to_dict()})
    
    elif request.method == 'PATCH':
        ip_family = rule.ip_family
        traffic_direction = rule.traffic_direction
        last_rule = FirewallRule.objects.get(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=1000)
        try: 
            if last_rule.action == 'ACCEPT':
                last_rule.action = 'DROP'
            else:
                last_rule.action = 'ACCEPT'
            last_rule.save()
            message = 'Table policy changed successfully!'
            messages.success(request, message)
            request.session['alert-message'] = message
            #update_ip_tables(ip_family, traffic_direction)
            return JsonResponse({'success': True}, status=200)
        except:
            message = 'Error has occured during the proccess of changing the table policy!'
            messages.error(request, message, extra_tags='danger')
            request.session['alert-message'] = message
            return JsonResponse({'success': False})
        
    elif request.method == 'DELETE':
        ip_family = rule.ip_family
        traffic_direction = rule.traffic_direction
        #update_ip_tables(ip_family, traffic_direction)
        try:
            rule.delete()
        except:
            return JsonResponse({'success': False})
        message = 'Rule deleted successfully!'
        messages.success(request, message)
        request.session['alert-message'] = message
        return JsonResponse({'status': 'success'}, status=200)

    # Return an error message for unsupported request methods
    return JsonResponse({'status': 'error', 'message': 'Unsupported request method.'})
