# Tank Trouble

A 2D top-down tank combat game built using Python and Pygame. The project features physics-based bouncing projectiles, randomized level generation, and shared-keyboard local multiplayer. 

## Features

* **Shared-Keyboard Local Multiplayer**: Play locally against a friend on the same computer using the standalone `TankTrouble.py` script. The game is a race to 2 points.
* **Randomized Maps**: The game dynamically selects and loads from a pool of 10 uniquely designed maps every time you play.
* **Bouncing Projectiles**: Bullets reflect off walls based on their collision angle, allowing for strategic trick shots and clever angles.
* **Tile-Based Rendering**: Levels are 64x48 grids rendered using Tiled map files (`.tmx`) utilizing the `pytmx` library, ensuring crisp wall collisions and scaling.

## Prerequisites

To run this project, you need **Python 3.x** and the following external libraries installed:

```bash
pip install pygame pytmx

```

### Required Assets and Folder Structure

The game uses relative paths and expects the following folder structure to be present in the same directory as the main script:

* `imagefolder/` - Must contain the following sprites:
* `tank_blue.png`
* `tank_green.png`
* `dirt.png` (used for walls)
* `white.png`
* `BULLET.png`


* `MAZEFOLDER/` - Must contain the map data:
* The `dirt.tsx` tileset file.
* 10 distinct map blueprints named `TankTroubleMap1.tmx` through `TankTroubleMap10.tmx`.


* `snd/` - Directory for sound files.

## How to Play

1. Ensure all Python dependencies are installed.
2. Clone or download the repository, ensuring the folder structure remains intact.
3. Run the main script to launch the game window (1024x768 resolution):
```bash
python TankTrouble.py

```



## Controls

* **Blue Tank**:
* **Movement**: `Up Arrow` (Forward), `Down Arrow` (Backward)
* **Rotation**: `Left Arrow` / `Right Arrow`
* **Shoot**: `Spacebar`


* **Green Tank**:
* **Movement**: `W` (Forward), `S` (Backward)
* **Rotation**: `A` / `D`
* **Shoot**: `Q`



*Note: Tanks have a maximum of 6 bullets on screen at any given time, and bullets despawn after 6 seconds.*
