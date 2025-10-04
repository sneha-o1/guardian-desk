# helpdesk_mini/tickets/serializers.py

from rest_framework import serializers
from .models import Ticket, Comment, CustomUser

# 1. USER SERIALIZER 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role'] 

# 2. COMMENT SERIALIZER 
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['ticket', 'user'] 

# 3. TICKET SERIALIZER 
class TicketSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True) 

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'owner', 'assigned_to', # <--- ENSURE 'description' is here
                  'created_at', 'deadline', 'is_breached']
        read_only_fields = ['owner', 'is_breached']