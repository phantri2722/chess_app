import chess
from tkinter import messagebox

class GameManager:
    def __init__(self, renderer, turn_label):
        self.board = chess.Board()
        self.renderer = renderer
        self.turn_label = turn_label
        self.redo_stack = []

        self.redraw()

    def move(self, from_pos, to_pos):
        move = chess.Move.from_uci(from_pos + to_pos)
        if move not in self.board.legal_moves:
            print("Không hợp lệ")
            return

        self.board.push(move)
        self.redo_stack.clear()
        self.redraw()
        self.check_game_end()

    def check_game_end(self):
        if self.board.is_game_over():
            result = self.board.result()
            if self.board.is_checkmate():
                winner = "Trắng" if self.board.turn == chess.BLACK else "Đen"
                messagebox.showinfo("Chiếu bí", f"{winner} thắng!")
            elif self.board.is_stalemate():
                messagebox.showinfo("Hòa", "Hòa vì bí nước")
            elif self.board.is_insufficient_material():
                messagebox.showinfo("Hòa", "Hòa do thiếu quân")
            else:
                messagebox.showinfo("Kết thúc", f"Kết quả: {result}")

    def undo(self):
        if self.board.move_stack:
            self.redo_stack.append(self.board.pop())
            self.redraw()

    def redo(self):
        if self.redo_stack:
            self.board.push(self.redo_stack.pop())
            self.redraw()

    def redraw(self):
        self.renderer.canvas.delete("all")
        self.renderer.draw_board()
        self.renderer.pieces.clear()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                pos = chess.square_name(square)
                img_key = piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
                if img_key in self.renderer.images:
                    col = ord(pos[0]) - ord('a')
                    row = 8 - int(pos[1])
                    x, y = col * 60, row * 60
                    img = self.renderer.images[img_key]
                    piece_id = self.renderer.canvas.create_image(x, y, image=img, anchor="nw")
                    self.renderer.pieces[pos] = piece_id

        self.turn_label.config(text="Lượt: Trắng" if self.board.turn else "Lượt: Đen",
                               fg="blue" if self.board.turn else "green")
