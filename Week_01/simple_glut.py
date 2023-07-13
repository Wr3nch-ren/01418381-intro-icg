import sys, os
from OpenGL.GL import *
from OpenGL.GLUT import *

def display_cb():
    glClearColor(1, 1, 0.5, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    glColor3f(0, 1, 0)
    glVertex3f(-0.5, -0.5, 0)
    glVertex3f( 0.5, -0.5, 0)
    glVertex3f( 0, 0.5, 0)
    glEnd()    
    glFlush()
    
def main():    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_SINGLE)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(50, 100)
    glutCreateWindow("A Simple GLUT Program")
    glutDisplayFunc(display_cb)
    show_versions()
    glutMainLoop()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()