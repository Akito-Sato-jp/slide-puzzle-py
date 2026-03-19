import tkinter as tk
from tkinter import messagebox

class HakoiriMusume:
    def __init__(self, root):
        self.root = root
        self.root.title("箱入り娘 - スライド連続移動版")
        
        self.size = 80
        self.moves = 0
        
        self.label_moves = tk.Label(root, text=f"手数: {self.moves}", font=("Arial", 14))
        self.label_moves.pack()

        self.canvas = tk.Canvas(root, width=self.size*4, height=self.size*5 + 20, bg="#fdf6e3")
        self.canvas.pack(pady=10)
        
        # 出口のガイド
        self.canvas.create_rectangle(self.size*1, self.size*5, self.size*3, self.size*5+10, fill="#ef4444", outline="")

        self.pieces = {}
        self.setup_game()

    def setup_game(self):
        configs = [
            ("娘", 2, 2, 1, 0, "#ef4444"),
            ("親1", 1, 2, 0, 0, "#3b82f6"), ("親2", 1, 2, 3, 0, "#3b82f6"),
            ("親3", 1, 2, 0, 2, "#3b82f6"), ("親4", 1, 2, 3, 2, "#3b82f6"),
            ("横木", 2, 1, 1, 2, "#10b981"),
            ("卒1", 1, 1, 0, 4, "#f59e0b"), ("卒2", 1, 1, 1, 3, "#f59e0b"),
            ("卒3", 1, 1, 2, 3, "#f59e0b"), ("卒4", 1, 1, 3, 4, "#f59e0b"),
        ]
        for name, w, h, x, y, color in configs:
            tag = f"p_{name}"
            self.canvas.create_rectangle(x*self.size, y*self.size, (x+w)*self.size, (y+h)*self.size,
                                       fill=color, outline="#1e293b", width=3, tags=tag)
            self.canvas.create_text((x+w/2)*self.size, (y+h/2)*self.size, 
                                     text=name, font=("Helvetica", 14, "bold"), fill="white", tags=tag)
            self.pieces[tag] = {"w": w, "h": h, "x": x, "y": y}
            self.canvas.tag_bind(tag, "<ButtonPress-1>", lambda e, t=tag: self.on_start(e, t))
            self.canvas.tag_bind(tag, "<B1-Motion>", lambda e, t=tag: self.on_drag(e, t))
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", lambda e, t=tag: self.on_drop(e, t))

    def on_start(self, event, tag):
        self.last_x, self.last_y = event.x, event.y
        self.canvas.tag_raise(tag)

    def on_drag(self, event, tag):
        dx, dy = event.x - self.last_x, event.y - self.last_y
        self.canvas.move(tag, dx, dy)
        self.last_x, self.last_y = event.x, event.y

    def on_drop(self, event, tag):
        p = self.pieces[tag]
        curr_coords = self.canvas.coords(self.canvas.find_withtag(tag)[0])
        nx, ny = round(curr_coords[0]/self.size), round(curr_coords[1]/self.size)

        # 移動が直線（縦または横）かつ、経路が空いているかチェック
        if self.is_path_clear(tag, p['x'], p['y'], nx, ny):
            if nx != p['x'] or ny != p['y']:
                p['x'], p['y'] = nx, ny
                self.moves += 1
                self.label_moves.config(text=f"手数: {self.moves}")
        
        self.snap_to_grid(tag)
        self.check_clear(tag)

    def is_path_clear(self, target_tag, x1, y1, x2, y2):
        # 盤面外チェック
        p = self.pieces[target_tag]
        if x2 < 0 or x2 + p['w'] > 4 or y2 < 0 or y2 + p['h'] > 5:
            return False
        # 斜め移動は禁止
        if x1 != x2 and y1 != y2:
            return False

        # 経路上の全マスをチェック（1マスずつ進んで衝突を確認）
        step_x = 1 if x2 > x1 else -1 if x2 < x1 else 0
        step_y = 1 if y2 > y1 else -1 if y2 < y1 else 0
        
        curr_x, curr_y = x1, y1
        while (curr_x != x2 or curr_y != y2):
            curr_x += step_x
            curr_y += step_y
            # この位置に他のブロックがあるか
            for tag, other in self.pieces.items():
                if tag == target_tag: continue
                # 矩形同士の衝突判定
                if not (curr_x + p['w'] <= other['x'] or curr_x >= other['x'] + other['w'] or
                        curr_y + p['h'] <= other['y'] or curr_y >= other['y'] + other['h']):
                    return False
        return True

    def snap_to_grid(self, tag):
        p = self.pieces[tag]
        curr = self.canvas.coords(self.canvas.find_withtag(tag)[0])
        self.canvas.move(tag, (p['x']*self.size)-curr[0], (p['y']*self.size)-curr[1])

    def check_clear(self, tag):
        p = self.pieces[tag]
        if "娘" in tag and p['x'] == 1 and p['y'] == 3:
            messagebox.showinfo("Clear", f"脱出成功！\n手数: {self.moves}")
            self.canvas.move(tag, 0, self.size)

if __name__ == "__main__":
    root = tk.Tk()
    HakoiriMusume(root)
    root.mainloop()
