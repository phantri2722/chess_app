import tkinter as tk
from gui.board_renderer import BoardRenderer
from gui.event_handler import EventHandler
from logic.game_manager import GameManager

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ vua - Trí")
        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.pack()

        self.turn_label = tk.Label(root, text="Lượt: Trắng", font=("Helvetica", 14), fg="blue")
        self.turn_label.pack(pady=5)

        self.board_renderer = BoardRenderer(self.canvas)
        self.board_renderer.draw_board()
        self.board_renderer.load_images()

        self.game_manager = GameManager(self.board_renderer, self.turn_label)
        self.event_handler = EventHandler(self.canvas, self.game_manager)

        self.canvas.bind("<Button-1>", self.event_handler.on_click)

        # Undo/Redo
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="⏪ Undo", command=self.game_manager.undo).pack(side="left", padx=5)
        tk.Button(button_frame, text="Redo ⏩", command=self.game_manager.redo).pack(side="left", padx=5)
