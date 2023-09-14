import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd
import imgui
from imgui.integrations.glut import GlutRenderer
from gl_helpers_subst import *

impl, vao = None, None
shininess = 50
Ka, Kd, Ks, clear_color = [0.05, 0.05, 0.05], [0.5, 1.0, 0.2], [0.9, 0.9, 0.9], [0.1, 0.6, 0.6]
light_intensity, light_pos, eye_pos = [1, 1, 1], [0, 0, 0], [0, 0, 0]
specular_on, selection = True, False
rot_x, rot_y = 0, 0

def draw_gui():
    global selection, light_intensity, Ka, Kd, Ks, shininess, specular_on, clear_color, rot_x, rot_y
    impl.process_inputs()
    imgui.new_frame()                    # Start the Dear ImGui frame   
    imgui.begin("Control")               # Create a window
    imgui.push_item_width(300)
    _, light_intensity = imgui.color_edit3("Light Intensity", *light_intensity)
    _, Ka = imgui.color_edit3("Ka", *Ka)
    _, Kd = imgui.color_edit3("Kd", *Kd)
    _, Ks = imgui.color_edit3("Ks", *Ks)
    _, shininess = imgui.slider_float("Shininess", shininess, 0.1, 180)
    _, specular_on = imgui.checkbox("Specular Enabled", specular_on)
    _, rot_x = imgui.slider_float("Rotation X", rot_x, -180, 180)
    _, rot_y = imgui.slider_float("Rotation Y", rot_y, -180, 180)
    if imgui.radio_button("Choice 1", not selection): 
        selection = False
    imgui.same_line()
    if imgui.radio_button("Choice 2", selection): 
        selection = True    
    imgui.text("Light Position")
    imgui.push_item_width(100)
    _, light_pos[0] = imgui.slider_float("X###light_pos_x", light_pos[0], -10, 10)
    imgui.same_line()
    _, light_pos[1] = imgui.slider_float("Y###light_pos_y", light_pos[1], -10, 10)
    imgui.same_line()
    _, light_pos[2] = imgui.slider_float("Z###light_pos_z", light_pos[2], -10, 10)
    imgui.text("Eye Position")
    _, eye_pos[0] = imgui.slider_float("X###eye_pos_x", eye_pos[0], -10, 10)
    imgui.same_line()
    _, eye_pos[1] = imgui.slider_float("Y###eye_pos_y", eye_pos[1], -10, 10)
    imgui.same_line()
    _, eye_pos[2] = imgui.slider_float("Z###eye_pos_z", eye_pos[2], -10, 10)
    imgui.pop_item_width()
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    imgui.pop_item_width()
    imgui.end()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    proj_mat = Perspective(60, w/h, 0.1, 10)
    
def display():
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    model_mat = Rotate(rot_y, 0, 1, 0) @ Rotate(rot_x, 1, 0, 0)
    view_mat = LookAt(*eye_pos, *centroid, 0, 1, 0)
    

    glUseProgram(prog_id)
    glUniform3fv(glGetUniformLocation(prog_id, "Ka"), 1, Ka)
    glUniform3fv(glGetUniformLocation(prog_id, "Kd"), 1, Kd)
    glUniform3fv(glGetUniformLocation(prog_id, "Ks"), 1, Ks)
    glUniform1f(glGetUniformLocation(prog_id, "shininess"), shininess)
    glUniform1i(glGetUniformLocation(prog_id, "specular_on"), specular_on)
    glUniform3fv(glGetUniformLocation(prog_id, "light_pos"), 1, light_pos)
    glUniform3fv(glGetUniformLocation(prog_id, "eye_pos"), 1, eye_pos)
    glUniform3fv(glGetUniformLocation(prog_id, "light_intensity"), 1, light_intensity)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "model_mat"), 1, GL_TRUE, model_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "view_mat"), 1, GL_TRUE, view_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "proj_mat"), 1, GL_TRUE, proj_mat)

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)

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

    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlutRenderer()
    impl.user_keyboard_func(keyboard)
    impl.user_reshape_func(reshape)
    imgui.set_next_window_position(500, 10)
    imgui.set_next_window_collapsed(True)

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
        
def create_shaders():
    global prog_id, vao, vbo

    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    vert_code = b'''
#version 150
attribute vec3 position, normal, color;
in vec2 uv;
uniform vec3 Ka, Kd, Ks, eye_pos, light_pos, light_intensity;
uniform float shininess;
uniform mat4 model_mat, view_mat, proj_mat;
uniform bool specular_on;
out vec3 phong_color;
void main()
{
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);
    vec3 P = (model_mat * vec4(position, 1)).xyz;
    vec3 L = normalize(light_pos - P);
    vec3 V = normalize(eye_pos - P);
    vec3 N = (model_mat * vec4(normal, 0)).xyz;
    vec3 R = 2 * dot(L, N) * N - L;
    
    vec3 ambient = Ka * light_intensity;
    vec3 diffuse = Kd * max(dot(N, L), 0) * light_intensity;
    vec3 specular = Ks * pow(max(dot(V, R), 0), shininess) * light_intensity;
    // if (dot(N, L) <= 0 || !specular_on)
    //     specular = vec3(0, 0, 0);
    phong_color = ambient + diffuse + specular;
}'''
    frag_code = b'''
#version 150
in vec3 phong_color;
void main()
{
   gl_FragColor = vec4(phong_color, 1);
}'''
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
    print_program_info_log(prog_id, "Link error")

    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global light_pos, eye_pos

    df = pd.read_csv("../models/teapot_culling.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)
    light_pos = centroid + (0, 0, 5)
    eye_pos = centroid + (0, 0, 3)

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    n_vertices = len(positions)

    glUseProgram(prog_id)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(4)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)
    position_loc = glGetAttribLocation(prog_id, "position")
    glVertexAttribPointer(position_loc, 3, GL_FLOAT, GL_FALSE, 0, 
        c_void_p(0))
    glEnableVertexAttribArray(position_loc)
    color_loc = glGetAttribLocation(prog_id, "color")
    if color_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
        glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)
        glVertexAttribPointer(color_loc, 3, GL_FLOAT, GL_FALSE, 0, 
            c_void_p(0))
        glEnableVertexAttribArray(color_loc)
    normal_loc = glGetAttribLocation(prog_id, "normal")
    if normal_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
        glBufferData(GL_ARRAY_BUFFER, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, GL_FALSE, 0, 
            c_void_p(0))
        glEnableVertexAttribArray(normal_loc)
    uv_loc = glGetAttribLocation(prog_id, "uv")
    if uv_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
        glBufferData(GL_ARRAY_BUFFER, uvs, GL_STATIC_DRAW)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(uv_loc)

def main():
    global impl, clear_color
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowPosition(80, 0)
    glutInitWindowSize(1024, 768)
    glutCreateWindow("Phong Lighting Model Exercise")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glEnable(GL_DEPTH_TEST)
    initialize()
    create_shaders()
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