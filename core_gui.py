import sys
import random
import math
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import math


class ChaseCore3D(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.particles = []
        self.speaking = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # ~60fps

        self.init_particles()

    def init_particles(self):
        for _ in range(150):
            self.particles.append([
                random.uniform(-2, 2),
                random.uniform(-2, 2),
                random.uniform(-2, 2)
            ])

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.02, 0.02, 0.02, 1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h else 1, 0.1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -8)

        self.draw_core()
        self.draw_ring()
        self.draw_particles()

    def draw_core(self):
        glPushMatrix()
        glow = 1.5 if self.speaking else 1.0
        glColor3f(1.0, 0.5 * glow, 0.0)
        glColor3f(1.0, 0.6, 0.0)
        glPopMatrix()

    def draw_ring(self):
        glPushMatrix()
        glColor3f(1.0, 0.7, 0.1)  
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)

        segments = 120
        radius = 2.5

        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0)

        glEnd()
        glPopMatrix()


    def draw_particles(self):
        glPointSize(2)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.6, 0.1)
        for p in self.particles:
            glVertex3f(p[0], p[1], p[2])
        glEnd()

    def update_scene(self):
        self.angle += 1.5 if self.speaking else 0.5
        self.update()

    def set_speaking(self, state):
        self.speaking = state

if __name__ == "__main__":
    from OpenGL.GLUT import glutInit, glutSolidSphere, glutWireTorus
    glutInit()

    app = QApplication(sys.argv)
    window = ChaseCore3D()
    window.resize(800, 800)
    window.setWindowTitle("Chase Reactor Core")
    window.show()
    sys.exit(app.exec_())