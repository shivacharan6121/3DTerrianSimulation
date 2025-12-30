---

# Missile vs Target 3D Trajectory Visualizer (CSV-Driven)

A **file-driven 3D missile–target engagement visualizer** built using **PyVista**, **Trimesh**, **NumPy**, and **Pandas**.
The simulation reads time-step state data from a CSV file and renders a full 3D engagement scene with terrain, models, trajectories, HUD telemetry, hit detection, and video recording.

This project is intended for **trajectory visualization, validation, and analysis** — not real-time guidance or control.

---

## Features

* 📁 **CSV-Driven Simulation**

  * Reads missile and target position & velocity at each time step
* 🚀 **3D GLTF Models**

  * Missile and target models are aligned with their velocity vectors
* 🧭 **Heading Angle Calculation**

  * Missile heading relative to line-of-sight (LOS)
* 🗺️ **Procedural Mountain Terrain**

  * Perlin-noise-based terrain with realistic elevation coloring
* 📈 **Trajectory Path Lines**

  * Continuous path lines from start to end for verification
* 🎥 **MP4 Video Recording**

  * Automatically records the animation to a video file
* 🎯 **Hit Detection**

  * Engagement stops once kill distance is reached
* 📊 **HUD Overlay**

  * Real-time telemetry for missile, target, and engagement state

---

## CSV File Format

The simulation requires a CSV file with the **exact column structure** shown below:

```
time,
mx,my,mz,
mvx,mvy,mvz,
tx,ty,tz,
tvx,tvy,tvz
```

### Column Description

| Column        | Meaning                   |
| ------------- | ------------------------- |
| `time`        | Simulation time (seconds) |
| `mx,my,mz`    | Missile position (meters) |
| `mvx,mvy,mvz` | Missile velocity (m/s)    |
| `tx,ty,tz`    | Target position (meters)  |
| `tvx,tvy,tvz` | Target velocity (m/s)     |

---

## Project Structure

```
project-root/
│
├── main.py                  # Simulation script
├── missile/
│   └── scene.gltf           # Missile 3D model
├── r1/
│   └── scene.gltf           # Target aircraft 3D model
├── data/
│   └── trajectory.csv       # Input CSV file
└── README.md
```

---

## Dependencies

Install required Python packages:

```bash
pip install numpy pandas pyvista trimesh vtk
```

### Notes

* `tkinter` is required for file selection (usually included with Python)
* A working OpenGL environment is required for PyVista rendering

---

## How to Run

1. Ensure the GLTF models exist at:

   * `./missile/scene.gltf`
   * `./r1/scene.gltf`
2. Prepare a CSV file matching the required format
3. Run the script:

```bash
python terrianplot.py
```

4. Select the CSV file when prompted
5. The visualization window opens and video recording starts automatically

---

## Output

### Video

https://github.com/user-attachments/assets/a821ccd5-96d9-45a1-aace-a3ff93e969bd


### On-Screen HUD Displays

* Missile position (X, Y, Z)
* Missile speed
* Missile heading angle (deg)
* Target position and speed
* Separation distance
* Simulation time
* Engagement status (`TRACK` / `HIT`)

---

## Hit Detection Logic

* Kill distance is defined as:

```python
KILL_DIST = 35.0  # meters
```

* The first time separation falls below this distance:

  * Engagement status switches to **HIT**
  * Animation continues briefly for visualization
  * Trajectory paths remain visible

---

## Visualization Details

* Gradient sky background
* Directional sunlight for terrain shading
* Smooth shading for missile and target models
* Side-view camera (Y-Z plane) with zoom
* Terrain scaled dynamically to trajectory bounds

---

## Known Limitations

* No physics or guidance law computation
* CSV data must be valid and time-ordered
* Terrain is procedural (not geo-referenced)
* Very large datasets may reduce frame rate

---

## Typical Use Cases

* Missile–target engagement visualization
* Trajectory verification and debugging
* Post-processing simulation output
* Demonstrations and technical presentations

---

## License

This project is provided for **educational and research purposes only**.
No warranty or operational suitability is implied.

---

Just say the word.
