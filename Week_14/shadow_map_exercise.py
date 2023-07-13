import sys, os
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
from PIL import Image
import gl_helpers as glh

win_w, win_h = 1280, 960
t_value, wireframe, pause = 0, False, True
n_vertices, positions, colors, normals, uvs = 0, None, None, None, None
centroid, bbox, t_value = None, None, 0
mouse = [0, 0, GLUT_LEFT_BUTTON, GLUT_UP]
rotate_degree = [0, 0, 0]
shadow_map_size = 64

def idle():
    global t_value
    t_value += 0.01
    glutPostRedisplay()

def print_shader_info_log(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        os._exit()

def print_program_info_log(shader, prompt=""):
    result = glGetProgramiv(shader, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(shader).decode("utf-8")))
        os._exit()

def compile_program(vert_code, frag_code):
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(vert_id, vert_code)
    glShaderSource(frag_id, frag_code)

    glCompileShader(vert_id)
    glCompileShader(frag_id)
    print_shader_info_log(vert_id, "Vertex Shader")
    print_shader_info_log(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    print_program_info_log(prog_id, "Link Error")
    return prog_id

def motion_func(x ,y):
    dx, dy = x-mouse[0], y-mouse[1]
    button, state = mouse[2], mouse[3]
    mouse[0], mouse[1] = x, y
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            if abs(dx) > abs(dy):
                rotate_degree[0] += dx
            else:
                rotate_degree[1] += dy
        elif button == GLUT_MIDDLE_BUTTON:
            if abs(dx) > abs(dy):
                rotate_degree[2] += dx
            else:
                rotate_degree[2] += dy
    glutPostRedisplay()

def mouse_func(button, state, x, y):
    mouse[0], mouse[1], mouse[2], mouse[3] = x, y, button, state
    glutPostRedisplay()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    proj_mat = glh.Perspective(60, win_w/win_h, 0.01, 100)

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
    view_mat = glh.LookAt(centroid[0], centroid[1], centroid[2]+0.5*max(bbox), *centroid, 0, 1, 0)
    model_mat = glh.Rotate(rotate_degree[0], 0, 1, 0)
    model_mat = model_mat @ glh.Rotate(rotate_degree[1], 1, 0, 0)
    model_mat = model_mat @ glh.Rotate(rotate_degree[2], 0, 0, 1)

    # First pass: create shadow map 
    # Fix me!
    # Create shadow map into FBO.


    # Second pass: render scene
    # Fix me!
    # Render the scene (The information of the pass appears in Week 14).

    glutSwapBuffers()

def init_shaders():
    global shadow_prog_id, render_prog_id
    global shadow_vao, render_vao

    # First pass: create shadow map
    shadow_vert_code = '''
#version 120
attribute vec3 position;
void main()
{
}
'''
    shadow_frag_code = '''
#version 110
void main()
{
}
'''
    shadow_prog_id = compile_program(shadow_vert_code, shadow_frag_code)
    glUseProgram(shadow_prog_id)

    shadow_vao = glGenVertexArrays(1)
    glBindVertexArray(shadow_vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)
    position_loc = glGetAttribLocation(shadow_prog_id, "position")
    if position_loc != -1:
        glVertexAttribPointer(position_loc, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(position_loc)

    # Second pass: render scene
    render_vert_code = '''
#version 140
in vec3 position, color, normal;
in vec2 uv;
uniform mat4 model_mat, view_mat, proj_mat, shadow_mat;
out vec3 P, eye_position, lerped_normal, Kd;
out vec4 ss_position;   // Shadow-space (Light-space) position
void main()
{
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);
    P = (model_mat * vec4(position, 1)).xyz;
    eye_position = (inverse(view_mat) * vec4(0, 0, 0, 1)).xyz;
    mat4 adjunct_mat = transpose(inverse(model_mat));
    lerped_normal = (adjunct_mat * vec4(normal, 0)).xyz;
    ss_position = shadow_mat * vec4(position, 1);
    Kd = color;
}
'''
    render_frag_code = '''
#version 140
in vec3 P, eye_position, lerped_normal, Kd;
in vec4 ss_position;
uniform vec3 light_position, light_intensity, Ka, Ks;
uniform float shininess;
uniform sampler2D shadow_map;
out vec4 gl_FragColor;
void main()
{
}
'''
    render_prog_id = compile_program(render_vert_code, render_frag_code)
    glUseProgram(render_prog_id)

    render_vao = glGenVertexArrays(1)
    glBindVertexArray(render_vao)
    vbo = glGenBuffers(4)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)
    position_loc = glGetAttribLocation(render_prog_id, "position")
    if position_loc != -1:
        glVertexAttribPointer(position_loc, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(position_loc)

    color_loc = glGetAttribLocation(render_prog_id, "color")
    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)
    if color_loc != -1:
        glVertexAttribPointer(color_loc, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(color_loc)

    normal_loc = glGetAttribLocation(render_prog_id, "normal")
    glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
    glBufferData(GL_ARRAY_BUFFER, normals, GL_STATIC_DRAW)
    if normal_loc != -1:
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(normal_loc)

    uv_loc = glGetAttribLocation(render_prog_id, "uv")
    glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
    glBufferData(GL_ARRAY_BUFFER, uvs, GL_STATIC_DRAW)
    if uv_loc != -1:
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(uv_loc)

    # Fix me!
    # You need to create an FBO and link it to a texture.
    

def init_gl_and_model():
    global n_vertices, positions, colors, normals, uvs, centroid, bbox

    glClearColor(0.01, 0.01, 0.2, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    df = pd.read_csv("../models/objects_and_walls.tri",delim_whitespace=True, 
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]

    n_vertices = len(positions)
    print("no. of vertices: %d, no. of triangles: %d" % 
          (n_vertices, n_vertices//3))
    print("Centroid:", centroid)
    print("BBox:", bbox)

def main():  
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Shadow Map Exercise")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse_func)
    glutPassiveMotionFunc(motion_func)
    glutMotionFunc(motion_func)
    glutIdleFunc(idle)
    init_gl_and_model()
    init_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()