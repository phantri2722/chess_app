import chess

class EventHandler:
    def __init__(self, canvas, game_manager):
        self.canvas = canvas
        self.game_manager = game_manager
        self.selected = None

    def on_click(self, event):
        col = event.x // 60
        row = event.y // 60
        pos = f"{chr(col + ord('a'))}{8 - row}"

        if self.selected:
            if self.selected != pos:
                self.game_manager.move(self.selected, pos)
            self.selected = None
        else:
            if pos in self.game_manager.renderer.pieces:
                piece = self.game_manager.board.piece_at(chess.parse_square(pos))
                if piece and piece.color == self.game_manager.board.turn:
                    self.selected = pos
