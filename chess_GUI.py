import tkinter as tk
from PIL import Image, ImageTk
import chess  

BOARD_SIZE = 8
SQUARE_SIZE = 60

# Cấu hình vị trí các quân cờ theo hàng
INITIAL_POSITIONS = {
    "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
    "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP", "h2": "wP",
    "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
    "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
}

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ vua - Trí")
        self.canvas = tk.Canvas(root, width=BOARD_SIZE*SQUARE_SIZE, height=BOARD_SIZE*SQUARE_SIZE)
        self.canvas.pack()
        self.images = {}
        self.pieces = {}  # Lưu ID quân cờ trên canvas
        self.draw_board()
        self.load_images()
        self.draw_pieces()
        self.selected_piece = None  # Vị trí đang chọn
        self.canvas.bind("<Button-1>", self.on_click)
        self.board = chess.Board()
        self.turn_label = tk.Label(root, text="Lượt: Trắng", font=("Helvetica", 14), fg="blue")
        self.turn_label.pack(pady=5)
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        undo_btn = tk.Button(button_frame, text="⏪ Undo", command=self.undo_move)
        undo_btn.pack(side="left", padx=5)

        redo_btn = tk.Button(button_frame, text="Redo ⏩", command=self.redo_move)
        redo_btn.pack(side="left", padx=5)

        self.redo_stack = []


    def draw_board(self):
        colors = ["#EEEED2", "#769656"]  # Trắng - xanh
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * SQUARE_SIZE
                y1 = row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def load_images(self):
        pieces = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP']
        for piece in pieces:
            img_path = f'images/{piece}.png'
            img = Image.open(img_path)
            img = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.LANCZOS)
            self.images[piece] = ImageTk.PhotoImage(img)

    def draw_pieces(self):
        for pos, piece in INITIAL_POSITIONS.items():
            col = ord(pos[0]) - ord('a')
            row = 8 - int(pos[1])
            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE
            self.pieces[pos] = self.canvas.create_image(x, y, anchor='nw', image=self.images[piece])
    
    def on_click(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        clicked_pos = self.coords_to_pos(row, col)

        if self.selected_piece:
            # Click lần 2: di chuyển nếu khác vị trí
            if clicked_pos != self.selected_piece:
                self.move_piece(self.selected_piece, clicked_pos)
            self.selected_piece = None
        else:
            # Click lần 1: chọn quân nếu là đúng màu
            if clicked_pos in self.pieces:
                piece_square = chess.parse_square(clicked_pos)
                piece = self.board.piece_at(piece_square)
                if piece is None:
                    return
                if piece.color != self.board.turn:
                    print("Không phải lượt của bạn!")
                    return
                self.selected_piece = clicked_pos


    def move_piece(self, from_pos, to_pos):
        if from_pos not in self.pieces:
            return
        
        move_uci = self.pos_to_uci(from_pos, to_pos)

        #Kiem tra nuoc di co hop le khong
        move = chess.Move.from_uci(move_uci)
        if move not in self.board.legal_moves:
            print("Nuớc đi không hợp lệ")
            return
        
        #Cập nhật logic bàn cờ
        self.board.push(move)
        self.redo_stack.clear()

         # Kiểm tra kết thúc ván cờ
        if self.board.is_game_over():
            result = self.board.result()
            if self.board.is_checkmate():
                winner = "Trắng" if self.board.turn == chess.BLACK else "Đen"
                tk.messagebox.showinfo("Chiếu bí", f"{winner} thắng bằng chiếu bí!")
            elif self.board.is_stalemate():
                tk.messagebox.showinfo("Hòa", "Hòa vì bí nước (Stalemate)")
            elif self.board.is_insufficient_material():
                tk.messagebox.showinfo("Hòa", "Hòa do thiếu quân")
            else:
                tk.messagebox.showinfo("Kết thúc", f"Ván cờ kết thúc. Kết quả: {result}")

        self.update_turn_label()

        # Xoá quân cờ nếu có ở vị trí đích (ăn quân)
        if to_pos in self.pieces:
            self.canvas.delete(self.pieces[to_pos])
            del self.pieces[to_pos]

        # Di chuyển quân cờ
        piece_id = self.pieces[from_pos]
        col = ord(to_pos[0]) - ord('a')
        row = 8 - int(to_pos[1])
        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE
        self.canvas.coords(piece_id, x, y)

        # Cập nhật vị trí trong dict
        self.pieces[to_pos] = piece_id
        del self.pieces[from_pos]


    def coords_to_pos(self, row, col):
        return f"{chr(col + ord('a'))}{8 - row}"
    
    def pos_to_uci(self, from_pos, to_pos):
        return from_pos + to_pos
    
    def update_turn_label(self):
        if self.board.turn == chess.WHITE:
            self.turn_label.config(text="Lượt: Trắng", fg="blue")
        else:
            self.turn_label.config(text="Lượt: Đen", fg="green")

    def undo_move(self):
        if len(self.board.move_stack) == 0:
            return

        move = self.board.pop()
        self.redo_stack.append(move)
        self.redraw_board()

    def redo_move(self):
        if not self.redo_stack:
            return

        move = self.redo_stack.pop()
        self.board.push(move)
        self.redraw_board()

    def redraw_board(self):
        # Xoá toàn bộ quân cờ hiện có trên canvas
        for piece_id in self.pieces.values():
            self.canvas.delete(piece_id)
        self.pieces.clear()

        # Duyệt qua tất cả các ô vuông trên bàn cờ
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                pos = chess.square_name(square)
                image_key = piece.symbol()

                # Đảm bảo key tồn tại trong self.images
                if image_key in self.images:
                    image = self.images[image_key]
                    col = ord(pos[0]) - ord('a')
                    row = 8 - int(pos[1])
                    x = col * SQUARE_SIZE
                    y = row * SQUARE_SIZE
                    piece_id = self.canvas.create_image(x, y, image=image, anchor="nw")
                    self.pieces[pos] = piece_id

        # Cập nhật lượt chơi
        self.update_turn_label()



if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
