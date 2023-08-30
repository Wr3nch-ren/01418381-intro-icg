from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd

prog_id = None

def printShaderInfoLog(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        exit()

def printProgramInfoLog(program, prompt=""):
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(program).decode("utf-8")))
        exit()

def compileProgram(vertex_code, fragment_code):
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vert_id, vertex_code)
    glCompileShader(vert_id)
    printShaderInfoLog(vert_id, "Vertex Shader")

    frag_id = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(frag_id, fragment_code)
    glCompileShader(frag_id)
    printShaderInfoLog(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)
    glLinkProgram(prog_id)
    printProgramInfoLog(prog_id, "Link Program")

    return prog_id

def gl_init():
    global prog_id, n_vertices, positions, colors, normals, uvs, centroid, bbox

    glEnable(GL_DEPTH_TEST)

    vert_code = '''
#version 120
varying vec3 teapot_color;
uniform vec3 bunny_color;
void main()
{
    float angle = 2 * length(gl_Vertex.xy);

    float s = sin(angle);

    float c = cos(angle);

    gl_Position.x = c * gl_Vertex.x - s * gl_Vertex.y;

    gl_Position.y = s * gl_Vertex.x + c * gl_Vertex.y;

    gl_Position.z = 0.0;

    gl_Position.w = 1.0;

    //gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
    
    teapot_color = 0.5*(gl_Normal + 1);
}
                '''
    frag_code = ''' 
#version 120
varying vec3 teapot_color;
void main()
{
    gl_FragColor.rgb = teapot_color;
}
                '''                
    prog_id = compileProgram(vert_code, frag_code)

    df = pd.read_csv("../models/bunny_uv.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    n_vertices = len(df.values)
    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    print("no. of vertices: %d, no. of triangles: %d" % 
          (n_vertices, n_vertices//3))
    print("Centroid:", centroid)
    print("BBox:", bbox)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 800/600, 0.01, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)
    glUseProgram(prog_id)

    location = glGetUniformLocation(prog_id, "bunny_color")
    glUniform3fv(location, 1, [0.5, 0.5, 0])

    glVertexPointer(3, GL_FLOAT, 0, positions)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glNormalPointer(GL_FLOAT, 0, normals)
    glTexCoordPointer(2, GL_FLOAT, 0, uvs)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)     
    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(50, 50)    
    glutCreateWindow("GLSL Shaders Exercise")
    glutDisplayFunc(display)
    gl_init()
    glutMainLoop()

if __name__ == "__main__":
    main()    