import numpy as np
import pandas as pd
import trimesh
import pyvista as pv
import tkinter as tk
from tkinter import filedialog
import time

# ============================================================
# FILE SELECTION
# ============================================================
def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select Trajectory CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )

# ============================================================
# LOAD CSV
# ============================================================
file_path = select_csv_file()
if not file_path:
    raise RuntimeError("No CSV selected")

data = pd.read_csv(file_path)

times = data["time"].values
missile_pos = data[["mx","my","mz"]].values
missile_vel = data[["mvx","mvy","mvz"]].values
target_pos  = data[["tx","ty","tz"]].values
target_vel  = data[["tvx","tvy","tvz"]].values

# ============================================================
# HIT DETECTION
# ============================================================
KILL_DIST = 35.0
ranges = np.linalg.norm(target_pos - missile_pos, axis=1)
hit_idx = np.where(ranges <= KILL_DIST)[0]
hit_idx = hit_idx[0] if len(hit_idx) else len(times)-1

# ============================================================
# ROTATION FROM VELOCITY
# ============================================================
def rotation_from_velocity(v):
    n = np.linalg.norm(v)
    if n < 1e-6:
        return np.eye(3)

    v = v / n
    yaw = np.arctan2(v[1], v[0])
    pitch = np.arctan2(v[2], np.sqrt(v[0]**2 + v[1]**2))

    Rz = np.array([[ np.cos(yaw),-np.sin(yaw),0],
                   [ np.sin(yaw), np.cos(yaw),0],
                   [0,0,1]])

    Ry = np.array([[ np.cos(-pitch),0,np.sin(-pitch)],
                   [0,1,0],
                   [-np.sin(-pitch),0,np.cos(-pitch)]])

    return Rz @ Ry



# ============================================================
# HEADING ANGLE
# ============================================================
def heading_deg(v, mp, tp):
    los = tp - mp
    nv = np.linalg.norm(v)
    nl = np.linalg.norm(los)
    if nv < 1e-6 or nl < 1e-6:
        return 0.0
    v = v / nv
    los = los / nl
    return np.degrees(np.arccos(np.clip(np.dot(v, los), -1, 1)))

# ============================================================
# CREATE TERRAIN
# ============================================================
def create_mountain_terrain(missile_pos, target_pos):
    # 1. Define the size based on simulation bounds
    all_pts = np.vstack([missile_pos, target_pos])
    x_min, x_max = all_pts[:,0].min() - 15000, all_pts[:,0].max() + 15000
    y_min, y_max = all_pts[:,1].min() - 15000, all_pts[:,1].max() + 15000
    z_floor = all_pts[:,2].min() - 1500 

    # 2. Create a High-Resolution Grid
    res = 250  
    terrain = pv.Plane(
        center=((x_min + x_max)/2, (y_min + y_max)/2, z_floor),
        direction=(0, 0, 1),
        i_size=(x_max - x_min),
        j_size=(y_max - y_min),
        i_resolution=res,
        j_resolution=res
    )

    # 3. Use PyVista's built-in parametric surfaces or a simple noise displacement
    # This approach is version-safe
    import vtk
    noise = vtk.vtkPerlinNoise()
    noise.SetFrequency(0.0001, 0.0001, 0.0001)
    noise.SetAmplitude(2000) # Height of the mountains

    # Apply displacement to the points
    points = terrain.points.copy()
    for i in range(len(points)):
        # Calculate noise value for each point
        val = noise.EvaluateFunction(points[i])
        points[i, 2] += val

    terrain.points = points
    # Recompute elevation scalars for the colormap
    terrain = terrain.elevation() 
    
    return terrain


# ============================================================
# LOAD GLTF
# ============================================================
def load_gltf(path, scale, base_rot):
    scene = trimesh.load(path, force="scene")
    mesh = trimesh.util.concatenate(scene.geometry.values())
    mesh.vertices -= mesh.vertices.mean(axis=0)
    mesh.apply_scale(scale)
    mesh.vertices = mesh.vertices @ base_rot.T
    return pv.PolyData(mesh.vertices, np.hstack(
        (np.full((len(mesh.faces),1),3), mesh.faces)
    ))

MISSILE_ROT = np.array([[0,0,1],[0,1,0],[-1,0,0]])
AIRCRAFT_ROT = np.array([[0,-1,0],[1,0,0],[0,0,1]])

missile_mesh = load_gltf("./missile/scene.gltf", 2000, MISSILE_ROT)
target_mesh  = load_gltf("./r1/scene.gltf", 800, AIRCRAFT_ROT)



# ============================================================
# PYVISTA SCENE
# ============================================================



plotter = pv.Plotter(window_size=(1600,900))
plotter.set_background("skyblue", top="royalblue") # Gradient sky

plotter.add_text("MISSILE Vs TARGET SIMULATION", position="upper_edge", font_size=16, color='white')
plotter.show_axes()

mountains = create_mountain_terrain(missile_pos, target_pos)

plotter.add_mesh(
    mountains,
    scalars="Elevation", 
    cmap="terrain",      # Provides the mountain colors
    show_scalar_bar=False,
    lighting=True,
    roughness=1.0      # Makes it look less "shiny" and more like rock
)

# Add a sun-like light to create shadows on the mountains
sunlight = pv.Light(position=(5000, 5000, 10000), intensity=1.2)
plotter.add_light(sunlight)

# ============================================================
# MODEL ACTORS
# ============================================================
missile_actor = plotter.add_mesh(
    missile_mesh.copy(),
    color="cyan",
    smooth_shading=True
)

target_actor = plotter.add_mesh(
    target_mesh.copy(),
    color="red",
    opacity=0.6,
    smooth_shading=True
)

# ============================================================
# ATTACHED PATH LINES (MODEL-FOLLOWING)
# ============================================================
missile_path = pv.PolyData(missile_pos[:1])
missile_path.lines = np.array([1, 0])
missile_path_actor = plotter.add_mesh(missile_path, color="cyan", line_width=2)

target_path = pv.PolyData(target_pos[:1])
target_path.lines = np.array([1, 0])
target_path_actor = plotter.add_mesh(target_path, color="red", line_width=2)


# HUD
info = plotter.add_text("", position="upper_left", font_size=10, color="white")


# Set the camera to a side view (Looking at the X-Z plane)
plotter.view_yz() 
plotter.camera.zoom(2.5)   # Zoom in once
# Zoom out slightly so the whole terrain is visible
#plotter.reset_camera()

# Example: Custom "High-Angle Side View"
'''plotter.camera_position = [
    (10000, 10000, 5000), # Camera location (X, Y, Z)
    (0, 0, 0),             # Look at this point (center of scene)
    (0, 0, 1)              # Z-axis is "up"
]'''

# ============================================================
# RECORD
# ============================================================
plotter.open_movie("missile_vs_target.mp4", framerate=50)
plotter.show(interactive_update=True, auto_close=False)

# ============================================================
# ANIMATION LOOP
# ============================================================
for i in range(hit_idx + 50):
    idx = min(i, hit_idx)

    # ---- UPDATE PATH LINES (ATTACHED) ----
    missile_path.points = missile_pos[:idx+1]
    missile_path.lines = np.hstack([[idx+1], np.arange(idx+1)])

    target_path.points = target_pos[:idx+1]
    target_path.lines = np.hstack([[idx+1], np.arange(idx+1)])

    # ---- UPDATE MODELS ----
    missile_actor.mapper.dataset.points = (
        missile_mesh.points @ rotation_from_velocity(missile_vel[idx]).T
        + missile_pos[idx]
    )

    target_actor.mapper.dataset.points = (
        target_mesh.points @ rotation_from_velocity(target_vel[idx]).T
        + target_pos[idx]
    )
    
    sep = np.linalg.norm(target_pos[idx] - missile_pos[idx])
    hdg = heading_deg(missile_vel[idx], missile_pos[idx], target_pos[idx])
    
    missile_speed = np.linalg.norm(missile_vel[idx])
    target_speed = np.linalg.norm(target_vel[idx])
    
    info.set_text("upper_left", (
    "========== MISSILE ==========\n"
    f"X : {missile_pos[idx,0]:10.1f} m\n"
    f"Y : {missile_pos[idx,1]:10.1f} m\n"
    f"Z : {missile_pos[idx,2]:10.1f} m\n"
    f"SPD : {missile_speed:8.1f} m/s\n"
    f"HDG : {hdg:8.2f} deg\n\n"

    "========== TARGET ==========\n"
    f"X : {target_pos[idx,0]:10.1f} m\n"
    f"Y : {target_pos[idx,1]:10.1f} m\n"
    f"Z : {target_pos[idx,2]:10.1f} m\n"
    f"SPD : {target_speed:8.1f} m/s\n\n"

    "======= ENGAGEMENT ========\n"
    f"SEP : {sep:8.2f} m\n"
    f"TIME: {times[idx]:8.2f} s\n"
    f"STAT: {'HIT' if idx >= hit_idx else 'TRACK'}\n\n"
    ))


    plotter.render()
    plotter.write_frame()
    time.sleep(0.02)

plotter.close()
