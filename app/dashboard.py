import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import time
import sys, os

# Ensure the root directory is in the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.simulation import Simulation
from simulation.config import MAX_STEPS, NUM_AGENTS

st.set_page_config(
    page_title="CAR-MuSC Instrument",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Initialisation ─────────────────────────────────────────────
if 'sim' not in st.session_state:
    st.session_state.sim = Simulation(seed=0)
    st.session_state.playing = False
    st.session_state.prev_counts = None
    st.session_state.multirun_results = None

# ── Helper: Draw Grid Function ───────────────────────────────────────────────
def draw_grid(agents, damage, hgf, injury_mask, title):
    """
    Render a single population grid with damage background and agent overlays.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 1. Damage background (RdYlGn_r: Red=High, Green=Low)
    ax.imshow(damage.T, origin='lower', cmap='RdYlGn_r', alpha=0.9, interpolation='nearest')
    
    # 2. HGF Gradient overlay (low alpha Blues)
    ax.imshow(hgf.T, origin='lower', cmap='Blues', alpha=0.2, interpolation='bilinear')
    
    # 3. Injury boundary contour
    ax.contour(injury_mask.T.astype(float), levels=[0.5], colors='cyan', linewidths=1.5, linestyles='--')
    
    # 4. Agent scatter
    # States: 0=migrating (white), 2=engrafted (cyan), -1=failed (red)
    mig_x, mig_y = [], []
    eng_x, eng_y = [], []
    fai_x, fai_y = [], []
    
    for a in agents:
        if a.state == 0:
            mig_x.append(a.x); mig_y.append(a.y)
        elif a.state == 2:
            eng_x.append(a.x); eng_y.append(a.y)
        else:
            fai_x.append(a.x); fai_y.append(a.y)
            
    ax.scatter(mig_x, mig_y, color='white', s=8,  label='Migrating', edgecolors='black', linewidth=0.3)
    ax.scatter(eng_x, eng_y, color='cyan',  s=12, label='Engrafted', edgecolors='black', linewidth=0.5)
    ax.scatter(fai_x, fai_y, color='red',   s=6,  label='Failed')
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])
    
    # Legend
    white_patch = mpatches.Patch(color='white', label='Migrating')
    cyan_patch  = mpatches.Patch(color='cyan',  label='Engrafted')
    red_patch   = mpatches.Patch(color='red',   label='Failed')
    ax.legend(handles=[white_patch, cyan_patch, red_patch], loc='upper right', fontsize=8, framealpha=0.6)
    
    return fig

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("CAR-MuSC Computational Instrument")
st.caption("Real-time visual validation of CAR-receptor noise reduction in muscle stem cell recruitment.")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Instrument Controls")
    
    seed = st.number_input("RNG Seed", min_value=0, max_value=100, value=st.session_state.sim.seed)
    
    # Reset Logic
    if st.button("Reset Simulation"):
        st.session_state.sim = Simulation(seed=seed)
        st.session_state.playing = False
        st.session_state.prev_counts = None
        st.rerun()
        
    # Play/Pause Logic
    if st.session_state.playing:
        if st.button("⏸ Pause"):
            st.session_state.playing = False
            st.rerun()
    else:
        if st.button("▶ Play"):
            st.session_state.playing = True
            st.rerun()
            
    st.write(f"**Step:** {st.session_state.sim.current_step} / {MAX_STEPS}")
    
    st.divider()
    
    # Multi-run Trigger
    if st.button("Run Multi-Run Analysis"):
        with st.spinner("Running 10 simulations..."):
            all_results = []
            for i in range(10):
                m_sim = Simulation(seed=i)
                m_sim.run(MAX_STEPS)
                res = m_sim.get_metrics()
                all_results.append({
                    'Run': i,
                    'CAR Targeting%': res['car_targeting_index'],
                    'Unmod Targeting%': res['unmod_targeting_index'],
                    'CAR Advantage': res['car_targeting_index'] - res['unmod_targeting_index']
                })
            
            df = pd.DataFrame(all_results)
            st.session_state.multirun_results = {
                'df': df,
                'car_mean': df['CAR Targeting%'].mean(),
                'car_std':  df['CAR Targeting%'].std(),
                'unmod_mean': df['Unmod Targeting%'].mean(),
                'unmod_std':  df['Unmod Targeting%'].std(),
                'car_wins': (df['CAR Targeting%'] > df['Unmod Targeting%']).sum()
            }
        st.rerun()

# ── SECTION 1: SIDE-BY-SIDE ANIMATED GRIDS ──────────────────────────────────
st.subheader("Population Navigation & Engraftment")

col1, col2 = st.columns(2)

sim = st.session_state.sim

with col1:
    fig_unmod = draw_grid(sim.unmod_agents, sim.damage_unmod, sim.hgf_grid, sim.injury_mask, 
                          f"Unmodified MuSC (Step {sim.current_step})")
    st.pyplot(fig_unmod)
    plt.close(fig_unmod)

with col2:
    fig_car = draw_grid(sim.car_agents, sim.damage_car, sim.hgf_grid, sim.injury_mask, 
                        f"CAR-MuSC (Step {sim.current_step})")
    st.pyplot(fig_car)
    plt.close(fig_car)

# ── SECTION 2: STATE COUNTERS ───────────────────────────────────────────────
st.divider()
st.subheader("Real-Time Instrumentation Metrics")

# Current counts
def get_counts(agents):
    c = {0: 0, 2: 0, -1: 0}
    for a in agents:
        if a.state in c:
            c[a.state] += 1
    return c

u_counts = get_counts(sim.unmod_agents)
c_counts = get_counts(sim.car_agents)

# Delta calculation
if st.session_state.prev_counts is None:
    u_deltas = {0:0, 2:0, -1:0}
    c_deltas = {0:0, 2:0, -1:0}
else:
    pc = st.session_state.prev_counts
    u_deltas = {k: u_counts[k] - pc['u'][k] for k in u_counts}
    c_deltas = {k: c_counts[k] - pc['c'][k] for k in c_counts}

# Unmodified Row
st.caption("**Unmodified MuSC (σ=0.4)**")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Migrating", u_counts[0], delta=u_deltas[0])
m2.metric("Engrafted", u_counts[2], delta=u_deltas[2])
m3.metric("Failed", u_counts[-1], delta=u_deltas[-1])
m4.metric("Targeting%", f"{u_counts[2]/NUM_AGENTS*100:.1f}%")

# CAR-MuSC Row
st.caption("**CAR-MuSC (σ=0.2)**")
m5, m6, m7, m8 = st.columns(4)
m5.metric("Migrating", c_counts[0], delta=c_deltas[0])
m6.metric("Engrafted", c_counts[2], delta=c_deltas[2])
m7.metric("Failed", c_counts[-1], delta=c_deltas[-1])
m8.metric("Targeting%", f"{c_counts[2]/NUM_AGENTS*100:.1f}%")

# Save for next delta
st.session_state.prev_counts = {'u': u_counts, 'c': c_counts}

# ── SECTION 3: REPAIR CURVES ────────────────────────────────────────────────
if len(sim.history) >= 2:
    st.divider()
    st.subheader("Targeting Performance")
    
    steps = [h['step'] for h in sim.history]
    u_ti  = [h['unmod_engrafted']/NUM_AGENTS*100 for h in sim.history]
    c_ti  = [h['car_engrafted']/NUM_AGENTS*100 for h in sim.history]
    
    fig_curve, ax_curve = plt.subplots(figsize=(10, 4))
    ax_curve.plot(steps, u_ti, color='#e07070', label='Unmodified MuSC (σ=0.4)', linewidth=2)
    ax_curve.plot(steps, c_ti, color='#70a8e0', label='CAR-MuSC (σ=0.2)', linewidth=2)
    ax_curve.fill_between(steps, u_ti, c_ti, color='grey', alpha=0.15)
    
    ax_curve.axhline(40, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
    ax_curve.axhline(80, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
    
    ax_curve.set_xlabel("Simulation Step")
    ax_curve.set_ylabel("Targeting Index (%)")
    ax_curve.set_title("Targeting Index Over Time — CAR vs Unmodified")
    ax_curve.set_ylim(0, 100)
    ax_curve.legend(loc='upper left')
    
    st.pyplot(fig_curve)
    plt.close(fig_curve)
    
    # Summary Metrics
    current_metrics = sim.get_metrics()
    c1, c2, c3 = st.columns(3)
    c1.metric("CAR Targeting", f"{current_metrics['car_targeting_index']:.1f}%")
    c2.metric("Unmod Targeting", f"{current_metrics['unmod_targeting_index']:.1f}%")
    adv = current_metrics['car_targeting_index'] - current_metrics['unmod_targeting_index']
    c3.metric("CAR Advantage", f"{adv:+.1f}pp", delta=f"{adv:+.1f}pp")

# ── SECTION 4: MULTI-RUN ANALYSIS ───────────────────────────────────────────
if st.session_state.multirun_results is not None:
    st.divider()
    st.subheader("Multi-Run Statistical Analysis")
    
    res = st.session_state.multirun_results
    df = res['df']
    
    # 1. Bar chart with error bars
    fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
    labels = ['Unmodified', 'CAR-MuSC']
    means  = [res['unmod_mean'], res['car_mean']]
    stds   = [res['unmod_std'],  res['car_std']]
    
    bars = ax_bar.bar(labels, means, yerr=stds, color=['#e07070', '#70a8e0'], 
                      edgecolor='black', capsize=10, width=0.5)
    
    ax_bar.set_ylim(0, 100)
    ax_bar.set_ylabel("Mean Targeting Index (%)")
    ax_bar.set_title("Multi-Run Analysis — 10 Independent Simulations")
    ax_bar.axhline(40, color='grey', linestyle='--', alpha=0.5)
    ax_bar.axhline(80, color='grey', linestyle='--', alpha=0.5)
    
    # Annotate effect size
    effect_size = res['car_mean'] - res['unmod_mean']
    ax_bar.text(0.5, 90, f"Effect size: {effect_size:+.1f}pp", ha='center', 
                fontsize=12, fontweight='bold', color='#1a5276')
    
    st.pyplot(fig_bar)
    plt.close(fig_bar)
    
    # 2. Results metrics
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("CAR wins", f"{res['car_wins']} / 10 runs")
    mc2.metric("Mean CAR", f"{res['car_mean']:.1f}%")
    mc3.metric("Mean Unmod", f"{res['unmod_mean']:.1f}%")
    
    # 3. Dataframe with highlighting
    def highlight_car_win(row):
        color = 'background-color: rgba(112, 168, 224, 0.2)' if row['CAR Targeting%'] > row['Unmod Targeting%'] else ''
        return [color] * len(row)

    st.caption("Per-Run Data (Highlight: CAR Wins)")
    st.dataframe(df.style.apply(highlight_car_win, axis=1).format("{:.1f}", subset=['CAR Targeting%', 'Unmod Targeting%', 'CAR Advantage']))

# ── Animation Loop ──────────────────────────────────────────────────────────
if st.session_state.playing and sim.current_step < MAX_STEPS:
    sim.step()
    time.sleep(0.05)
    st.rerun()
elif sim.current_step >= MAX_STEPS:
    st.session_state.playing = False
