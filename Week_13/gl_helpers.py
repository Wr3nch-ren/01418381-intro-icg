from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from numpy import array, ndarray, zeros, dot, cross
from numpy import float32, identity, matrix
from numpy.linalg import norm
from math import sqrt, sin, cos, tan, acos, pi
from PIL import Image

mat_map = {5888: GL_MODELVIEW_MATRIX, 5889: GL_PROJECTION_MATRIX}

def Identity():
    return array(((1, 0, 0, 0),
                  (0, 1, 0, 0),
                  (0, 0, 1, 0),
                  (0, 0, 0, 1)), dtype=float32)
    
def normalize(v):
    l = norm(v)
    if l == 0:
        return v
    else:
        return v/l
    
def Translate(tx, ty, tz):
    return array(((1, 0, 0, tx),
                  (0, 1, 0, ty),
                  (0, 0, 1, tz),
                  (0, 0, 0, 1)), dtype=float32)
    
def Scale(sx, sy, sz):
    return array(((sx, 0, 0, 0),
                  (0, sy, 0, 0),
                  (0, 0, sz, 0),
                  (0, 0, 0, 1)), dtype=float32)

def Rotate(angle, x, y, z):
    l = sqrt(x*x + y*y + z*z) # norm((x, y, z))
    x, y, z = x/l, y/l, z/l
    c, s = cos(angle*pi/180), sin(angle*pi/180)
    return array(((x*x*(1-c)+c, x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0),
                  (y*x*(1-c)+z*s, y*y*(1-c)+c, y*z*(1-c)-x*s, 0),
                  (x*z*(1-c)-y*s, y*z*(1-c)+x*s, z*z*(1-c)+c, 0),
                  (0, 0, 0, 1)), dtype=float32)
    
def LookAt(eyex, eyey, eyez, atx, aty, atz, upx, upy, upz):
    z = normalize(array((eyex-atx, eyey-aty, eyez-atz), dtype=float32))
    y = normalize(array((upx, upy, upz), dtype=float32))
    x = normalize(cross(y, z))
    y = cross(z, x)
    return array(((x[0], x[1], x[2], -dot(x, array((eyex, eyey, eyez)))),
                  (y[0], y[1], y[2], -dot(y, array((eyex, eyey, eyez)))),
                  (z[0], z[1], z[2], -dot(z, array((eyex, eyey, eyez)))),
                  (0, 0, 0, 1)), dtype=float32)
    
def Perspective(fovy, aspect, near, far):
    f = 1/tan(fovy*pi/360) # cot(fovy/2)
    return array(((f/aspect, 0, 0, 0),
                  (0, f, 0, 0),
                  (0, 0, (far+near)/(near-far), 2*far*near/(near-far)),
                  (0, 0, -1, 0)), dtype=float32)
    
def Frustum(left, right, bottom, top, near, far):
    return array(((2*near/(right-left), 0, (right+left)/(right-left), 0),
                  (0, 2*near/(top-bottom), (top+bottom)/(top-bottom), 0),
                  (0, 0, (far+near)/(near-far), 2*far*near/(near-far)),
                  (0, 0, -1, 0)), dtype=float32)
    
def Ortho(left, right, bottom, top, near, far):
    return array(((2/(right-left), 0, 0, -(right+left)/(right-left)),
                  (0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)),
                  (0, 0, 2/(near-far), -(near+far)/(near-far)),
                  (0, 0, 0, 1)), dtype=float32)