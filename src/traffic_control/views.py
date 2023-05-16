from django.http import StreamingHttpResponse
from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.interface_metric import read_last_pkt_batch

from .models import TCPolicy
from .serializers import (
    TCPolicySerializer,
    IPTCPolicySerializer,
    ProgramTCPolicySerializer)
from utils.utils import get_interfaces as local_get_interfaces


class HomePageView(TemplateView):
    template_name = 'traffic_control/home.html'


class TCPolicyViewSet(viewsets.ModelViewSet):
    model = TCPolicy
    queryset = TCPolicy.objects.all()
    serializer_class = TCPolicySerializer


class ProgramTCPolicyViewSet(viewsets.ModelViewSet):
    model = TCPolicy
    queryset = TCPolicy.objects.filter(config__has_key="programs")
    serializer_class = ProgramTCPolicySerializer


class IPTCPolicyViewSet(viewsets.ModelViewSet):
    model = TCPolicy
    queryset = TCPolicy.objects.filter(config__has_key="match")
    serializer_class = IPTCPolicySerializer


@api_view(['GET'])
def interface_metrics(request):
    """
    Returns a JSON response with the number of packets sent and received.
    """
    interface = request.query_params.get("interface")
    if interface:
        return StreamingHttpResponse(read_last_pkt_batch(interface))
    else:
        return Response({"error": "No interface specified."})


@api_view(['GET'])
def get_interfaces(request):
    return Response(local_get_interfaces())
