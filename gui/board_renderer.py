from PIL import Image, ImageTk

SQUARE_SIZE = 60

class BoardRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.images = {}
        self.pieces = {}

    def draw_board(self):
        colors = ["#EEEED2", "#769656"]
        for row in range(8):
            for col in range(8):
                x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def load_images(self):
        for name in ['wK','wQ','wR','wB','wN','wP','bK','bQ','bR','bB','bN','bP']:
            path = f'images/{name}.png'
            img = Image.open(path).resize((SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.LANCZOS)
            self.images[name] = ImageTk.PhotoImage(img)
