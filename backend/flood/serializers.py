from rest_framework import serializers

class FloodPredictionSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    road = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    neighborhood = serializers.CharField(required=False, allow_null=True)
    flood_probability = serializers.FloatField(required=False)
    severity_score = serializers.FloatField(required=False)
    severity_label = serializers.CharField(required=False)
    datetime = serializers.DateTimeField()
