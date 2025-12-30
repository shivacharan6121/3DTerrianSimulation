```markdown
# Missile Engagement 3D Visualizer

A high-fidelity 3D visualization tool for missile-target engagement scenarios. This project uses **PyVista** for rendering, **Trimesh** for 3D model handling, and **VTK** for procedural terrain generation. It transforms raw trajectory data (CSV) into a cinematic 3D animation.

## ✨ Features

* **Interactive 3D Scene:** Full orbit, zoom, and pan capabilities during playback.
* **Procedural Mountains:** Generates a unique terrain landscape using Perlin noise based on the data's spatial bounds.
* **Real-time HUD:** On-screen display showing coordinates, speed (m/s), heading (deg), and separation distance.
* **Dynamic Orientation:** Automatically calculates pitch and yaw from velocity vectors to ensure models align with their flight path.
* **Automated Recording:** Export your simulation directly to an `.mp4` video file.

---

## 🛠️ Installation

Ensure you have Python 3.8+ installed. You can install the required dependencies via pip:

```bash
pip install numpy pandas trimesh pyvista pyyaml PyQt5 vtk

```

*Note: `PyQt5` serves as the GUI backend for the PyVista plotter window.*

---

## 📁 Project Structure

The script expects the following directory structure for assets:

```text
.
├── missile_sim.py        # The main script
├── missile/
│   └── scene.gltf        # Missile 3D model
├── r1/
│   └── scene.gltf        # Target aircraft 3D model
└── data.csv              # Your trajectory data

```

---

## 📊 CSV Data Requirements

The input CSV must contain the following columns:

| Column | Description |
| --- | --- |
| `time` | Simulation time in seconds |
| `mx, my, mz` | Missile Position (X, Y, Z) |
| `mvx, mvy, mvz` | Missile Velocity (Vx, Vy, Vz) |
| `tx, ty, tz` | Target Position (X, Y, Z) |
| `tvx, tvy, tvz` | Target Velocity (Vx, Vy, Vz) |

---

## 🚀 How to Use

1. **Prepare Models:** Place your `.gltf` models in the folders specified in the script.
2. **Run the Script:**
```bash
python missile_sim.py

```


3. **Select File:** A Windows dialog will open. Select your trajectory CSV.
4. **Watch & Record:** The simulation will play in the PyVista window and automatically save a file named `missile_vs_target.mp4` to your directory.

---

## ⚙️ Configuration

You can adjust these variables directly in the script to customize the simulation:

* **Kill Distance:** `KILL_DIST = 35.0` (Distance in meters for a "Hit" status).
* **Model Scale:** Adjust the `scale` argument in `load_gltf()` to resize the missile or aircraft.
* **Terrain Height:** Change `noise.SetAmplitude(2000)` to make mountains taller or flatter.
* **Framerate:** Change `framerate=50` in `plotter.open_movie()` to adjust video speed.

---

## 📐 Mathematics Overview

The simulation calculates the heading angle between the missile velocity and the Line-of-Sight (LOS) vector using the dot product formula:

The 3D orientation is handled via a rotation matrix  to align the model's forward axis with the velocity vector.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

```

---

**Would you like me to help you create a sample Python script to generate a dummy CSV file for testing this visualizer?**

```
