import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd
import imgui
from imgui.integrations.glut import GlutRenderer
from gl_helpers import *

impl, vao = None, None
win_w, win_h = 600, 600
clear_color = [0, 0.3, 0.3]
separation = 0

def draw_gui():
    global separation, clear_color
    impl.process_inputs()
    imgui.new_frame()                 # Start the Dear ImGui frame 
    imgui.set_next_window_position(win_w-250, win_h-100, imgui.FIRST_USE_EVER)
    imgui.begin("Control")            # Create a window
    imgui.push_item_width(200)
    _, separation = imgui.slider_float("Separation Value", separation, 0, 3)
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)    
    imgui.pop_item_width()

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    impl.set_current_gui_params(imgui.get_window_position(), imgui.get_window_size())        
    imgui.end()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    
def display():
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glUseProgram(prog_id)
    glBegin(GL_TRIANGLES)
    glTexCoord2f(0, 0)
    glVertex2f(-0.8, 0.8)
    glTexCoord2f(1, 0)
    glVertex2f(0.8, 0.8)
    glTexCoord2f(0.5, 1)
    glVertex2f(0.0, -0.8)
    glEnd()

    draw_gui()
    imgui.render()
    impl.render(imgui.get_draw_data())

    glutSwapBuffers()

wireframe = False
def keyboard(key, x, y):
    global wireframe

    key = key.decode("utf-8")
    if key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)        
    elif key == 'q':
        impl.shutdown()
        os._exit(0)

def idle():
    glutPostRedisplay()

def initialize():
    global impl

    show_versions()
    glEnable(GL_DEPTH_TEST)
    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlutRenderer()
    impl.user_keyboard_func(keyboard)
    impl.user_reshape_func(reshape)
       
def create_shaders():
    global prog_id

    vert_code = b'''
#version 120
void main()
{
   gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
}'''
    frag_code = b'''
#version 110
void main()
{
}'''

    prog_id = compileProgram(vert_code, frag_code)

def main():
    global impl
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowPosition(80, 0)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Double Vision Exercise")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    initialize()
    create_shaders()

    glutMainLoop()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()