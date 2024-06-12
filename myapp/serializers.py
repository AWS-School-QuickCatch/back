from rest_framework import serializers
from .models import Product, HomeShopping, BroadcastSchedule

class BroadcastProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
