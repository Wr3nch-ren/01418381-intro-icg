#รหัสนิสิต 6410406541 ชื่อ-นามสกุล ชินพัฒน์ ฟองอ่อน
#ระบุข้อกำหนดของงานที่เลือกทำ (โดยระบุเพียงหมายเลข) 1, 2, 3, 4
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
win_w, win_h = 1280, 800
shininess = 50
Ka, Kd, Ks, bKd = [0.05, 0.05, 0.05], [0.83, 0.69, 0.22], [0.9, 0.9, 0.9], [0.22, 0.69, 0.83]
clear_color = [0, 0.45, 0.45]
I, light_pos, eye_pos, eye_at = [1, 1, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0]
rot_x, rot_y, use_blinn_specular, two_sided_lighting = 30, 30, False, False

def draw_gui():
    global I, Ka, Kd, bKd, Ks, shininess, clear_color
    global rot_x, rot_y, use_blinn_specular, two_sided_lighting

    impl.process_inputs()
    imgui.new_frame()                 # Start the Dear ImGui frame 
    imgui.set_next_window_position(win_w-450, 10, imgui.FIRST_USE_EVER)
    imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
    imgui.begin("Control")            # Create a window
    imgui.push_item_width(300)
    _, I = imgui.color_edit3("Light Intensity", *I)
    _, Ka = imgui.color_edit3("Ka", *Ka)
    _, Kd = imgui.color_edit3("Front Kd", *Kd)
    _, bKd = imgui.color_edit3("Back Kd", *bKd)
    _, Ks = imgui.color_edit3("Ks", *Ks)
    _, shininess = imgui.slider_float("Shininess", shininess, 0.5, 128)    
    _, two_sided_lighting = imgui.checkbox("Two-Sided Enabled", two_sided_lighting)    
    imgui.same_line()
    if imgui.radio_button("Phong Specular", not use_blinn_specular): 
        use_blinn_specular = False
        create_shaders()
    imgui.same_line()
    if imgui.radio_button("Blinn Specular", use_blinn_specular): 
        use_blinn_specular = True
        create_shaders()
    imgui.text("Light Position")
    imgui.push_item_width(100)
    _, light_pos[0] = imgui.slider_float("X###light_pos_x", light_pos[0], -5, 5)
    imgui.same_line()
    _, light_pos[1] = imgui.slider_float("Y###light_pos_y", light_pos[1], -5, 5)
    imgui.same_line()
    _, light_pos[2] = imgui.slider_float("Z###light_pos_z", light_pos[2], centroid[2]-5*bbox[2], centroid[2]+5*bbox[2])
    imgui.text("Eye Position")
    _, eye_pos[0] = imgui.slider_float("X###eye_pos_x", eye_pos[0], -5, 5)
    imgui.same_line()
    _, eye_pos[1] = imgui.slider_float("Y###eye_pos_y", eye_pos[1], -5, 5)
    imgui.same_line()
    _, eye_pos[2] = imgui.slider_float("Z###eye_pos_z", eye_pos[2], centroid[2]-5*bbox[2], centroid[2]+5*bbox[2])
    imgui.text("Model Rotation")
    _, rot_x = imgui.slider_float("Rotate X", rot_x, -180, 180) 
    imgui.same_line()   
    _, rot_y = imgui.slider_float("Rotate Y", rot_y, -180, 180)    
    imgui.pop_item_width()
    imgui.text("")
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    imgui.end()    

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    proj_mat = Perspective(45, w/h, 0.1, 100)
    
def display():
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    model_mat = Rotate(rot_y, 0, 1, 0) @ Rotate(rot_x, 1, 0, 0)
    view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)

    glUseProgram(prog_id)        
    glUniformMatrix4fv(glGetUniformLocation(prog_id, 'model_mat'), 1, GL_TRUE, model_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, 'view_mat'), 1, GL_TRUE, view_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, 'proj_mat'), 1, GL_TRUE, proj_mat)
    glUniform3fv(glGetUniformLocation(prog_id, 'I'), 1, I)
    glUniform3fv(glGetUniformLocation(prog_id, 'light_pos'), 1, light_pos)
    glUniform3fv(glGetUniformLocation(prog_id, 'eye_pos'), 1, eye_pos)
    glUniform3fv(glGetUniformLocation(prog_id, 'Ka'), 1, Ka)
    glUniform3fv(glGetUniformLocation(prog_id, 'Kd'), 1, Kd)
    glUniform3fv(glGetUniformLocation(prog_id, 'bKd'), 1, bKd)
    glUniform3fv(glGetUniformLocation(prog_id, 'Ks'), 1, Ks)
    glUniform1f(glGetUniformLocation(prog_id, 'shininess'), shininess)
    glUniform1i(glGetUniformLocation(prog_id, 'two_sided_lighting'), two_sided_lighting)
    glUniform1i(glGetUniformLocation(prog_id, 'use_blinn_specular'), use_blinn_specular)

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
    global prog_id, vao, vao

    vert_code = '''
#version 140
in vec3 position, normal, color;
in vec2 uv;
uniform mat4 model_mat, view_mat, proj_mat;
// uniform vec3 I, light_pos, eye_pos, Ka, Kd, bKd, Ks;
// uniform float shininess;
// uniform bool two_sided_lighting, use_blinn_specular;
// out vec3 fcolor;
out vec3 fP, fN;
void main()
{
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);
    fP = (view_mat * model_mat * vec4(position, 1)).xyz;
    fN = (view_mat * model_mat * vec4(normal, 0)).xyz;
}'''

    frag_code = '''
#version 140
uniform vec3 I, light_pos, eye_pos, Ka, Kd, bKd, Ks;
uniform float shininess;
uniform bool two_sided_lighting, use_blinn_specular;
// in vec3 fcolor;
in vec3 fP,fN;
void main()
{
    vec3 L = normalize(light_pos - fP);
    vec3 V = normalize(eye_pos - fP);
    vec3 N = normalize(fN);
    vec3 R = 2 * dot(L, N) * N - L;
    vec3 ambient = Ka * I;
    vec3 diffuse;
    vec3 specular;
    if (two_sided_lighting){
        if (dot(N, L) > 0){
            diffuse = Kd * max(dot(N, L), 0) * I;
            }
        else{
            diffuse = bKd * max(dot(-N, L), 0) * I;
            }
        }
    else {
        diffuse = Kd * max(dot(N, L), 0) * I;
    }
    if (use_blinn_specular){
        vec3 H = normalize(L + V);
        specular = Ks * pow(max(dot(N, H), 0), shininess) * I;
    }
    else{
        specular = Ks * pow(max(dot(V, R), 0), shininess) * I;
    }
   gl_FragColor.rgb = ambient + diffuse + specular;
}'''

    vert_id = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vert_id, vert_code)
    glCompileShader(vert_id)
    print_shader_info_log(vert_id, "Vertex Shader")

    frag_id = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(frag_id, frag_code)
    glCompileShader(frag_id)
    print_shader_info_log(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    print_program_info_log(prog_id, "Link error")

    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global light_pos, eye_pos, eye_at

    df = pd.read_csv("../models/teapot_culling.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)
    light_pos = centroid + (0, 0, 5)
    eye_pos = centroid + (0, 0, 2) + (0.3, 0, 0)
    eye_at = centroid.copy() + (0.3, 0, 0)

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
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Per-Fragment Lighting Lab")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glEnable(GL_DEPTH_TEST)
    initialize()
    create_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()