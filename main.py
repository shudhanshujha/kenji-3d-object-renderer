import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import math
import time

class TankRenderer3D:
    def __init__(self, root):
        self.root = root
        self.root.title("Kenji 3D Object Renderer")
        self.root.geometry("1100x800")
        self.root.configure(bg='#020202')

        # --- High-Stability State ---
        self.angles = np.array([0.5, 0.8, 0.0], dtype=float)
        self.zoom_dist = 8.0
        self.last_mouse = np.array([0, 0])
        self.auto_rotate = True
        self.render_mode = "Solid" 
        self.show_axes = True
        self.last_time = time.time()
        
        # --- Engine Data ---
        self.verts = np.empty((0, 3), dtype=float)
        self.faces = [] 
        
        # Pre-generate Perfect Primitives (Reordered: Sphere and Donut at bottom)
        self.primitives = {
            "Cylinder": self.gen_cylinder(1.0, 2.5, 20),
            "Cone": self.gen_cone(1.2, 2.5, 20),
            "Cube": self.gen_cube(),
            "Prism": self.gen_prism(1.4, 2.0, 6),
            "Pyramid": self.gen_pyramid(),
            "Sphere": self.gen_sphere(1.5, 20, 20),
            "Donut": self.gen_torus(1.2, 0.5, 20, 20)
        }
        
        self.setup_ui()
        self.load_primitive("Sphere")
        self.render_loop()

    def setup_ui(self):
        self.sidebar = tk.Frame(self.root, bg='#0f0f0f', width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="3D STUDIO PRO", bg='#0f0f0f', fg='#00eaff', font=('Arial', 16, 'bold')).pack(pady=20)
        tk.Button(self.sidebar, text="📂 Upload .obj File", command=self.open_obj_file, bg='#005bb7', fg='white', font=('Arial', 10, 'bold'), relief=tk.FLAT).pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(self.sidebar, text="SHAPES", bg='#0f0f0f', fg='#555555', font=('Arial', 8, 'bold')).pack(pady=(10, 0))
        for name in self.primitives:
            tk.Button(self.sidebar, text=name, command=lambda n=name: self.load_primitive(n), bg='#1e1e1e', fg='white', relief=tk.FLAT).pack(fill=tk.X, padx=20, pady=2)

        tk.Label(self.sidebar, text="DISPLAY", bg='#0f0f0f', fg='#555555', font=('Arial', 8, 'bold')).pack(pady=(15, 0))
        for mode in ["Solid", "Wireframe", "Points"]:
            tk.Button(self.sidebar, text=mode, command=lambda m=mode: self.set_mode(m), bg='#1e1e1e', fg='white', relief=tk.FLAT).pack(fill=tk.X, padx=20, pady=2)

        self.axis_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.sidebar, text="Show Axis & Grid", variable=self.axis_var, bg='#0f0f0f', fg='white', selectcolor='#0f0f0f').pack(pady=10)
        
        tk.Button(self.sidebar, text="⏯ Pause / Play", command=self.toggle_spin, bg='#444444', fg='white', relief=tk.FLAT).pack(fill=tk.X, padx=20, pady=20)
        
        self.fps_label = tk.Label(self.sidebar, text="FPS: 0", bg='#0f0f0f', fg='#00ff00', font=('Courier New', 10))
        self.fps_label.pack(side=tk.BOTTOM, pady=10)

        self.canvas = tk.Canvas(self.root, bg='#020202', highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<B1-Motion>", self.rotate_mouse)
        self.canvas.bind("<Button-1>", self.save_mouse)
        self.canvas.bind("<MouseWheel>", self.zoom_mouse)

    # --- Robust Geometry Generators ---
    def gen_cube(self):
        v = np.array([[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1]], dtype=float)
        f = [([0,1,2,3],'#ff4d4d'), ([1,5,6,2],'#4dff4d'), ([5,6,7,4],'#4d4dff'), ([4,7,3,0],'#ffff4d'), ([2,3,7,6],'#ff4dff'), ([0,1,5,4],'#4dffff')]
        return v, f

    def gen_sphere(self, r, lats, lons):
        v, f = [], []
        for i in range(lats + 1):
            lat = np.pi * i / lats
            for j in range(lons):
                lon = 2 * np.pi * j / lons
                v.append([r * np.sin(lat) * np.cos(lon), r * np.cos(lat), r * np.sin(lat) * np.sin(lon)])
        for i in range(lats):
            for j in range(lons):
                p1, p2, p3, p4 = i*lons+j, i*lons+(j+1)%lons, (i+1)*lons+(j+1)%lons, (i+1)*lons+j
                f.append(([p1,p2,p3,p4], '#00aaff'))
        return np.array(v, dtype=float), f

    def gen_torus(self, R, r, rings, sides):
        v, f = [], []
        for i in range(rings):
            u = 2 * np.pi * i / rings
            for j in range(sides):
                v_ang = 2 * np.pi * j / sides
                v.append([(R + r * np.cos(v_ang)) * np.cos(u), (R + r * np.cos(v_ang)) * np.sin(u), r * np.sin(v_ang)])
        for i in range(rings):
            for j in range(sides):
                p1, p2, p3, p4 = i*sides+j, ((i+1)%rings)*sides+j, ((i+1)%rings)*sides+(j+1)%sides, i*sides+(j+1)%sides
                f.append(([p1,p2,p3,p4], '#ffaa00'))
        return np.array(v, dtype=float), f

    def gen_cylinder(self, r, h, sides):
        v, f = [], []
        for i in range(sides):
            a = 2 * np.pi * i / sides
            x, z = r * np.cos(a), r * np.sin(a)
            v.extend([[x, h/2, z], [x, -h/2, z]])
        for i in range(sides):
            p1, p2, p3, p4 = i*2, (i*2+2)%(sides*2), (i*2+3)%(sides*2), i*2+1
            f.append(([p1,p2,p3,p4], '#ff4dff'))
        f.append(([i*2 for i in range(sides)], '#ff4dff'))
        f.append(([i*2+1 for i in range(sides)], '#ff4dff'))
        return np.array(v, dtype=float), f

    def gen_cone(self, r, h, sides):
        v, f = [[0, h/2, 0]], []
        for i in range(sides):
            a = 2 * np.pi * i / sides
            v.append([r * np.cos(a), -h/2, r * np.sin(a)])
        for i in range(1, sides + 1):
            f.append(([0, i, (i % sides) + 1], '#00ffff'))
        f.append(([i for i in range(1, sides+1)], '#00ffff'))
        return np.array(v, dtype=float), f

    def gen_prism(self, r, h, sides):
        v, f = [], []
        for i in range(sides):
            a = 2 * np.pi * i / sides
            v.extend([[r*np.cos(a), h/2, r*np.sin(a)], [r*np.cos(a), -h/2, r*np.sin(a)]])
        for i in range(sides):
            p1, p2, p3, p4 = i*2, (i*2+2)%(sides*2), (i*2+3)%(sides*2), i*2+1
            f.append(([p1,p2,p3,p4], '#00ffaa'))
        f.append(([i*2 for i in range(sides)], '#00ffaa'))
        f.append(([i*2+1 for i in range(sides)], '#00ffaa'))
        return np.array(v, dtype=float), f

    def gen_pyramid(self):
        v = np.array([[0,1.5,0], [-1,-1,1], [1,-1,1], [1,-1,-1], [-1,-1,-1]], dtype=float)
        f = [([0,1,2], '#ff4d4d'), ([0,2,3], '#4dff4d'), ([0,3,4], '#4d4dff'), ([0,4,1], '#ffff4d'), ([1,2,3,4], '#666666')]
        return v, f

    # --- Engine Mechanics ---
    def load_primitive(self, name): self.verts, self.faces = self.primitives[name]
    def set_mode(self, m): self.render_mode = m
    def toggle_spin(self): self.auto_rotate = not self.auto_rotate
    def save_mouse(self, e): self.last_mouse = np.array([e.x, e.y])
    def rotate_mouse(self, e):
        curr = np.array([e.x, e.y]); self.angles[1] += (curr[0] - self.last_mouse[0]) * 0.01; self.angles[0] += (curr[1] - self.last_mouse[1]) * 0.01
        self.last_mouse = curr; self.auto_rotate = False

    def zoom_mouse(self, e): self.zoom_dist = np.clip(self.zoom_dist - (0.5 if e.delta > 0 else -0.5), 2, 80)

    def open_obj_file(self):
        path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])
        if not path: return
        try:
            v, f = [], []
            with open(path, 'r') as file:
                for line in file:
                    if line.startswith('v '): v.append([float(x) for x in line.split()[1:4]])
                    elif line.startswith('f '):
                        idx = [int(p.split('/')[0]) - 1 for p in line.split()[1:]]
                        f.append((idx, '#007acc'))
            self.verts = np.array(v, dtype=float); self.verts -= self.verts.mean(axis=0)
            mx = np.abs(self.verts).max()
            if mx > 0: self.verts = (self.verts / mx) * 3.0
            self.faces = f
        except Exception as e: messagebox.showerror("Error", str(e))

    def render_loop(self):
        now = time.time(); dt = now - self.last_time; self.last_time = now
        self.canvas.delete("all")
        if len(self.verts) == 0: return

        # 1. Full-Resolution Transformation
        if self.auto_rotate: self.angles += [0.5 * dt, 0.8 * dt, 0.2 * dt]
        
        ax, ay, az = self.angles
        Rx = np.array([[1,0,0],[0,np.cos(ax),-np.sin(ax)],[0,np.sin(ax),np.cos(ax)]])
        Ry = np.array([[np.cos(ay),0,np.sin(ay)],[0,1,0],[-np.sin(ay),0,np.cos(ay)]])
        Rz = np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]])
        R = Rz @ Ry @ Rx
        rv = self.verts @ R.T
        
        zo = rv[:, 2] + self.zoom_dist; zo[zo < 0.1] = 0.1; f_vals = 900 / zo
        proj = np.stack((rv[:, 0] * f_vals + 450, -rv[:, 1] * f_vals + 400), axis=1)

        # 2. Grid & Axis Background
        if self.axis_var.get():
            for i in range(-5, 6):
                p1, p2 = self.proj_m(R, i, -2.5, -5), self.proj_m(R, i, -2.5, 5)
                p3, p4 = self.proj_m(R, -5, -2.5, i), self.proj_m(R, 5, -2.5, i)
                self.canvas.create_line(p1, p2, fill='#111111'); self.canvas.create_line(p3, p4, fill='#111111')
            for v_ax, lbl, cl in [([3,0,0],'X','#ff4444'), ([0,3,0],'Y','#44ff44'), ([0,0,3],'Z','#4444ff')]:
                o, e = self.proj_m(R, 0,0,0), self.proj_m(R, *v_ax)
                self.canvas.create_line(o, e, fill=cl, arrow=tk.LAST, width=2)
                self.canvas.create_text(e[0]+10, e[1], text=lbl, fill=cl, font=('Arial', 10, 'bold'))

        # 3. Robust Rendering (No Skipping)
        draw_list = []
        for idx, base_color in self.faces:
            if len(idx) < 3: continue
            points = rv[idx]
            # Normal for lighting ONLY
            norm = np.cross(points[1] - points[0], points[2] - points[0])
            br = max(0.2, min(1.0, (norm[2] / (np.linalg.norm(norm) + 1e-6) * -1 + 1) / 2))
            draw_list.append((points[:, 2].mean(), proj[idx].flatten().tolist(), self.shade(base_color, br)))

        # Painter's Algorithm Sorting
        for _, pts, col in sorted(draw_list, key=lambda x: x[0], reverse=True):
            if self.render_mode == "Solid": self.canvas.create_polygon(pts, fill=col, outline='#ffffff', width=0.1)
            elif self.render_mode == "Wireframe": self.canvas.create_polygon(pts, fill='', outline=col)
            else: [self.canvas.create_oval(pts[j]-1, pts[j+1]-1, pts[j]+1, pts[j+1]+1, fill='white') for j in range(0, len(pts), 2)]

        self.fps_label.config(text=f"FPS: {int(1/dt if dt > 0 else 0)}")
        self.root.after(1, self.render_loop)

    def proj_m(self, R, x, y, z):
        p = np.array([x, y, z]) @ R.T; f = 900 / (p[2] + self.zoom_dist); return p[0] * f + 450, -p[1] * f + 400

    def shade(self, hex_c, br):
        if not hex_c.startswith('#'): return hex_c
        r, g, b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
        return f'#{int(r*br):02x}{int(g*br):02x}{int(b*br):02x}'

if __name__ == "__main__":
    root = tk.Tk(); root.attributes('-topmost', True); root.focus_force(); app = TankRenderer3D(root); root.mainloop()
