from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player2')
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_current_player')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_won', blank=True, null=True)
    board = models.JSONField(default=[[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']])
    # board = models.CharField(max_length=9, default=' ' * 9)

    @property
    def movements_played(self):
        return sum(3-row.count(' ') for row in self.board)

    @property
    def is_over(self):
        return self.movements_played == 9 or self.winner is not None

    @property
    def is_player_win(self):
        symbol = self.current_player.symbol
        board = self.board
        return self.movements_played > 4 and (
            any(all(r == symbol for r in row) for row in board) or  # Check rows
            any(all(row[i] == symbol for row in board) for i in range(3)) or  # Check columns
            all(board[i][i] == symbol for i in range(3)) or  # Check main diagonal
            all(board[i][2 - i] == symbol for i in range(3))  # Check secondary diagonal
        )

    def __str__(self):
        return f"{self.player1.username} vs {self.player2.username}"
