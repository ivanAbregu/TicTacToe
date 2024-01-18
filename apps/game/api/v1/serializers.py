from rest_framework import serializers
from apps.game.models import Game


class PlayerSerializer(serializers.Serializer):
    name = serializers.CharField()
    symbol = serializers.CharField(allow_null=True, required=False)

class CreateGameSerializer(serializers.Serializer):
    players = PlayerSerializer(many=True)
    starting_player = serializers.CharField()


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'current_player', 'board', 'winner']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        winner_username = instance.winner.username if instance.winner else None

        players_data = [
            {"name": instance.player1.username, "symbol": instance.player1.symbol},
            {"name": instance.player2.username, "symbol": instance.player2.symbol},
        ]

        response_data = {
            "game_id": representation['id'],
            "players": players_data,
            "movements_played": instance.movements_played,
            "next_turn": instance.current_player.username,
            "board": instance.board,
            "winner": winner_username,
        }

        return response_data

class PlayInputSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    player = serializers.CharField()
    row = serializers.IntegerField()
    column = serializers.IntegerField()

    def validate_row(self, value):
        if not (0 <= value <= 2):
            raise serializers.ValidationError("Row must be between 0 and 2.")
        return value

    def validate_column(self, value):
        if not (0 <= value <= 2):
            raise serializers.ValidationError("Column must be between 0 and 2.")
        return value
