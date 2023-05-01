from django.shortcuts import render, redirect
from django.contrib import messages
import json
from django.http import JsonResponse
from django.urls import reverse
from django.core import serializers
from firewall.models import FirewallRule
from .forms import FirewallRuleForm
import subprocess

# django ALL=(ALL) NOPASSWD:/sbin/iptables need to be added to the /etc/sudoers file 
# def iptables_command(command):
#    full_command = f'sudo /sbin/iptables {command}'
#    subprocess.run(full_command.split(), check=True)

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
            
    
def index(request):
    if request.method == 'GET':
        if 'ip_family' in request.GET and 'traffic_direction' in request.GET and 'new_action_index' in request.GET:
            new_action = ['DROP', 'ACCEPT']
            ip_family = request.GET['ip_family']
            traffic_direction = request.GET['traffic_direction']
            new_action_index = request.GET['new_action_index']
            FirewallRule.objects.filter(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=1000).update(
                action=new_action[int(new_action_index)])
            update_ip_tables(ip_family, traffic_direction)

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

        if 'success_message' in request.GET:
            success_message = request.GET['success_message']
            messages.success(request, success_message)
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
            form.save()
            success_message = "Rule added successfully!"
            update_ip_tables(ip_family, traffic_direction)
            return redirect(reverse('home') + "?success_message=" + success_message)

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
            form.save()
            success_message = "Rule updated successfully!"
            update_ip_tables(ip_family, traffic_direction)
            return redirect(reverse('home') + "?success_message=" + success_message)

    context = {'form':form, 'update_or_submit':update_or_submit, 'instance':rule, 
                'ip_family':ip_family , 'traffic_direction':traffic_direction}
    return render(request, 'firewall/addrule.html', context)

def remove_rule(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    rule.delete()
    success_message = "Rule removed successfully!"
    update_ip_tables(ip_family, traffic_direction)
    return redirect(reverse('home') + "?success_message=" + success_message)

"""
def index_RESTful(request):
    if request.method == 'GET':
        return render(request, 'firewall/firewall.html')
    
def rule_RESTful(request):
    if request.method == 'GET':
        # check rule uniqueness
        if 'ip_family' in request.GET and 'traffic_direction' in request.GET and 'rule_priority' in request.GET:
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
        # asks for rule form
        elif 'ip_family' in request.GET and 'traffic_direction' in request.GET:
            form = FirewallRuleForm()
            ip_family = request.GET['ip_family']
            traffic_direction = request.GET['traffic_direction']
            context = {'form':form, 'ip_family':ip_family, 'traffic_direction':traffic_direction}
            return JsonResponse(context)
        # asks for tables content
        else:
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
            serialized_tables = []
            for table in context['tables']:
                serialized_table = serializers.serialize('json', table)
                serialized_tables.append(serialized_table)
            return JsonResponse(serialized_tables, safe=False)

    # flips the action of last rule of each table between DROP and ACCEPT
    elif request.method == 'PATCH':
        ip_family = request.GET['ip_family']
        traffic_direction = request.GET['traffic_direction']
        rule = FirewallRule.objects.get(ip_family=ip_family, traffic_direction=traffic_direction, rule_priority=1000)
        if rule.action == 'ACCEPT':
            rule.action = 'DROP'
        else:
            rule.action = 'ACCEPT'
        rule.save()
        return JsonResponse({'success': True, 'message': 'Rule action updated successfully'})
        # return JsonResponse({'success': False, 'message': 'Rule not found'}, status=404) is it possible to fail?

    # rule addition
    elif request.method == 'POST':
        if request.method == 'POST':
            form = FirewallRuleForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True, 'message': 'Rule added successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'An error has occurred while adding rule!'}, status=400)
            
def rule_handler_RESTFUL(request, pk):
    rule = FirewallRule.objects.get(id=pk)
    if request.method == 'GET':
        form = FirewallRuleForm(instance=rule)
        data = json.dumps(form.cleaned_data)
        return JsonResponse(data, safe=False)
    #############################################
        if request.method == 'PATCH':
            field_name = request.POST.get('field_name')
            field_value = request.POST.get('field_value')
            if field_name and field_value:
                setattr(rule, field_name, field_value)
                rule.save()
                return JsonResponse(rule.to_dict())
            else:
                return JsonResponse({'error': 'Invalid PATCH request'}, status=400)

        # update two or more fields
        elif request.method == 'PUT':
            rule_data = request.POST.dict()
            del rule_data['id'] # exclude the primary key from the update
            for key, value in rule_data.items():
                setattr(rule, key, value)
            try:
                rule.full_clean()
            except ValidationError as e:
                return JsonResponse({'error': e.message_dict}, status=400)
            else:
                rule.save()
                return JsonResponse(rule.to_dict())
    #############################################
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'rule': rule.to_dict()})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    elif request.method == 'DELETE':
        rule.delete()
        return JsonResponse({'status': 'success', 'message': 'Rule deleted.'})

    # Return an error message for unsupported request methods
    return JsonResponse({'status': 'error', 'message': 'Unsupported request method.'})

"""
