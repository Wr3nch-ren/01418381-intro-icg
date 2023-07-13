from OpenGL.GL import *
from glfw.GLFW import *
  
def display_cb():
    glClearColor(0, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-0.5, -0.5, 0)
    glVertex3f( 0.5, -0.5, 0)
    glVertex3f( 0, 0.5, 0)
    glEnd()
    glFlush()

def main():
    if not glfwInit():
        glfwTerminate()
        os._exit()

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_FALSE)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_COMPAT_PROFILE)
    window = glfwCreateWindow(800, 600, "A Simple GLFW Program", None, None)
    glfwMakeContextCurrent(window)
    show_versions()

    while not glfwWindowShouldClose(window):
        display_cb()
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()