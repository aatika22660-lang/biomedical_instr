import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Ellipse
from matplotlib.gridspec import GridSpec

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 10,
})

BLUE   = '#1976D2'
AMBER  = '#FFC107' # Matching biophysics
ORANGE = '#F4511E'
TEAL   = '#00897B'
GREY   = '#546E7A'
RED    = '#D32F2F'

LBLUE   = '#E3F2FD'
LAMBER  = '#FFF8E1'
LORANGE = '#FBE9E7'
LTEAL   = '#E0F2F1'
LGREY   = '#ECEFF1'
LPURP   = '#F3E5F5' # Kept for variety if needed

def box(ax,x,y,w,h,fc,ec,label,sub='',fontsize=10):
    r=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.15',
                     facecolor=fc,edgecolor=ec,linewidth=2.0,zorder=3)
    ax.add_patch(r)
    ax.text(x,y+(0.2 if sub else 0),label,ha='center',va='center',
            fontsize=fontsize,fontweight='bold',color=ec,zorder=4)
    if sub: ax.text(x,y-0.4,sub,ha='center',va='center',fontsize=fontsize-1.5,color='#333',zorder=4)

def arr(ax,x1,y1,x2,y2,col='#333',lw=2.0):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),
                arrowprops=dict(arrowstyle='->', color=col, lw=lw),zorder=5)

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 7), facecolor='white')
gs = GridSpec(1, 2, figure=fig, wspace=0.3, left=0.08, right=0.92, top=0.85, bottom=0.1)

ax_a = fig.add_subplot(gs[0, 0])
ax_c = fig.add_subplot(gs[0, 1])

for ax in [ax_a, ax_c]: ax.axis('off')

# ══════════════════════════════════════════════════════════════════════════════
# PANEL A — Noise Filter Circuit Diagram
# ══════════════════════════════════════════════════════════════════════════════
ax_a.set_xlim(0,10); ax_a.set_ylim(0,10)
ax_a.set_title('A   CAR Receptor Noise Filter', fontsize=14, fontweight='bold', loc='left', pad=20)

box(ax_a,2,8.0,3.2,1.2,LBLUE,BLUE,'HGF Signal','C(x,y)')
ax_a.text(5,9.3,'+ Noise',ha='center',va='center',fontsize=10,color=RED,fontweight='bold')
ax_a.annotate('',xy=(5,8.5),xytext=(5,9.1), arrowprops=dict(arrowstyle='->',color=RED,lw=1.5))
circ=Circle((5,8.0),0.6,facecolor='white',edgecolor='#333',linewidth=2.0,zorder=3)
ax_a.add_patch(circ)
ax_a.text(5,8.0,'⊕',ha='center',va='center',fontsize=16,color='#333',zorder=4)
box(ax_a,5,6.0,3.5,1.2,LAMBER,AMBER,'CAR Receptor','σ: 0.4 → 0.2')
box(ax_a,5,3.5,3.5,1.2,LTEAL,TEAL,'Directed Nav.','σ_CAR = 0.2')
arr(ax_a,3.6,8.0,4.4,8.0,BLUE)
arr(ax_a,5,7.4,5,6.6,AMBER)
arr(ax_a,5,5.4,5,4.1,TEAL)

# ══════════════════════════════════════════════════════════════════════════════
# PANEL B — Agent State Machine
# ══════════════════════════════════════════════════════════════════════════════
ax_c.set_xlim(0,10); ax_c.set_ylim(0,10)
ax_c.set_title('B   Agent State Machine', fontsize=14, fontweight='bold', loc='left', pad=20)
states=[(5,8.2,BLUE,'State 0\nMigrating'),(5,5.0,AMBER,'Threshold\nCheck'),(2.2,1.8,RED,'State −1\nFailed'),(7.8,1.8,TEAL,'State 2\nEngrafted')]
for x,y,col,lab in states:
    c=Circle((x,y),1.2,facecolor='white',edgecolor=col,linewidth=2.5,zorder=3)
    ax_c.add_patch(c)
    ax_c.text(x,y,lab,ha='center',va='center',fontsize=9,fontweight='bold',color=col)

arr(ax_c,5,7.0,5,6.2,AMBER)
arr(ax_c,4.0,4.2,3.0,3.0,RED)
arr(ax_c,6.0,4.2,7.0,3.0,TEAL)

# Parameter annotation
ax_c.text(6.5, 5.0, r'$C_{thresh} = 0.5$', fontsize=10, color=AMBER, fontweight='bold', va='center')

# G removed as requested.

fig.text(0.5, 0.04, 'CAR-MuSC Simulation System Architecture', 
         fontsize=12, ha='center', color='#555', fontweight='normal', style='italic')

out='/Users/aatikashaikh/Desktop/CAR_MuSC/report/figures/architecture_fig.png'
plt.savefig(out,dpi=200,bbox_inches='tight')
print(f'Saved to {out}')
