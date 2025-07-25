from rest_framework import serializers

class AnalyticsDataSerializer(serializers.Serializer):
    total_users = serializers.IntegerField(read_only=True)
    change_percentage = serializers.FloatField(read_only=True)