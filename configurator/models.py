from django.db import models
from django.contrib.auth.models import User

class Component(models.Model):
    CATEGORY_CHOICES = [
        ('CPU', 'პროცესორი (CPU)'),
        ('GPU', 'ვიდეობარათი (GPU)'),
        ('RAM', 'ოპერატიული (RAM)'),
        ('MOBO', 'დედაპლატა (Motherboard)'),
        ('SSD', 'მეხსიერება (SSD)'),
        ('PSU', 'კვების ბლოკი (PSU)'),
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wattage = models.IntegerField(help_text="ენერგომოხმარება ვატებში")

    def __str__(self):
        return f"[{self.category}] {self.brand} {self.name}"

class PCBuild(models.Model):
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='builds')
    components = models.ManyToManyField(Component, related_name='builds')
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(c.price for c in self.components.all())

    def total_wattage(self):
        return sum(c.wattage for c in self.components.all())

    def __str__(self):
        return f"{self.title} - {self.creator.username}"
