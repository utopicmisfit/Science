# rotating_earth_quakes.py — Rotating Earth with Earthquake Visualization
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import requests
from datetime import datetime

# --------------------------------------------------------------
# 1. Fetch earthquake data
# --------------------------------------------------------------
def fetch_earthquake_data():
    """Fetch recent earthquake data from USGS"""
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"
        response = requests.get(url)
        data = response.json()["features"]
        
        quakes = []
        for q in data:
            quakes.append({
                "magnitude": q["properties"]["mag"],
                "latitude": q["geometry"]["coordinates"][1],
                "longitude": q["geometry"]["coordinates"][0],
                "place": q["properties"]["place"]
            })
        return quakes
    except:
        print("Failed to fetch earthquake data. Using sample data.")
        # Return some sample data if fetch fails
        return [
            {"magnitude": 5.2, "latitude": 35.0, "longitude": -120.0, "place": "Sample 1"},
            {"magnitude": 6.1, "latitude": -10.0, "longitude": 160.0, "place": "Sample 2"},
            {"magnitude": 4.8, "latitude": 40.0, "longitude": 30.0, "place": "Sample 3"}
        ]

# Fetch earthquake data
earthquakes = fetch_earthquake_data()

# Get current date for the title
current_date = datetime.now().strftime("%B %d, %Y")

# --------------------------------------------------------------
# 2. Figure setup — pure black background
# --------------------------------------------------------------
fig = plt.figure(figsize=(14, 8), facecolor='black')
ax = fig.add_axes([0, 0.05, 1, 0.9], projection=ccrs.Orthographic(central_longitude=0, central_latitude=10))
ax.set_global()

# Remove all axes decoration
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

# Black background
ax.set_facecolor('black')

# --------------------------------------------------------------
# 3. Animation — clean every frame and plot earthquakes
# --------------------------------------------------------------
def animate(frame):
    # Clear all dynamic elements
    for artist in list(ax.artists):
        artist.remove()
    # Clear all collections
    for coll in list(ax.collections):
        coll.remove()
    for patch in list(ax.patches):
        patch.remove()
    # Clear lines (which include the plotted points)
    for line in list(ax.lines):
        line.remove()
    # Clear text (labels)
    for text in list(ax.texts):
        text.remove()

    # Rotate the globe
    lon0 = (frame * -0.5) % 360
    ax.projection = ccrs.Orthographic(central_longitude = lon0 + 140, central_latitude = 20)
    ax.set_global()

    # Re-apply black background after projection change
    ax.set_facecolor('black')

    # Draw circumference boundary around the globe view
    circle = mpatches.Circle((0.5, 0.5), 0.5, transform=ax.transAxes, 
                            fill=False, edgecolor='cyan', linewidth=1.50,
                            alpha=0.9, zorder=10)
    ax.add_patch(circle)
    
    # Add outer glow
    circle_glow = mpatches.Circle((0.5, 0.5), 0.55, transform=ax.transAxes,
                                 fill=False, edgecolor='cyan', linewidth=0.60,
                                 alpha=0.3, zorder=9)
    ax.add_patch(circle_glow)

    # Dark ocean + subtle land
    ax.add_feature(cfeature.OCEAN, facecolor="#000000", zorder=2)
    ax.add_feature(cfeature.LAND, facecolor="#000000", zorder=3)

    # Bright cyan coastlines
    ax.add_feature(cfeature.COASTLINE, edgecolor='cyan', linewidth=0.5, zorder=4)

    # Plot earthquakes
    for quake in earthquakes:
        mag = quake["magnitude"]
        lat = quake["latitude"]
        lon = quake["longitude"]
        
        # Size based on magnitude
        size = max(5, mag * 8) / 10
        
        # Color based on magnitude
        if mag < 5.0:
            color = 'yellow'
        elif mag < 6.0:
            color = 'orange'
        else:
            color = 'red'
        
        # Plot earthquake location
        ax.plot(lon, lat, 'o', color=color, markersize=size, 
                transform=ccrs.PlateCarree(), zorder=5, alpha=0.7)
        
        # Add a smaller inner dot for better visibility
        ax.plot(lon, lat, 'o', color='white', markersize=size/3, 
                transform=ccrs.PlateCarree(), zorder=6, alpha=0.9)

    # Add title with earthquake count and date
    title_text = f"Global Earthquakes (M≥4.5) in the last month - {current_date}"
    ax.text(-0.05, 1.00, title_text, transform=ax.transAxes, 
            color='white', fontsize=10, fontweight='bold',
            ha='center', va='bottom', zorder=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='black', 
                     alpha=0.7, edgecolor='white', linewidth=1))

    # Add legend just below the title
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                  markersize=8, label='M4.5-5.0'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                  markersize=8, label='M5.0-6.0'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                  markersize=8, label='M≥6.0')
    ]
    
    # Place legend below the title using bbox_to_anchor
    legend = ax.legend(handles=legend_elements, 
                      loc='upper center',
                      bbox_to_anchor=(-0.35, 0.10),  # Position below title
                      ncol=1,  # Arrange in a row
                      facecolor='black', 
                      edgecolor='white', 
                      labelcolor='white', 
                      fontsize=8,
                      framealpha=0.8)

    return []

# --------------------------------------------------------------
# 4. Create animation
# --------------------------------------------------------------
ani = FuncAnimation(fig, animate, frames=1200, interval=20, blit=False, repeat=True)

# Save as MP4 video
print("Saving MP4 video... This may take a few minutes.")
ani.save('rotating_earth_with_earthquakes.mp4', 
         writer='ffmpeg',  # Using FFmpeg writer for MP4
         fps=30,           # Frames per second
         dpi=150,          # Resolution
         bitrate=5000)     # Video quality (higher = better quality)
print("MP4 video saved successfully as 'rotating_earth_with_earthquakes.mp4'")

# Optionally show the animation (comment out if you only want to save)
# plt.show()