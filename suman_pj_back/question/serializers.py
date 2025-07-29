from rest_framework import serializers
from .models import FAQ, Category

class FAQserializer(serializers.ModelSerializer) :
    category = serializers.SlugRelatedField(
        slug_field = 'name',
        queryset = Category.objects.all()
    )
    
    class Meta :
        model = FAQ
        fields = '__all__'
        read_only_fields = ['created_at']
