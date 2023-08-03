import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd

pos_temp = []
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(*(centroid+(0, 10, max(bbox))), *centroid, 0, 1, 0)
    glRotatef(degree, 0, 1, 0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glBegin(GL_TRIANGLES)
    for i in range(n_vertices):
        glColor3fv(0.5 * (normals[i] + 1))
        glVertex3fv(positions[i])
    glEnd()
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_TRIANGLES)
    for j in range(n_vertices):
        glColor3fv(colors[j])
        glVertex3fv(positions[j])
    glEnd()
    glBegin(GL_LINES)
    for k in range(n_vertices):
        pos_temp.append(positions[k])
        glColor3f(0.0, 1.0, 0.0)
        glVertex3fv()
        drawVertexNorm(normals[k])
    glEnd()
    glutSwapBuffers()

def drawVertexNorm(list normal):
    
    
    
    glColor3f(1.0, 0.0, 0.0)
    glVertex3fv(center - (normal * norm_length))

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w/h, 1, 50)

degree = 0
def idle():
    global degree
    degree = degree + 1
    glutPostRedisplay()

wireframe, animation = False, False
norm_length = 1
def keyboard(key, x, y):
    global wireframe, animation
    global norm_length
    

    key = key.decode("utf-8")
    if key == ' ':
        animation = not animation
        glutIdleFunc(idle if animation else None)
    elif key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    elif key == 'q':
        os._exit(0)
    elif key == '+':
        norm_length += 1
    elif key == '-':
        norm_length -= 1
    glutPostRedisplay()

def my_init():
    global n_vertices, positions, colors, normals, uvs
    global centroid, bbox

    glClearColor(0.2, 0.8, 0.8, 1)
    df = pd.read_csv("../models/ashtray.tri", delim_whitespace=True, comment='#',
                     header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    n_vertices = len(positions)
    print("no. of vertices: %d, no. of triangles: %d" % 
          (n_vertices, n_vertices//3))    
    print("Centroid: ", centroid)
    print(positions)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glLineWidth(1)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutCreateWindow("Show Normals")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    my_init()
    glutMainLoop()    

if __name__ == "__main__":
    main()