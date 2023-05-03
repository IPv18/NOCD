from rest_framework import serializers
from .models import TCPolicy


class TCPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TCPolicy
        fields = ["id", "name", "config", "description",
                  "enabled", "startup", "created"]
        
    def validate(self, data):
        if data.get("startup") is True and data.get("enabled", False) is False:
            raise serializers.ValidationError(
                "A policy cannot be enabled at startup if it is disabled."
            )
        return data
    
    
class ProgramTCPolicySerializer(TCPolicySerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            **instance.config.get("class", {}),
            **{key: instance.config.get(key)
               for key in ["interface", "direction", "programs"]}
        })
        representation["created"]
        return representation


class IPTCPolicySerializer(TCPolicySerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            **instance.config.get("class", {}),
            "interface": instance.config.get("interface"),
            "direction": instance.config.get("direction"),
            **instance.config.get("match", {})
        })
        return representation


""" 
    programs = serializers.SerializerMethodField()
    interface = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    burst = serializers.SerializerMethodField()
    prio = serializers.SerializerMethodField()
config": {
            "class": {
                "burst": "100024",
                "prio": 1,
                "rate": "1000kbit"
            },
            "direction": "outbound",
            "interface": "wlp0s20f3",
            "programs": [
                "chrome"
            ]
        } 
"""