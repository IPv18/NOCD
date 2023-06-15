from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from collections import defaultdict
import psutil
import pyshark
import time
import threading

# Create your views here.
traffic_distribution_percentages = {}

def DashboardPage(request):
	threading.Thread(target=get_network_traffic_distribution).start()

	return render(request, 'dashboard/dashboard.html')

def Widgets(request):
	param = request.GET.get('widget')
	if param == 'cpu_utilization':
		return cpu_utilization()
	
	elif param == 'memory_utilization':
		return memory_utilization()
	
	elif param == 'download':
		return network_traffic_utilization(type='download')
	
	elif param == 'upload':
		return network_traffic_utilization(type='upload')
	
	elif param == 'pie':	
		return JsonResponse(traffic_distribution_percentages)



def cpu_utilization():
	cpu_percent = psutil.cpu_percent(interval=1)
	return JsonResponse({'cpu_percent': cpu_percent})


def memory_utilization():
	memory_percent = psutil.virtual_memory().percent
	return JsonResponse({'memory_percent': memory_percent})


def network_traffic_utilization(type):
	
	total_download = 0
	total_upload = 0
	net_io_counters = psutil.net_io_counters(pernic=True)
	
	for interface, io_counters in net_io_counters.items():
		if interface != 'lo':
			total_download += io_counters.bytes_recv
			total_upload += io_counters.bytes_sent
	
	total_download = total_download / (1024 * 1024)  # Convert bytes to megabytes
	total_upload = total_upload / (1024 * 1024)  # Convert bytes to megabytes

	if type == 'download':
		return JsonResponse({'download': f"{total_download:.2f}"})
	else:
		return JsonResponse({'upload': f"{total_upload:.2f}"})



# For PieChart 

def get_network_traffic_distribution():
	traffic_distribution = defaultdict(int)

	# Get the network interfaces
	# interfaces = psutil.net_if_stats().keys()

	# Sniff packets on each interface
	interface="wlp0s20f3"
	try:
		# Start packet capture on the interface
		global traffic_distribution_percentages 
		traffic_distribution_percentages = {}
	
		capture = pyshark.LiveCapture(interface=interface, display_filter='')

		# Capture packets for a certain duration (adjust as needed)
		packet_limit = 1000000
		captured_packets = capture.sniff_continuously(packet_count=packet_limit)
		
		# Process captured packets and update traffic distribution
		for packet in captured_packets:
			layer = packet.highest_layer

			if(layer in ["TCP", "UDP", "ARP", "TLS", "ICMPV6", "DNS", "HTTP"]):
				traffic_distribution[layer] += 1

			# total_packets = sum(traffic_distribution.values())
			traffic_distribution_percentages = {
				protocol: (count) for protocol, count in traffic_distribution.items()
			}


	except pyshark.capture.capture.TSharkCrashException as e:
		print(f"Error capturing packets on interface {interface}: {e}")


				
