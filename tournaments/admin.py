# Register your models here.
from django.contrib import admin
from .models import TournamentInput, PokerUser

admin.site.register(TournamentInput)
admin.site.register(PokerUser)