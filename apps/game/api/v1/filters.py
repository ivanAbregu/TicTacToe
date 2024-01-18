import django_filters
from apps.game.models import Game


class GameFilter(django_filters.FilterSet):
    class Meta:
        model = Game
        fields = ['status']
