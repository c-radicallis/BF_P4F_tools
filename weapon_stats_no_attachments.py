
from pathlib import Path
import re
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BATCH_MODE = False  # True = all .con files; False = single file

FILE = Path("LMG_M27IAR.con")
OUTPUT = FILE.stem + "_stats.png"

# --------------------------------------------------
# Parse .con file
# --------------------------------------------------
def parse_con(filename):
    text = filename.read_text(encoding="utf-8", errors="ignore")
    stats = {}
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        match = re.match(r"ObjectTemplate\.([\w.]+)\s+(.+)", line)
        if match:
            stats[match.group(1)] = match.group(2).strip()
    return stats

def get(key, default=None):
    return stats.get(key, default)

def number(key, default=0):
    try:
        return float(get(key, default))
    except (ValueError, TypeError):
        return default

def display(value):
    try:
        n = float(value)
        return str(int(n)) if n.is_integer() else f"{n:g}"
    except (ValueError, TypeError):
        return str(value) if value is not None else "N/A"


# --------------------------------------------------
# Create visual report
# --------------------------------------------------
def generate_report(FILE):
    stats = parse_con(FILE)

    def get(key, default=None):
        return stats.get(key, default)

    def number(key, default=0):
        try:
            return float(get(key, default))
        except (ValueError, TypeError):
            return default

    # --------------------------------------------------
    # Extract relevant parameters
    # --------------------------------------------------
    rpm = number("fire.roundsPerMinute")
    mag = number("ammo.magSize")
    mags = number("ammo.nrOfMags")
    reload = number("ammo.reloadTime")
    velocity = number("velocity")

    distances = [
        0,
        number("mediumDistance"),
        number("longDistance")]

    damage_min = [
        number("initialMinDamage"),
        number("mediumMinDamage"),
        number("longMinDamage")]

    damage_max = [
        number("initialMaxDamage"),
        number("mediumMaxDamage"),
        number("longMaxDamage")]

    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    fig.suptitle(FILE.stem.replace("_", " ") + " - Weapon Statistics",
                fontsize=18, fontweight="bold")

    # 1. Damage vs distance
    ax1 = fig.add_subplot(gs[0, 0])

    end_distance = max(40, distances[-1] * 1.3)
    x = distances + [end_distance]

    y_min = damage_min + [damage_min[-1]]
    y_max = damage_max + [damage_max[-1]]

    ax1.fill_between(x, y_min, y_max, step="post", alpha=0.2)
    ax1.step(x, y_max, where="post", label="Maximum damage", linewidth=2)
    ax1.step(x, y_min, where="post", label="Minimum damage", linewidth=2)

    ax1.set_title("Damage vs Distance")
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Damage")
    ax1.set_xlim(0, end_distance)
    ax1.set_ylim(bottom=0)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    for d, dmin, dmax in zip(distances, damage_min, damage_max):
        ax1.annotate(f"{dmin:g}–{dmax:g}", (d, dmax),
                    xytext=(5, 5), textcoords="offset points", fontsize=9)

    # 2. Main weapon statistics
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off")
    ax2.set_title("General Statistics")

    main_stats = [
        ("Fire rate", f"{display(rpm)} RPM"),
        ("Projectile velocity", f"{display(velocity)} m/s"),
        ("Magazine capacity", display(mag)),
        ("Number of magazines", display(mags)),
        ("Total ammunition", display(mag * mags)),
        ("Reload time", f"{display(reload)} s"),
        ("Time between shots", f"{60/rpm:.4f} s" if rpm else "N/A"),
    ]

    table = ax2.table(
        cellText=main_stats,
        colLabels=["Parameter", "Value"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.55, 0.4]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.7)

    # 3. Recoil parameters
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis("off")
    ax3.set_title("Recoil Characteristics")

    recoil_keys = [
        "recoil.hasRecoilForce",
        "recoil.goBackOnRecoil",
        "recoil.recoilForceUp",
        "recoil.recoilForceLeftRight",
        "recoil.recoilGraphFrameCount",
        "recoil.recoilGraphExponent",
        "recoil.recoilGraphTotalMovement",
        "recoil.zoomModifier",
    ]

    recoil_data = [(k.split(".")[-1], get(k, "N/A").replace("CRD_UNIFORM/", "")) for k in recoil_keys]

    table = ax3.table(
        cellText=recoil_data,
        colLabels=["Parameter", "Value"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.65, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.45)

    # 4. Accuracy / deviation parameters
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    ax4.set_title("Accuracy / Deviation Characteristics")

    deviation_keys = [
        "deviation.minDev",
        "deviation.subProjectileDev",
        "deviation.DevModZoom",
        "deviation.minDevModZoom",
        "deviation.setFireDev",
        "deviation.setTurnDev",
        "deviation.setSpeedDev",
        "deviation.setMiscDev",
        "deviation.devModStand",
        "deviation.devModCrouch",
        "deviation.syncDev",
    ]

    deviation_data = [
        (k.split(".")[-1], get(k, "N/A")) for k in deviation_keys
    ]

    table = ax4.table(
        cellText=deviation_data,
        colLabels=["Parameter", "Value"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.65, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    # --------------------------------------------------
    # Save and display
    # --------------------------------------------------
    OUTPUT = FILE.stem + "_stats.png"
    OUTPUT_DIR = Path("Weapon_Stats")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT = OUTPUT_DIR / (FILE.stem + "_stats.png")

    plt.savefig(OUTPUT, dpi=200, bbox_inches="tight")
    #plt.show()

    print(f"Statistics extracted from: {FILE}")
    print(f"Report saved to: {OUTPUT}")

# --------------------------------------------------
# Run
# --------------------------------------------------
if BATCH_MODE:
    files = sorted(Path(".").glob("*.con"))
else:
    files = [FILE]

if not files:
    print("No .con files found.")

for file in files:
    print(f"Processing {file.name}...")
    try:
        generate_report(file)
    except Exception as e:
        print(f"Error processing {file.name}: {e}")