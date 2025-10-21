from rest_framework import serializers

class FloodPredictionSerializer(serializers.Serializer):
    road_sector = serializers.CharField()
    city = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    severity_score = serializers.FloatField()
    severity_label = serializers.CharField()
    distance_m = serializers.FloatField()
    datetime = serializers.DateTimeField()
