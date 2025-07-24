from rest_framework import serializers
from .models import FAQ, Category

class FAQserializer(serializers.ModelSerializer) :
    category = serializers.StringRelatedField()
    
    class Meta :
        model = FAQ
        fields = '__all__'

