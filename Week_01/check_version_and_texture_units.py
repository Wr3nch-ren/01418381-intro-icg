from OpenGL.GL import *
from OpenGL.GLUT import *
  
def draw():
	pass

glutInit([])
glutCreateWindow("Version Check")
glutDisplayFunc(draw)

lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
         ['OpenGL Version', GL_VERSION],
         ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
for x in lists:
    print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

unit_count = glGetIntegerv(GL_MAX_TEXTURE_UNITS)
print("Number of texture units = %d" % unit_count)