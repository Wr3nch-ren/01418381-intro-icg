import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd
import imgui
from imgui.integrations.glut import GlutRenderer
from gl_helpers import *
from PIL import Image

win_w, win_h = 1024, 768
Ka, Kd, Ks = [0.01, 0.01, 0.01], [0.86, 0.65, 0.13], [0.8, 0.8, 0.0]
light_intensity = [1, 1, 1]
shininess = 80
blend_factor, clear_color = 0.5, [0.0, 0.1, 0.1]
rot_x, rot_y = 0, 0
uv_translate, uv_rotate, uv_scale = [0, 0], 0, 1

def draw_gui():
    global blend_factor, clear_color, rot_x, rot_y, uv_rotate, uv_scale
    impl.process_inputs()
    imgui.new_frame()                 # Start the Dear ImGui frame 
    imgui.set_next_window_position(win_w-300, 10, imgui.FIRST_USE_EVER)
    imgui.begin("Control")            # Create a window
    imgui.push_item_width(200)
    _, blend_factor = imgui.slider_float("Blend Factor", blend_factor, 0, 1)
    imgui.pop_item_width()
    imgui.text("Texture Coordinate Transform")
    imgui.push_item_width(100)
    _, uv_translate[0] = imgui.slider_float("Translate S###uv_translate_x", uv_translate[0], -1, 1)
    imgui.same_line()
    _, uv_translate[1] = imgui.slider_float("Translate T###uv_translate_y", uv_translate[1], -1, 1)
    _, uv_rotate = imgui.slider_float("Angle Rotation###uv_rotate_x", uv_rotate, -180, 180)
    _, uv_scale = imgui.slider_float("Scale###uv_scale_x", uv_scale, 0.01, 5)
    imgui.pop_item_width()
    imgui.text("Model Rotation")
    imgui.push_item_width(100)
    _, rot_x = imgui.slider_float("Rotate X", rot_x, -180, 180)      
    imgui.same_line()  
    _, rot_y = imgui.slider_float("Rotate Y", rot_y, -180, 180)
    imgui.pop_item_width()
    imgui.text("")      
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)    
    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    impl.set_current_gui_params(imgui.get_window_position(), imgui.get_window_size())        
    imgui.end()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    proj_mat = Perspective(45, w / h, 0.1, 30)
    
def display():
    glClearColor(*clear_color, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    model_mat = Rotate(rot_x, 1, 0, 0) @ Rotate(rot_y, 0, 1, 0)
    view_mat = LookAt(*eye_pos, *centroid, 0, 1, 0)

    glUseProgram(prog_id)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "model_mat"), 1, GL_TRUE, model_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "view_mat"), 1, GL_TRUE, view_mat)
    glUniformMatrix4fv(glGetUniformLocation(prog_id, "proj_mat"), 1, GL_TRUE, proj_mat)
    glUniform3fv(glGetUniformLocation(prog_id, "Ka"), 1, Ka)
    glUniform3fv(glGetUniformLocation(prog_id, "Kd"), 1, Kd)
    glUniform3fv(glGetUniformLocation(prog_id, "Ks"), 1, Ks)
    glUniform3fv(glGetUniformLocation(prog_id, "I"), 1, light_intensity)
    glUniform1f(glGetUniformLocation(prog_id, "shininess"), shininess)
    glUniform3fv(glGetUniformLocation(prog_id, "light_pos"), 1, light_pos)
    glUniform3fv(glGetUniformLocation(prog_id, "eye_pos"), 1, eye_pos)
    glUniform1f(glGetUniformLocation(prog_id, "blend_factor"), blend_factor)
    glUniform2fv(glGetUniformLocation(prog_id, "uv_translate"), 1, uv_translate)
    glUniform1f(glGetUniformLocation(prog_id, "uv_rotate"), uv_rotate)
    glUniform1f(glGetUniformLocation(prog_id, "uv_scale"), uv_scale)
    
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
        os._exit(0)

def idle():
    glutPostRedisplay()

def initialize():
    global impl

    glEnable(GL_DEPTH_TEST)
    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlutRenderer()
    impl.user_keyboard_func(keyboard)
    impl.user_reshape_func(reshape)

def load_texture(filename, active_texture_unit):
    try:
        im = Image.open(filename)
    except:
        print("Error:", sys.exc_info()[0])
    w, h = im.size
    image = im.tobytes("raw", im.mode, 0)
    tex_id = glGenTextures(1)
    glActiveTexture(active_texture_unit)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    
    if im.mode == 'RGBA':
        n_channels = GL_RGBA
        format = GL_RGBA
    else:
        n_channels = GL_RGB
        format = GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, n_channels, w, h, 0, format, GL_UNSIGNED_BYTE, image)
    glGenerateMipmap(GL_TEXTURE_2D)
    glTextureParameteri(tex_id, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE if format == GL_RGBA else GL_REPEAT)
    glTextureParameteri(tex_id, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE if format == GL_RGBA else GL_REPEAT)
    glTextureParameteri(tex_id, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTextureParameteri(tex_id, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return active_texture_unit - GL_TEXTURE0

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
    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global eye_pos, light_pos

    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    vert_code = '''
#version 140
in vec3 position, color, normal;
in vec2 uv;
uniform mat4 model_mat, view_mat, proj_mat;
uniform vec2 uv_translate;
uniform float uv_rotate, uv_scale;
smooth out vec3 vP, vN;
smooth out vec2 bunny_tex_coord, brick_tex_coord;

void main()
{
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);

    vP = (model_mat *  vec4(position, 1)).xyz;
    vN = (transpose(inverse(model_mat)) * vec4(normal,0)).xyz;
    bunny_tex_coord = uv;
    brick_tex_coord = uv + uv_translate;
    brick_tex_coord *= uv_scale;
    float angle = uv_rotate/180*3.14159265358979323846;
    mat2 rot_mat = mat2(cos(angle), sin(angle), -sin(angle), cos(angle));
    brick_tex_coord *= rot_mat;
}'''

    frag_code = '''
#version 140
uniform vec3 Ka, Kd, Ks, I, light_pos, eye_pos;
uniform float shininess, blend_factor;
uniform sampler2D bunny_hair, brick;
smooth in vec3 vP, vN;
smooth in vec2 bunny_tex_coord, brick_tex_coord;
out vec4 frag_color;

void main()
{
    vec3 L = normalize(light_pos - vP);
    vec3 N = normalize(vN);
    vec3 V = normalize(eye_pos - vP);
    vec3 H = normalize(L + V);
    vec3 ambient = Ka * I;
    vec3 tex_color = mix(texture(brick, brick_tex_coord),
                        texture(bunny_hair, bunny_tex_coord),
                        blend_factor).rgb;
    //vec3 diffuse = Kd * max(0, dot(N, L)) * I;
    vec3 diffuse = tex_color * max(0, dot(N, L)) * I; //If texture is too dark
    vec3 specular = Ks * pow(max(0, dot(N, H)), shininess) * I;
    if (dot(N, L) <= 0)
        specular = vec3(0, 0, 0);

    vec3 phong_color = ambient + diffuse + specular;
    
    frag_color.rgb =  phong_color * texture(bunny_hair, bunny_tex_coord).rgb;
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
    glUseProgram(prog_id)

    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global light_pos, eye_pos

    df = pd.read_csv("../models/bunny_uv.tri", delim_whitespace=True, comment='#',
                     header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)
    eye_pos = centroid + (0, 0, 1.5*bbox[0])
    light_pos = eye_pos

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
        
    bunny_unit = load_texture("../texture_map/bunny_hair.jpg", GL_TEXTURE1) # bunny texture
    # bunny_unit = load_texture("../texture_map/black.jpg", GL_TEXTURE1) # dark texture
    brick_unit = load_texture("../texture_map/brick_wall_small.jpg", GL_TEXTURE2)
    loc = glGetUniformLocation(prog_id, "bunny_hair")
    glUniform1i(loc, bunny_unit)
    loc = glGetUniformLocation(prog_id, "brick")
    glUniform1i(loc, brick_unit)
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowPosition(80, 0)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Multitexturing Exercise")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    initialize()
    create_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()