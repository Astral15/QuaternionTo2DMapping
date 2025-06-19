import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from scipy.spatial.transform import Rotation as R

vertices = (
    (1, -2, -0.2), (1, 2, -0.2), (-1, 2, -0.2), (-1, -2, -0.2),
    (1, -2,  0.2), (1, 2,  0.2), (-1, -2,  0.2), (-1, 2,  0.2)
)

edges = (
    (0,1), (1,2), (2,3), (3,0), (4,5), (5,7), (7,6), (6,4),
    (0,4), (1,5), (2,7), (3,6)
)

surfaces = (
    (0,1,2,3), (4,5,7,6), (0,1,5,4),
    (2,3,6,7), (1,2,7,5), (0,3,6,4)
)

colors = (
    (0.1, 0.1, 0.1), (0.2, 0.2, 0.2), (0.3, 0.3, 0.3),
    (0.3, 0.3, 0.3), (0.2, 0.2, 0.2), (0.2, 0.2, 0.2)
)

def draw_phone():
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor3fv(colors[i % len(colors)])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_virtual_cursor(x, y):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 600, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 0, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    radius = 8
    for angle in range(0, 361, 30):
        rad = np.radians(angle)
        glVertex2f(x + radius * np.cos(rad), y + radius * np.sin(rad))
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, display[0] / display[1], 0.1, 100.0)
    glTranslatef(0.0, 0.0, -8)

    rotation = R.identity()
    forward_vec = np.array([0, 0, 1])
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        angle = 2

        if keys[K_LEFT]:
            rotation = R.from_euler('y', angle, degrees=True) * rotation
        if keys[K_RIGHT]:
            rotation = R.from_euler('y', -angle, degrees=True) * rotation
        if keys[K_UP]:
            rotation = R.from_euler('x', angle, degrees=True) * rotation
        if keys[K_DOWN]:
            rotation = R.from_euler('x', -angle, degrees=True) * rotation

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        rot_matrix = rotation.as_matrix()
        glPushMatrix()
        rot4 = np.identity(4)
        rot4[:3, :3] = rot_matrix
        glMultMatrixf(rot4.T)
        draw_phone()
        glPopMatrix()

        rotated_forward = rot_matrix @ forward_vec
        cursor_x = int((rotated_forward[0] + 1) / 2 * display[0])
        cursor_y = int((1 - rotated_forward[1]) / 2 * display[1])
        cursor_x = max(0, min(display[0] - 1, cursor_x))
        cursor_y = max(0, min(display[1] - 1, cursor_y))

        draw_virtual_cursor(cursor_x, cursor_y)
        pygame.display.flip()
        clock.tick(60)

        quat = rotation.as_quat()
        print(f"\nQuaternion [x y z w]: {quat.round(4)}")
        print(f"Cursor: ({cursor_x}, {cursor_y})")

main()
