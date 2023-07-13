from OpenGL.GL import *
from glfw.GLFW import *
import imgui
from imgui.integrations.glfw import GlfwRenderer

clear_color = [0, 1, 1] 

def display_cb():
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-0.5, -0.5, 0)
    glVertex3f( 0.5, -0.5, 0)
    glVertex3f( 0, 0.5, 0)
    glEnd()
    glFlush()

def keyboard_cb(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

def main():
    global clear_color

    if not glfwInit():
        glfwTerminate()
        os._exit()

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_FALSE)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_COMPAT_PROFILE)
    window = glfwCreateWindow(800, 600, "A Simple GLFW Program with ImGui", None, None)
    glfwMakeContextCurrent(window)
    show_versions()

    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlfwRenderer(window)
    glfwSetKeyCallback(window, keyboard_cb)
    imgui.set_next_window_position(500, 10)
    imgui.set_next_window_collapsed(True)
    check_box_val1 = True
    check_box_val2 = False
    float_val = 50

    while not glfwWindowShouldClose(window):
        glfwPollEvents()
        impl.process_inputs()
        
        imgui.new_frame()                    # Start the Dear ImGui frame   
        imgui.begin("Control")               # Create a window
        imgui.text("This is some useful text.")
        _, check_box_val1 = imgui.checkbox("Box 1", check_box_val1)
        _, check_box_val2 = imgui.checkbox("Box 2", check_box_val2)
        _, float_val = imgui.slider_float("Intensity", float_val, 0, 100)
        _, clear_color = imgui.color_edit3("Clear Color", *clear_color)

        imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
            (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
        imgui.end()
        
        display_cb()
        imgui.render()
        impl.render(imgui.get_draw_data())

        glfwSwapBuffers(window)

    impl.shutdown()
    glfwTerminate()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()