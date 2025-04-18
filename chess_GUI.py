import tkinter as tk
from PIL import Image, ImageTk  # Cần cài Pillow để load ảnh

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
        self.images = {}  # Dictionary lưu ảnh
        self.pieces = {}  # Lưu ID quân cờ trên canvas
        self.draw_board()
        self.load_images()
        self.draw_pieces()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
