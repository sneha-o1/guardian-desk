# helpdesk_mini/tickets/permissions.py

from rest_framework import permissions

class IsOwnerAgentOrAdmin(permissions.BasePermission):
    """
    Custom permission: 
    - Authenticated users can access.
    - Owners, Agents, and Admins can view/edit their own ticket details.
    - Agents/Admins can see ALL tickets in a list.
    """
    
    # Permission check for the entire list (GET /api/tickets/) or creation (POST /api/tickets/)
    def has_permission(self, request, view):
        # Only authenticated users are allowed in this API
        return request.user.is_authenticated

    # Permission check for a single object (GET/PATCH/DELETE /api/tickets/:id)
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admins and Agents have full read/write access to any ticket object
        if user.role in ['admin', 'agent']:
            return True
        
        # Owners can view (SAFE_METHODS: GET, HEAD, OPTIONS) their own ticket
        if obj.owner == user and request.method in permissions.SAFE_METHODS:
            return True
            
        # Owners can also PATCH/update their own ticket (e.g., to fix a typo)
        if obj.owner == user and request.method in ['PUT', 'PATCH']:
            return True 
            
        # All other access is denied
        return False

class IsAgentOrAdmin(permissions.BasePermission):
    """Allows POST/PATCH/DELETE access only to agents and admins (e.g., for system-level actions)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['agent', 'admin']