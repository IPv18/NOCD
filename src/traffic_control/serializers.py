"""
    Serializers for the traffic_control app.
    Serializers are used to convert data from the database into a format that
    can be easily consumed by the frontend.
        - TCPolicySerializer: Serializes all policies.
        - ProgramTCPolicySerializer: Serializes policies that match programs.
        - IPTCPolicySerializer: Serializes policies that match IP addresses.
    Note:
        The serializers are used by the viewsets in views.py.
        ProgramTCPolicySerializer and IPTCPolicySerializer are used to
        provide a cleaner interface for front-end. The frontend expects the
        data to be in a certain format, and the frontend code is not flexible
        enough to handle the data returned by the TCPolicySerializer.
    TODO:
        - Refactor the serializers to use inheritance. (IMPORTANT)
        - Add validation for the serializers.
        - Add tests for the serializers.
"""


from rest_framework import serializers
from .models import TCPolicy
from .traffic_control import pack_config, unpack_config

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


class ProgramTCPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TCPolicy
        fields = ["id", "name", "description", "enabled", "startup", "created",
                  "programs", "interface", "direction",
                  "prio", "rate", "burst"]

    programs = serializers.CharField(write_only=True)
    interface = serializers.CharField(write_only=True)
    direction = serializers.CharField(write_only=True)
    prio = serializers.CharField(write_only=True)
    rate = serializers.CharField(write_only=True)
    burst = serializers.CharField(write_only=True)

    def create(self, validated_data):
        config = pack_config(**validated_data)
        return TCPolicy.objects.create(
            config=config,
            name=validated_data["name"],
            description=validated_data["description"],
            enabled=validated_data["enabled"],
            startup=validated_data["startup"]
            )

    def update(self, instance, validated_data):
        instance.config = pack_config(**validated_data)
        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.enabled = validated_data["enabled"]
        instance.startup = validated_data["startup"]
        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(unpack_config(instance.config))
        for ks in ["config", "transport", "ip_src", "ip_dest",
                   "sport", "dport"]:
            if ks in representation:
                del representation[ks]
        return representation


class IPTCPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TCPolicy
        fields = ["id", "name", "description", "enabled", "startup", "created",
                  "interface", "direction", "prio", "rate", "burst",
                  "ip_src", "ip_dest", "sport", "dport", "transport"]

    ip_src = serializers.CharField(write_only=True, allow_blank=True)
    ip_dest = serializers.CharField(write_only=True, allow_blank=True)
    sport = serializers.CharField(write_only=True, allow_blank=True)
    dport = serializers.CharField(write_only=True, allow_blank=True)
    transport = serializers.CharField(write_only=True, allow_blank=True)
    interface = serializers.CharField(write_only=True)
    direction = serializers.CharField(write_only=True)
    prio = serializers.CharField(write_only=True)
    rate = serializers.CharField(write_only=True)
    burst = serializers.CharField(write_only=True)

    def create(self, validated_data):
        config = pack_config(**validated_data)
        return TCPolicy.objects.create(
            config=config,
            name=validated_data["name"],
            description=validated_data["description"],
            enabled=validated_data["enabled"],
            startup=validated_data["startup"]
            )

    def update(self, instance, validated_data):
        instance.config = pack_config(**validated_data)
        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.enabled = validated_data["enabled"]
        instance.startup = validated_data["startup"]
        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(unpack_config(instance.config))
        for ks in ["config", "programs"]:
            if ks in representation:
                del representation[ks]
        return representation
