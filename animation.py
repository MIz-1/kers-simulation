import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ── Parameters ─────────────────────────────────────────────
m          = 1200
v0         = 30
F_engine   = 4000
F_brake    = 3000
efficiency = 0.85
battery_max= 400000
F_drag_c   = 0.5 * 1.225 * 0.30 * 2.2

dt = 0.01
t  = np.arange(0, 60, dt)

def get_phase(time):
    if   0  <= time < 10: return "accelerate"
    elif 10 <= time < 20: return "brake"
    elif 20 <= time < 30: return "accelerate"
    elif 30 <= time < 40: return "brake"
    else:                 return "accelerate"

# ── Simulation ─────────────────────────────────────────────
v_log, battery_log, boost_log = [], [], []
v       = v0
battery = 0.0

for i in range(len(t)):
    phase  = get_phase(t[i])
    F_drag = F_drag_c * v**2

    if phase == "brake" and v > 0:
        P_recovered = F_brake * v
        battery     = min(battery + P_recovered * dt * efficiency, battery_max)
        F_boost     = 0
        F_net       = -F_brake - F_drag
    elif phase == "accelerate":
        if battery > 0 and v > 0.1:
            F_boost = min(battery / (v * dt), 2000)
            battery = max(battery - F_boost * v * dt, 0)
        else:
            F_boost = 0
        F_net = F_engine + F_boost - F_drag
    else:
        F_boost = 0
        F_net   = -F_drag

    a = F_net / m
    v = max(v + a * dt, 0)

    v_log.append(v)
    battery_log.append(battery / 1000)
    boost_log.append(F_boost)

# ── Animation ──────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 8), facecolor='#0a0a0a')
fig.suptitle('KERS — Kinetic Energy Recovery System',
             color='white', fontsize=13, fontweight='bold')

for ax in axes:
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white', labelsize=7)
    ax.set_xlim(0, t[-1])
    ax.grid(True, alpha=0.2, color='#333333')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

axes[0].set_title('VEHICLE SPEED (m/s)', color='#4fc3f7', fontsize=9, fontweight='bold')
axes[0].set_ylim(0, max(v_log) * 1.2)

axes[1].set_title('BATTERY CHARGE (kJ)', color='#66bb6a', fontsize=9, fontweight='bold')
axes[1].set_ylim(0, max(battery_log) * 1.2 + 1)

axes[2].set_title('KERS BOOST FORCE (N)', color='#ffa726', fontsize=9, fontweight='bold')
axes[2].set_ylim(0, 2500)

line_speed,   = axes[0].plot([], [], color='#4fc3f7', lw=2)
line_battery, = axes[1].plot([], [], color='#66bb6a', lw=2)
line_boost,   = axes[2].plot([], [], color='#ffa726', lw=2)

time_text  = axes[0].text(0.02, 0.85, '', transform=axes[0].transAxes,
                           color='white', fontsize=9)
phase_text = axes[0].text(0.60, 0.85, '', transform=axes[0].transAxes,
                           color='yellow', fontsize=9, fontweight='bold')

plt.tight_layout()

STEP = 10

def update(frame):
    i = min(frame * STEP, len(t) - 1)
    x = t[:i]

    line_speed.set_data(x, v_log[:i])
    line_battery.set_data(x, battery_log[:i])
    line_boost.set_data(x, boost_log[:i])

    phase = get_phase(t[i])
    phase_label = {"accelerate": "ACCELERATING", "brake": "BRAKING"}
    time_text.set_text(f't = {t[i]:.1f}s')
    phase_text.set_text(phase_label.get(phase, ""))

    return [line_speed, line_battery, line_boost, time_text, phase_text]

frames = len(t) // STEP
ani = animation.FuncAnimation(fig, update, frames=frames, interval=30, blit=True)

print("Saving GIF...")
ani.save('kers_animation.gif', writer='pillow', fps=20)
print("Done! kers_animation.gif saved!")

plt.show()