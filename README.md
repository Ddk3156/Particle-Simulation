# Hand-Controlled Particle Explosion

An interactive particle simulation controlled by **real-time hand gestures**.

The program tracks your hand using **MediaPipe**, captures video using **OpenCV**, and renders thousands of particles using **ModernGL (GPU shaders)**.

Particles gather at your hand when it is closed and burst outward when the hand opens, creating an effect similar to a **small star explosion**.

---

## Demo



```
![Demo](demo.gif)
```

---

## Features

* Real-time **hand tracking**
* Interactive **particle explosion effect**
* **20,000 GPU-rendered particles**
* Webcam feed used as the background
* Smooth particle motion with simple physics
* Runs entirely in **real time**

---

## How It Works

### Hand Tracking

The webcam feed is processed using **MediaPipe Hands**, which detects landmarks on the hand.
The distance between the palm and the fingertip is used to estimate whether the hand is **open or closed**.

---

### Particle Physics

Each particle has:

* position
* velocity

Two main forces control the motion:

#### 1. Attraction (when the hand is closed)

Particles are pulled toward the center of the hand.

This works like a **gravitational pull**:

```
force ∝ direction_to_hand / distance
```

This causes the particles to collapse and gather into a dense cluster.

---

#### 2. Explosion (when the hand opens)

When the hand suddenly opens, particles receive a strong outward velocity.

```
velocity += outward_direction × explosion_strength
```

This produces the **burst effect**, similar to a small stellar explosion.

---

#### 3. Damping

Velocity slowly decreases over time:

```
velocity *= 0.9
```

This prevents particles from flying away forever and keeps the motion stable.

---

## Technologies Used

* Python
* OpenCV
* MediaPipe
* NumPy
* Pygame
* ModernGL (OpenGL shaders)

---

## Installation

Clone the repository:

```
git clone https://github.com/yourusername/hand-particle-explosion.git
cd hand-particle-explosion
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Run the Program

```
python main.py
```

Make sure your webcam is connected.

---

## Controls

| Hand Gesture | Effect                          |
| ------------ | ------------------------------- |
| Closed fist  | Particles collapse to the hand  |
| Open hand    | Particles explode outward       |
| Move hand    | Particle cloud follows the hand |

---

## Requirements

* Python 3.8+
* Webcam
* GPU with OpenGL support (recommended)

---

## License

This project is provided for educational purposes and can be licensed under the MIT License.
