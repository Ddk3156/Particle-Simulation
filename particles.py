import cv2
import mediapipe as mp
import numpy as np
import pygame
import moderngl
import time

# -------- Hand Tracking --------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

# -------- Camera --------
cap = cv2.VideoCapture(0)

# -------- OpenGL --------
W, H = 800, 600
pygame.init()
pygame.display.set_mode((W, H), pygame.OPENGL | pygame.DOUBLEBUF)
ctx = moderngl.create_context()

ctx.enable(moderngl.PROGRAM_POINT_SIZE)
ctx.enable(moderngl.BLEND)
ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE

# -------- Camera Texture --------
cam_tex = ctx.texture((W, H), 3)
cam_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

quad = ctx.buffer(np.array([
    -1, -1, 0, 0,
     1, -1, 1, 0,
    -1,  1, 0, 1,
     1,  1, 1, 1,
], dtype='f4'))

bg_prog = ctx.program(
    vertex_shader="""
    #version 120
    attribute vec2 in_pos;
    attribute vec2 in_uv;
    varying vec2 uv;
    void main() {
        uv = in_uv;
        gl_Position = vec4(in_pos, 0.0, 1.0);
    }
    """,
    fragment_shader="""
    #version 120
    uniform sampler2D tex;
    varying vec2 uv;
    void main() {
        vec4 color = texture2D(tex, uv);
        gl_FragColor = vec4(color.rgb * 0.8, 1.0);
    }
    """
)

bg_vao = ctx.simple_vertex_array(bg_prog, quad, 'in_pos', 'in_uv')

# -------- Particles --------
NUM = 15000

pos = np.random.uniform(-1, 1, (NUM, 2)).astype('f4')
vel = np.zeros((NUM, 2), dtype='f4')
speed = np.zeros((NUM, 1), dtype='f4')

particle_buffer = ctx.buffer(np.hstack([pos, speed]).astype('f4').tobytes())

prog = ctx.program(
    vertex_shader="""
    #version 120
    attribute vec2 in_pos;
    attribute float in_speed;
    varying float speed;

    void main() {
        speed = in_speed;
        gl_Position = vec4(in_pos, 0.0, 1.0);
        gl_PointSize = 2.0 + in_speed * 12.0;
    }
    """,
    fragment_shader="""
    #version 120
    varying float speed;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float d = length(coord);
        if (d > 0.5) discard;

        float glow = clamp(speed * 0.5, 0.0, 1.0);
        gl_FragColor = vec4(1.0, 0.4 + glow, glow, 0.9);
    }
    """
)

vao = ctx.simple_vertex_array(prog, particle_buffer, 'in_pos', 'in_speed')

center = np.array([0.0, 0.0])
prev_openness = 0.0
last_time = time.time()

# -------- Main Loop --------
while True:

    dt = time.time() - last_time
    last_time = time.time()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            quit()

    ret, frame = cap.read()
    frame = cv2.flip(frame, 0)
    frame = cv2.resize(frame, (W, H))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    openness = 0.0

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0].landmark

        palm = lm[0]
        index_tip = lm[8]

        dx = index_tip.x - palm.x
        dy = index_tip.y - palm.y

        openness = np.clip(np.sqrt(dx*dx + dy*dy) * 5, 0.0, 1.0)

        center[0] = (lm[9].x - 0.5) * 2
        center[1] = -(lm[9].y - 0.5) * 2

    # -------- Physics --------
    direction = center - pos
    dist = np.linalg.norm(direction, axis=1).reshape(-1, 1) + 0.0001
    norm = direction / dist

    compression = norm * (8.0 * (1.0 - openness)) / (dist + 0.05)

    burst = np.clip(openness - prev_openness, 0.0, 1.0)
    explosion = -norm * (30.0 * burst)

    vel += compression * dt
    vel += explosion * dt
    vel *= 0.90

    pos += vel * dt
    speed = np.linalg.norm(vel, axis=1).reshape(-1, 1)

    particle_buffer.write(np.hstack([pos, speed]).astype('f4').tobytes())
    prev_openness = openness

    # -------- Render --------
    ctx.clear(0.0, 0.0, 0.0)

    ctx.disable(moderngl.DEPTH_TEST)
    cam_tex.write(rgb.tobytes())
    cam_tex.use()
    bg_vao.render(moderngl.TRIANGLE_STRIP)

    vao.render(moderngl.POINTS)

    pygame.display.flip()
