from rest_framework import serializers
from enrollment.models import  Training,   Enrollment


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True) 
    last_name = serializers.CharField(source='user.last_name', read_only=True) 
    training_type = serializers.CharField(source='training.training', read_only=True) 
    class Meta:
        model = Enrollment
        fields = '__all__'
