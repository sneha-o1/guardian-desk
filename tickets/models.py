# helpdesk_mini/tickets/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# tickets/models.py (Add this function at the top, near imports)

def default_deadline():
    # Sets the deadline to 48 hours from now
    return timezone.now() + timedelta(hours=48)

# ... rest of the code ...
# ----------------- CUSTOM USER MODEL (REQUIRED FOR ROLES) -----------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return f"{self.username} ({self.role})"
        
        
# ----------------- TICKET MODEL (CORE DATA & SLA CHECK) -----------------
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    # Core fields
    title = models.CharField(max_length=255)
    description = models.TextField() # <--- CORRECT NAME IS 'description'
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    
    # Role-based fields
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_tickets', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    
    # SLA & Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=default_deadline)
    
    # Judge Check: Is the SLA breached?
    is_breached = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Ticket {self.id}: {self.title} ({self.status})"
        
    # Override save method to implement the SLA check logic
    def save(self, *args, **kwargs):
        # SLA CHECK: Mark as breached if past deadline AND the status is not 'closed'
        if self.status != 'closed' and self.deadline < timezone.now():
            self.is_breached = True
        else:
            self.is_breached = False 
        super().save(*args, **kwargs)


# ----------------- COMMENT MODEL -----------------
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.ticket.id} by {self.user.username}"