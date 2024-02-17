from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        seller_id = int(view.kwargs.get("seller_pk"))
        if request.method in permissions.SAFE_METHODS:
            return (request.user.seller.id == seller_id) or request.user.is_staff
        return request.user.seller.id == seller_id

    def has_object_permission(self, request, view, obj):
        return (obj.seller == request.user.seller) or request.user.is_staff
