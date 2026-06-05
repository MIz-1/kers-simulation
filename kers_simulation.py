import numpy as np
import matplotlib.pyplot as plt

# ── Vehicle Parameters ─────────────────────────────────────
m          = 1200      # Car mass (kg)
v0         = 30        # Initial speed (m/s) = 108 km/h
F_brake    = 3000      # Braking force (N)
F_engine   = 4000      # Engine driving force (N)
F_drag     = 0.5       # Drag coefficient (simplified)
efficiency = 0.85      # KERS energy capture efficiency
battery    = 0.0       # Battery starts empty (Joules)
battery_max= 400000    # Max battery capacity (Joules)

# ── Time Setup ─────────────────────────────────────────────
dt = 0.01             # Time step (seconds)
t  = np.arange(0, 60, dt)   # 60 second simulation

# ── Drive Cycle ────────────────────────────────────────────
# 0-10s   : Accelerating
# 10-20s  : Braking (KERS capturing energy)
# 20-30s  : Accelerating (KERS giving boost)
# 30-40s  : Braking again
# 40-60s  : Accelerating with KERS boost

def get_phase(time):
    if   0  <= time < 10: return "accelerate"
    elif 10 <= time < 20: return "brake"
    elif 20 <= time < 30: return "accelerate"
    elif 30 <= time < 40: return "brake"
    else:                 return "accelerate"

# ── Storage Arrays ─────────────────────────────────────────
v_log         = []   # velocity
battery_log   = []   # battery charge
boost_log     = []   # KERS boost force
energy_log    = []   # kinetic energy
phase_log     = []   # drive phase

# ── Initial State ──────────────────────────────────────────
v       = v0
battery = 0.0

# ── Simulation Loop ────────────────────────────────────────
for i in range(len(t)):
    phase = get_phase(t[i])

    KE      = 0.5 * m * v**2        # Kinetic energy
    F_drag_actual = F_drag * v**2   # Drag force

    if phase == "brake" and v > 0:
        # ── KERS capturing energy ──────────────────────────
        P_recovered = F_brake * v                    # Power from braking
        E_captured  = P_recovered * dt * efficiency  # Energy captured
        battery     = min(battery + E_captured, battery_max)

        # Net force during braking
        F_net = -F_brake - F_drag_actual
        F_boost = 0

    elif phase == "accelerate":
        # ── KERS giving boost ──────────────────────────────
        if battery > 0 and v > 0.1:
            F_boost     = min(battery / (v * dt), 2000)   # Boost force (max 2000N)
            E_used      = F_boost * v * dt                 # Energy used
            battery     = max(battery - E_used, 0)
        else:
            F_boost = 0

        F_net = F_engine + F_boost - F_drag_actual
    else:
        F_boost = 0
        F_net   = -F_drag_actual

    # ── Update velocity (Newton's 2nd Law) ─────────────────
    a = F_net / m
    v = max(v + a * dt, 0)   # velocity can't go below 0

    # ── Log Data ───────────────────────────────────────────
    v_log.append(v)
    battery_log.append(battery / 1000)    # convert to kJ
    boost_log.append(F_boost)
    energy_log.append(KE / 1000)          # convert to kJ
    phase_log.append(phase)

# ── Plot Results ───────────────────────────────────────────
plt.figure(figsize=(12, 12))

# Panel 1 — Vehicle Speed
plt.subplot(4, 1, 1)
plt.plot(t, v_log, color='blue', label='Vehicle Speed')
plt.ylabel('Speed (m/s)')
plt.legend()
plt.grid(True)

# Phase background colors
for ax in plt.gcf().get_axes():
    for i in range(len(t)):
        if phase_log[i] == "brake":
            ax.axvspan(t[i], t[i]+dt, alpha=0.05, color='red')

# Panel 2 — Battery Charge
plt.subplot(4, 1, 2)
plt.plot(t, battery_log, color='green', label='Battery Charge')
plt.ylabel('Energy (kJ)')
plt.legend()
plt.grid(True)

# Panel 3 — KERS Boost Force
plt.subplot(4, 1, 3)
plt.plot(t, boost_log, color='orange', label='KERS Boost Force')
plt.ylabel('Force (N)')
plt.legend()
plt.grid(True)

# Panel 4 — Kinetic Energy
plt.subplot(4, 1, 4)
plt.plot(t, energy_log, color='red', label='Kinetic Energy')
plt.ylabel('Energy (kJ)')
plt.xlabel('Time (s)')
plt.legend()
plt.grid(True)

plt.suptitle('KERS — Kinetic Energy Recovery System Simulation')
plt.tight_layout()
plt.savefig('kers_simulation.png')
plt.show()

print("KERS Simulation complete! Graph saved as kers_simulation.png")

# ── Final Stats ────────────────────────────────────────────
print(f"\n── Final Stats ──")
print(f"Max Speed Reached  : {max(v_log):.2f} m/s ({max(v_log)*3.6:.1f} km/h)")
print(f"Max Battery Stored : {max(battery_log):.2f} kJ")
print(f"Max KERS Boost     : {max(boost_log):.2f} N")