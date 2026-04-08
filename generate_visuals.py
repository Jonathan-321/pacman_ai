"""
Generate visuals for pacman_ai README.
Renders the actual LEVEL_1 maze from the codebase with pathfinding visualization.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
import os

BG = '#0d1117'
CARD = '#161b22'
BORDER = '#30363d'
ACCENT = '#58a6ff'
TEXT = '#e6edf3'
MUTED = '#8b949e'
GREEN = '#3fb950'
PURPLE = '#bc8cff'
ORANGE = '#f0883e'
YELLOW = '#d29922'
RED = '#f85149'
PINK = '#f778ba'

plt.rcParams.update({
    'figure.facecolor': BG, 'text.color': TEXT, 'font.family': 'DejaVu Sans',
})

out = '/home/user/workspace/pacman_ai/assets/visuals'
os.makedirs(out, exist_ok=True)

# Actual LEVEL_1 from src/config/maze_layouts.py
LEVEL_1 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W........W..........",
    "W.WW.WWW.W.WWW.WW.W.",
    "WoW....GG........oW.",
    "W.W.WW.WWWW.WW.W.W..",
    "W.....W....W.....W..",
    "W.WWW.WWWW.WWW.W.W..",
    "W.WWW.W....WWW.W.W..",
    "W.....W..........W..",
    "W.WWW.WSSSW.WWW.W...",
    "W.....W....W.....W..",
    "W.W.WW.WWWW.WW.W.W..",
    "WoW....GG.....W..oW.",
    "W.WW.WWW.W.WWW.WW.W.",
    "W........W..........",
    "WWWWWWWWWWWWWWWWWWW."
]

def make_hero():
    rows = len(LEVEL_1)
    cols = max(len(r) for r in LEVEL_1)
    
    fig = plt.figure(figsize=(14, 6), facecolor=BG)
    gs = fig.add_gridspec(1, 2, left=0.02, right=0.98, top=0.88, bottom=0.05,
                          wspace=0.08, width_ratios=[1.2, 1])
    
    fig.text(0.5, 0.97, 'Pacman AI', fontsize=26, fontweight='bold', color=YELLOW, ha='center', va='top')
    fig.text(0.5, 0.91, 'AI-Driven Pacman with A* / BFS / DFS Pathfinding & Ghost AI',
             fontsize=10, color=MUTED, ha='center', va='top')
    
    # Left: Render the actual maze
    ax = fig.add_subplot(gs[0, 0])
    ax.set_facecolor('#000011')
    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(rows - 0.5, -0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    wall_color = '#1a1a6e'
    pellet_color = '#ffcc00'
    power_color = '#ffffff'
    
    for r in range(rows):
        for c in range(len(LEVEL_1[r])):
            ch = LEVEL_1[r][c]
            if ch == 'W':
                ax.add_patch(plt.Rectangle((c - 0.45, r - 0.45), 0.9, 0.9,
                            facecolor=wall_color, edgecolor='#2828a0', linewidth=0.5))
            elif ch == '.':
                ax.add_patch(Circle((c, r), 0.08, facecolor=pellet_color, edgecolor='none'))
            elif ch == 'o':
                ax.add_patch(Circle((c, r), 0.2, facecolor=power_color, edgecolor='none', alpha=0.9))
            elif ch == 'S':
                ax.add_patch(Circle((c, r), 0.35, facecolor=YELLOW, edgecolor='none'))
            elif ch == 'G':
                ghost_colors = [RED, PINK, '#00ffff', ORANGE]
                gi = sum(1 for rr in range(r) for cc in range(len(LEVEL_1[rr])) if LEVEL_1[rr][cc] == 'G')
                gcolor = ghost_colors[gi % 4]
                ax.add_patch(Circle((c, r), 0.35, facecolor=gcolor, edgecolor='none', alpha=0.8))
    
    # Simulated A* path overlay
    astar_path = [(8, 9), (8, 8), (7, 8), (6, 8), (5, 8), (5, 7), (5, 6), (5, 5),
                  (4, 5), (3, 5), (3, 4), (3, 3)]
    for i, (c, r) in enumerate(astar_path):
        alpha = 0.3 + 0.5 * (i / len(astar_path))
        ax.add_patch(plt.Rectangle((c - 0.3, r - 0.3), 0.6, 0.6,
                    facecolor=GREEN, alpha=alpha * 0.3, edgecolor='none'))
    
    # Path line
    if len(astar_path) > 1:
        px = [p[0] for p in astar_path]
        py = [p[1] for p in astar_path]
        ax.plot(px, py, color=GREEN, linewidth=2, alpha=0.6, zorder=5)
    
    ax.text(cols/2, -1.2, 'Level 1 Maze with A* Path', fontsize=9, color=GREEN,
            ha='center', va='center')
    
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    
    # Right: Algorithm comparison & Ghost AI info
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_xlim(0, 6)
    ax2.set_ylim(0, 8)
    ax2.set_facecolor(BG)
    ax2.axis('off')
    
    # Pathfinding algorithms
    ax2.text(3, 7.5, 'Search Algorithms', fontsize=12, color=TEXT,
            ha='center', va='center', fontweight='bold')
    
    algos = [
        ('A* Search', 'Optimal path\nHeuristic: Manhattan', GREEN, 6.6),
        ('BFS', 'Shortest path\nLevel-order traversal', ACCENT, 5.4),
        ('DFS', 'Depth-first exploration\nStack-based', PURPLE, 4.2),
    ]
    for name, desc, color, y in algos:
        ax2.add_patch(FancyBboxPatch((0.2, y - 0.4), 5.5, 0.9,
                    boxstyle="round,pad=0.1", facecolor=CARD, edgecolor=color, linewidth=1.5))
        ax2.text(1.5, y + 0.05, name, fontsize=10, color=color,
                ha='center', va='center', fontweight='bold')
        ax2.text(4.0, y + 0.05, desc, fontsize=7, color=MUTED,
                ha='center', va='center', linespacing=1.3)
    
    # Ghost AI behaviors
    ax2.text(3, 3.2, 'Ghost AI Behaviors', fontsize=12, color=TEXT,
            ha='center', va='center', fontweight='bold')
    
    ghost_modes = [
        ('Chase', 'Pursue Pacman', RED),
        ('Scatter', 'Patrol corners', ORANGE),
        ('Frightened', 'Random movement', ACCENT),
    ]
    for i, (mode, desc, color) in enumerate(ghost_modes):
        bx = 0.3 + i * 1.95
        ax2.add_patch(FancyBboxPatch((bx, 2.0), 1.7, 0.8,
                    boxstyle="round,pad=0.08", facecolor=BG, edgecolor=color, linewidth=1.2))
        ax2.text(bx + 0.85, 2.55, mode, fontsize=8, color=color,
                ha='center', va='center', fontweight='bold')
        ax2.text(bx + 0.85, 2.25, desc, fontsize=6, color=MUTED,
                ha='center', va='center')
    
    # Features
    feats = ['Pygame rendering', 'Sound effects', 'Multiple levels', 'Score system']
    for i, f in enumerate(feats):
        fy = 1.2 - i * 0.3
        ax2.text(0.5, fy, '\u2022', fontsize=10, color=YELLOW, ha='center', va='center')
        ax2.text(0.8, fy, f, fontsize=7, color=MUTED, ha='left', va='center')
    
    fig.savefig(f'{out}/hero_banner.png', dpi=150, bbox_inches='tight',
                facecolor=BG, edgecolor='none')
    plt.close()
    print("\u2713 hero_banner.png")

if __name__ == '__main__':
    make_hero()
