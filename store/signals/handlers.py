from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from store.models import Seller, Credit

User = get_user_model()


@receiver(post_save, sender=User)
def create_seller_for_new_user(sender, **kwargs):
    if kwargs["created"]:
        Seller.objects.create(user=kwargs["instance"])


@receiver(post_save, sender=Seller)
def create_credit_for_new_seller(sender, **kwargs):
    if kwargs["created"]:
        Credit.objects.create(seller=kwargs["instance"])
