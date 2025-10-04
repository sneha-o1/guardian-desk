# helpdesk_mini/tickets/views.py
from django.views.decorators.csrf import csrf_exempt                                                                                            
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket, Comment
from .serializers import TicketSerializer, CommentSerializer
from .permissions import IsOwnerAgentOrAdmin, IsAgentOrAdmin
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.utils.decorators import method_decorator # <-- ADD THIS IMPORT
from django.views.decorators.csrf import csrf_exempt 

# ----------------- A. TICKET API (Core CRUD) -----------------
@method_decorator(csrf_exempt, name='dispatch') # <-- ADD THIS DECORATOR
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    # Apply our custom permission to all actions in this ViewSet
    permission_classes = [IsOwnerAgentOrAdmin]

    # This function customizes the list (GET /api/tickets) based on the user's role (RBAC)
    def get_queryset(self):
        user = self.request.user
        
        # Unauthenticated users get nothing
        if user.is_anonymous:
            return Ticket.objects.none()

        # Admins and Agents see ALL tickets (Judge Check for agents/admins)
        if user.role in ['admin', 'agent']:
            return Ticket.objects.all().order_by('-created_at')
        
        # Regular Users only see tickets they own
        return Ticket.objects.filter(owner=user).order_by('-created_at')

    # This runs when a new ticket is POSTed (POST /api/tickets)
    def perform_create(self, serializer):
        # Automatically set the 'owner' to the logged-in user
        serializer.save(owner=self.request.user)

    # ----------------- B. COMMENTS ACTION (POST /api/tickets/:id/comments) -----------------
    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)
        
        # Check if the user has permission to post to this specific ticket
        self.check_object_permissions(request, ticket) 

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Automatically set the comment's user and the target ticket
        serializer.save(ticket=ticket, user=request.user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ----------------- C. MANDATORY META ENDPOINTS (Judge Check) -----------------
class HealthView(APIView):
    # GET /api/health
    def get(self, request, format=None):
        return Response({"status": "OK"})

class MetaView(APIView):
    # GET /api/meta
    def get(self, request, format=None):
        return Response({"version": "1.0", "project": "HelpDesk Mini"})