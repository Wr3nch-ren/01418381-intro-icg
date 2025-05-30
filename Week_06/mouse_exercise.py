import sys, os
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math as m

win_w, win_h = 1024, 768
t_value, wireframe, pause = 0, False, True
mouse = [0, 0, GLUT_LEFT_BUTTON, GLUT_UP]
rotate_xyz = [0, 0, 0]

def motion_func(x ,y):
    dx, dy = x-mouse[0], y-mouse[1]
    button, state = mouse[2], mouse[3]
    mouse[0], mouse[1] = x, y
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            pass
    glutPostRedisplay()

def mouse_func(button, state, x, y):
    mouse[0], mouse[1], mouse[2], mouse[3] = x, y, button, state
    glutPostRedisplay()

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, win_w/win_h, 0.01, 100)

def keyboard(key, x, y):
    global wireframe, pause

    key = key.decode("utf-8")
    if key == ' ':
        pause = not pause
        glutIdleFunc(None if pause else idle)
    elif key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    elif key == 'q':
        os._exit(0)
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #glLightfv(GL_LIGHT0, GL_POSITION, 
    #   [-1.5*m.cos(theta/180*m.pi), 0, 1.5*m.sin(theta/180*m.pi), 1])
    gluLookAt(3, 0, 0, 0, 0, 0, 0, 1, 0)
    glColor3f(0, 1, 1)
    # glLightfv(GL_LIGHT0, GL_POSITION, [-1.5, 0, 0, 1])
    glRotate(theta, 0, 1, 0)
    glutSolidTeapot(1)
    glutSwapBuffers()


theta = 0
def idle():
    global theta
    theta = theta + 0.1
    print(theta)
    glutPostRedisplay()

def init_gl():
    glClearColor(0.01, 0.01, 0.2, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1, 1, 0, 0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 0, 0, 0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, [50])
    glLightfv(GL_LIGHT0, GL_POSITION, [-1.5, 0, 0, 1])
    glShadeModel(GL_SMOOTH)

def main():  
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Mouse Exercise")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse_func)
    glutPassiveMotionFunc(motion_func)
    glutMotionFunc(motion_func)
    init_gl()
    glutMainLoop()

if __name__ == "__main__":
    main()