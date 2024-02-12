from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Seller(BaseModel):
    first_name = models.CharField(max_length=55, blank=True, null=True)
    last_name = models.CharField(max_length=55, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Credit(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
