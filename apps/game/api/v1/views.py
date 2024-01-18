from collections import defaultdict

from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from apps.game.models import Game
from .serializers import GameSerializer, CreateGameSerializer, PlayInputSerializer

from django.contrib.auth import get_user_model

User = get_user_model()

class gameViewSet(ModelViewSet):
    """
        retrieve:
        Return the given game.

        list:
        Return a list of all the existing games.

        create:
        Create a new game. Recieve as param a dic of players
        example: {
                "players":[
                    {
                        "name":"me"
                    },
                    {
                        "name":"other"
                    }
                ],
                "starting_player":"me"
            }

        play:
            {
                "game_id":11,
                "player": "me",
                "row": 2,
                "column":2
            }
    """

    queryset = Game.objects.all().order_by("-created")
    serializer_class = GameSerializer
    
    def create(self, request, *args, **kwargs):
        entry_serializer = CreateGameSerializer(data=request.data)
        entry_serializer.is_valid(raise_exception=True)

        players_data = entry_serializer.validated_data['players']
        starting_player_name = entry_serializer.validated_data['starting_player']

        player1, player2 = self.get_players(players_data)

        if starting_player_name == player1.username:
            current_player = player1
        else:
            current_player = player2

        game_data  = {
            'player1': player1.id,
            'player2': player2.id,
            'current_player': current_player.id,
        }

        game_serializer = GameSerializer(data=game_data)
        game_serializer.is_valid(raise_exception=True)
        game_serializer.save()

        headers = self.get_success_headers(game_serializer.data)
        return Response(game_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_players(self, data):
        p1_name = data[0]['name']
        p1_symbol = data[0].get('symbol', 'X')

        player1 , _ = User.objects.update_or_create(
            username=p1_name,
            defaults={'symbol': p1_symbol}
        )

        p2_name = data[1]['name']
        p2_symbol = data[1].get('symbol', 'O')

        player2 , _ = User.objects.update_or_create(
            username=p2_name,
            defaults={'symbol': p2_symbol}
        )
        return player1, player2

    @action(detail=False, methods=['post'])
    def play(self, request):
        # Deserialize and validate the input data
        
        serializer = PlayInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        player_name = data['player']
        game = get_object_or_404(Game, pk=data['game_id'])
        row = data['row']
        column = data['column']

        if game.is_over:
            return Response({"detail": "The game has already ended."}, status=status.HTTP_400_BAD_REQUEST)

        if player_name != game.current_player.username:
            return Response({"detail": "It's not your turn to play."}, status=status.HTTP_400_BAD_REQUEST)

        if not self.is_valid_move(game.board, row, column):
            return Response({"detail": "Invalid move, already played."}, status=status.HTTP_400_BAD_REQUEST)

        self.update_game_state(game, row, column)

        serializer = GameSerializer(instance=game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def is_valid_move(self, board, row, column):
        return board[row][column]== " "


    def update_game_state(self, game, row, column):
        player = game.current_player
        game.board[row][column] = player.symbol
        if game.is_player_win:
            game.winner = player
            player.score += 1
            player.save() 
        else:
            game.current_player = self.get_next_player(game)
        game.save()

    def get_next_player(self, game):
        return game.player1 if game.current_player == game.player2 else game.player2
