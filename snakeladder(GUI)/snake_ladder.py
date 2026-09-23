
# Cara main:
#     python ular_tangga_gui.py

# Fitur:
# - Papan digambar visual 10x10 (kotak 1-100) di canvas.
# - Ular & tangga digambar sebagai garis merah/hijau.
# - Token pemain berupa lingkaran berwarna, bergerak saat giliran.
# - Mode SOLO: kamu vs 1-3 bot (komputer jalan otomatis).
# - Mode MULTIPLAYER: 2-4 pemain manusia bergantian.
# - Tombol "Lempar Dadu" + tampilan angka dadu.
# - Log permainan di panel samping.

import tkinter as tk
from tkinter import simpledialog, messagebox
import random

BOARD_SIZE = 100
GRID = 10
CELL = 60
PADDING = 20
CANVAS_SIZE = GRID * CELL + PADDING * 2

SNAKES = {99: 41, 89: 53, 69: 33, 62: 19, 46: 5, 27: 1}
LADDERS = {2: 23, 8: 34, 20: 77, 32: 68, 41: 79, 74: 88}

PLAYER_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f"]


def cell_to_xy(num):
    """Konversi nomor kotak (1-100) ke koordinat tengah piksel di canvas."""
    idx = num - 1
    
     # 0 = baris paling bawah
    row = idx // GRID
    col = idx % GRID

    # baris ganjil arah kanan-ke-kiri (pola zig-zag ular tangga asli)
    if row % 2 == 1:
        col = GRID - 1 - col
    x = PADDING + col * CELL + CELL / 2
    y = PADDING + (GRID - 1 - row) * CELL + CELL / 2
    return x, y


class Player:
    def __init__(self, name, color, is_bot=False):
        self.name = name
        self.color = color
        self.position = 0
        self.is_bot = is_bot
        self.token_id = None


class SnakeLadderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(" Ular Tangga ")
        self.root.resizable(False, False)

        self.players = []
        self.current_index = 0
        self.winner = None
        self.dice_value = 1
        self.game_started = False

        self.build_start_screen()

    # ---------- LAYAR AWAL (PILIH MODE) ----------
    def build_start_screen(self):
        self.start_frame = tk.Frame(self.root, padx=30, pady=30)
        self.start_frame.pack()

        tk.Label(self.start_frame, text=" ULAR TANGGA ", font=("Helvetica", 22, "bold")).pack(pady=10)

        tk.Label(self.start_frame, text="Nama kamu:", font=("Helvetica", 12)).pack(pady=(10, 0))
        self.name_entry = tk.Entry(self.start_frame, font=("Helvetica", 12), justify="center")
        self.name_entry.insert(0, "Pemain")
        self.name_entry.pack(pady=5)

        tk.Label(self.start_frame, text="Jumlah lawan bot (1-3):", font=("Helvetica", 12)).pack(pady=(10, 0))
        self.bot_var = tk.IntVar(value=1)
        tk.Spinbox(self.start_frame, from_=1, to=3, textvariable=self.bot_var,
                   font=("Helvetica", 12), justify="center", width=5).pack(pady=5)

        tk.Button(self.start_frame, text="▶ Main Sendiri (vs Bot)", font=("Helvetica", 12, "bold"),
                  bg="#2ecc71", fg="white", command=self.start_solo).pack(pady=(20, 5), fill="x")

        tk.Button(self.start_frame, text="👥 Main Multiplayer (2-4 orang)", font=("Helvetica", 12),
                  bg="#3498db", fg="white", command=self.start_multiplayer).pack(pady=5, fill="x")

    def start_solo(self):
        name = self.name_entry.get().strip() or "Pemain"
        n_bot = self.bot_var.get()

        self.players = [Player(name, PLAYER_COLORS[0], is_bot=False)]
        for i in range(n_bot):
            self.players.append(Player(f"Bot {i + 1}", PLAYER_COLORS[i + 1], is_bot=True))

        self.launch_game()

    def start_multiplayer(self):
        n = simpledialog.askinteger("Jumlah Pemain", "Masukkan jumlah pemain (2-4):",
                                     minvalue=2, maxvalue=4, parent=self.root)
        if not n:
            return

        self.players = []
        for i in range(n):
            name = simpledialog.askstring("Nama Pemain", f"Nama pemain {i + 1}:", parent=self.root) or f"Pemain{i + 1}"
            self.players.append(Player(name, PLAYER_COLORS[i], is_bot=False))

        self.launch_game()

    # ---------- LAYAR PERMAINAN ----------
    def launch_game(self):
        self.start_frame.destroy()
        self.build_game_screen()
        self.draw_board()
        self.spawn_tokens()
        self.update_status()

    def build_game_screen(self):
        main = tk.Frame(self.root)
        main.pack(padx=10, pady=10)

        # Canvas papan
        self.canvas = tk.Canvas(main, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white",
                                 highlightthickness=1, highlightbackground="black")
        self.canvas.grid(row=0, column=0, rowspan=6)

        # Panel kanan
        side = tk.Frame(main, padx=15)
        side.grid(row=0, column=1, sticky="n")

        self.status_label = tk.Label(side, text="", font=("Helvetica", 13, "bold"), justify="left")
        self.status_label.pack(pady=(0, 10), anchor="w")

        self.dice_label = tk.Label(side, text="🎲", font=("Helvetica", 40))
        self.dice_label.pack(pady=10)

        self.roll_btn = tk.Button(side, text="Lempar Dadu", font=("Helvetica", 13, "bold"),
                                   bg="#e67e22", fg="white", width=16, command=self.human_roll)
        self.roll_btn.pack(pady=10)

        tk.Label(side, text="Log Permainan:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(20, 0))
        self.log_box = tk.Listbox(side, width=32, height=14, font=("Helvetica", 9))
        self.log_box.pack(pady=5)

        tk.Label(side, text="Skor / Posisi:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(10, 0))
        self.pos_label = tk.Label(side, text="", font=("Helvetica", 10), justify="left")
        self.pos_label.pack(anchor="w")

    def draw_board(self):
        for num in range(1, BOARD_SIZE + 1):
            idx = num - 1
            row = idx // GRID
            col = idx % GRID
            if row % 2 == 1:
                col = GRID - 1 - col
            x0 = PADDING + col * CELL
            y0 = PADDING + (GRID - 1 - row) * CELL
            x1, y1 = x0 + CELL, y0 + CELL
            color = "#f7f7f7" if (row + col) % 2 == 0 else "#e8e8e8"
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#cccccc")
            self.canvas.create_text(x0 + 6, y0 + 8, text=str(num), font=("Helvetica", 7), anchor="nw", fill="#888")

        # Gambar ular (merah)
        for head, tail in SNAKES.items():
            x0, y0 = cell_to_xy(head)
            x1, y1 = cell_to_xy(tail)
            self.canvas.create_line(x0, y0, x1, y1, fill="#e74c3c", width=3, arrow=tk.LAST, dash=(4, 2))

        # Gambar tangga (hijau)
        for bottom, top in LADDERS.items():
            x0, y0 = cell_to_xy(bottom)
            x1, y1 = cell_to_xy(top)
            self.canvas.create_line(x0, y0, x1, y1, fill="#27ae60", width=3, arrow=tk.LAST)

    def spawn_tokens(self):
        for i, p in enumerate(self.players):
            x, y = cell_to_xy(1)
            offset = (i % 4) * 8 - 12
            r = 10
            p.token_id = self.canvas.create_oval(x + offset - r, y - r, x + offset + r, y + r,
                                                  fill=p.color, outline="black", width=2)

    def move_token(self, player):
        x, y = cell_to_xy(max(player.position, 1))
        i = self.players.index(player)
        offset = (i % 4) * 8 - 12
        r = 10
        self.canvas.coords(player.token_id, x + offset - r, y - r, x + offset + r, y + r)

    # ---------- LOGIKA PERMAINAN ----------
    def current_player(self):
        return self.players[self.current_index]

    def log(self, text):
        self.log_box.insert(tk.END, text)
        self.log_box.see(tk.END)

    def update_status(self):
        p = self.current_player()
        giliran = "🤖 Giliran Bot" if p.is_bot else "👤 Giliran Kamu"
        self.status_label.config(text=f"{giliran}: {p.name}")
        pos_text = "\n".join(f"{q.name}: kotak {q.position}" for q in self.players)
        self.pos_label.config(text=pos_text)
        self.roll_btn.config(state="disabled" if p.is_bot else "normal")

    def human_roll(self):
        if self.winner:
            return
        self.roll_btn.config(state="disabled")
        self.animate_and_roll(self.current_player())

    def animate_and_roll(self, player, steps=8):
        """Animasi dadu berputar sebelum menampilkan hasil akhir."""
        if steps > 0:
            self.dice_label.config(text=str(random.randint(1, 6)))
            self.root.after(60, lambda: self.animate_and_roll(player, steps - 1))
        else:
            dice = random.randint(1, 6)
            self.dice_label.config(text=self.dice_face(dice))
            self.resolve_move(player, dice)

    def dice_face(self, n):
        faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        return faces.get(n, str(n))

    def resolve_move(self, player, dice):
        new_pos = player.position + dice

        if new_pos > BOARD_SIZE:
            self.log(f"{player.name} dadu {dice} → lewat kotak {BOARD_SIZE}, tetap di {player.position}")
            self.move_token(player)
            self.end_turn(dice)
            return

        player.position = new_pos
        self.log(f"{player.name} dadu {dice} → kotak {new_pos}")
        self.move_token(player)

        if new_pos in SNAKES:
            tail = SNAKES[new_pos]
            self.log(f" Kena ular! Turun ke {tail}")
            player.position = tail
            self.root.after(300, lambda: self.move_token(player))
        elif new_pos in LADDERS:
            top = LADDERS[new_pos]
            self.log(f" Kena tangga! Naik ke {top}")
            player.position = top
            self.root.after(300, lambda: self.move_token(player))

        if player.position == BOARD_SIZE:
            self.winner = player
            self.root.after(400, lambda: self.announce_winner(player))
            return

        self.root.after(400, lambda: self.end_turn(dice))

    def end_turn(self, dice):
        self.update_status_positions()
        if dice != 6:
            self.current_index = (self.current_index + 1) % len(self.players)
        else:
            self.log(f"   ↻ Dadu 6! Giliran tambahan.")
        self.update_status()
        self.next_turn_check()

    def update_status_positions(self):
        pos_text = "\n".join(f"{q.name}: kotak {q.position}" for q in self.players)
        self.pos_label.config(text=pos_text)

    def next_turn_check(self):
        if self.winner:
            return
        p = self.current_player()
        if p.is_bot:
            self.root.after(700, lambda: self.animate_and_roll(p))

    def announce_winner(self, player):
        self.update_status_positions()
        self.log(f" {player.name} MENANG!")
        self.status_label.config(text=f"🏆 {player.name} MENANG!")
        self.roll_btn.config(state="disabled")
        messagebox.showinfo("Selesai!", f" {player.name} mencapai kotak 100 dan MENANG! ")


def main():
    root = tk.Tk()
    app = SnakeLadderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
