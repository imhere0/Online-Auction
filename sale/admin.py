from django.contrib import admin
from .models import User, Listing, BidModel, CommentModel, Winner

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(BidModel)
admin.site.register(CommentModel)
admin.site.register(Winner)

