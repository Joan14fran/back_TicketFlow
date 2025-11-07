from django.db import models
from django.conf import settings


USER_MODEL = settings.AUTH_USER_MODEL


class Category(models.Model):
    """
    Modelo para las categorías de los tickets (Ej: 'Soporte Técnico', 'Facturación').
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    """
    El modelo principal para un ticket de soporte.
    """
    STATUS_CHOICES = (
        ('open', 'Abierto'),
        ('in_progress', 'En Progreso'),
        ('closed', 'Cerrado'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, 
        related_name='tickets'
    )
    created_by = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='created_tickets' 
    )
    assigned_to = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='assigned_tickets' 
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id}: {self.title}"

class Comment(models.Model):
    """
    Modelo para los comentarios dentro de un ticket.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE, 
        related_name='comments' 
    )
    user = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE 
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.user.username} en Ticket #{self.ticket.id}"