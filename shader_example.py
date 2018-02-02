
from __future__ import print_function, division

from OpenGL import GL, GLUT
import OpenGL.GL.shaders
import ctypes
import types
import numpy
import pyopengltk
import sys
import time
if sys.version_info[0] > 2:
    import tkinter as tk
else:
    import Tkinter as tk

vertex_shader = """
#version 330
in vec3 position;
varying vec3 vertex_color;
uniform mat3 proj;
void main()
{
   gl_Position = vec4( proj*position, 1.0f);
   gl_PointSize = 4.f/(0.5f + length( position ));
   vertex_color = vec3( position.x/2+.5, position.y/2+.5, position.z/2+.5);
}
"""

fragment_shader = """
#version 330
varying vec3 vertex_color;
void main()
{
   gl_FragColor = vec4(vertex_color,0.25f); 
}
"""
NPTS=100000

vertices = (numpy.random.random( NPTS*3 ).astype(numpy.float32)-.5)*1.5
vertices.shape = NPTS,3

def create_object(shader):
    # Create a new VAO (Vertex Array Object) and bind it
    vertex_array_object = GL.glGenVertexArrays(1)
    GL.glBindVertexArray( vertex_array_object )
    # Generate buffers to hold our vertices
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    # Get the position of the 'position' in parameter of our shader and bind it.
    position = GL.glGetAttribLocation(shader, 'position')
    GL.glEnableVertexAttribArray(position)
    # Describe the position data layout in the buffer
    GL.glVertexAttribPointer(position, 3, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))
    # Send the data over to the buffer (bytes)
    vs = vertices.tostring()
    GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vs), vs, GL.GL_STATIC_DRAW)
    # Unbind the VAO first (Important)
    GL.glBindVertexArray( 0 )
    # Unbind other stuff
    GL.glDisableVertexAttribArray(position)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    return vertex_array_object
    
def rot(a,b,c):
    s=numpy.sin(a)
    c=numpy.cos(a)
    am = numpy.array((( c,s,0),(-s,c,0),(0,0,1)), numpy.float32)
    s=numpy.sin(b)
    c=numpy.cos(b)
    bm = numpy.array((( c,0,s),(0,1,0),(-s,0,c)), numpy.float32)
    s=numpy.sin(c)
    c=numpy.cos(c)
    cm = numpy.array((( 1,0,0 ),(0,c,s),(0,-s,c)), numpy.float32)
    return numpy.dot(numpy.dot( am, bm ), cm )


class ShaderFrame(pyopengltk.OpenGLFrame):

    def initgl(self):
        GLUT.glutInit()
        GL.glClearColor(0.15, 0.15, 0.15, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        if not hasattr(self, "shader"):
            self.shader = OpenGL.GL.shaders.compileProgram(
                OpenGL.GL.shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER),
                OpenGL.GL.shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER)
                )
            self.vertex_array_object = create_object(self.shader)
            self.proj = GL.glGetUniformLocation( self.shader, 'proj')
        self.nframes = 0

    def redraw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glUseProgram(self.shader)
        t = time.time()-self.start
        s = 2.
        p = rot(t*s/5.,t*s/6.,t*s/7.)
        GL.glUniformMatrix3fv(self.proj, 1, GL.GL_FALSE, p)
        GL.glBindVertexArray( self.vertex_array_object )
        GL.glDrawArrays(GL.GL_POINTS, 0, NPTS)
        GL.glBindVertexArray( 0 )
        GL.glUseProgram( 0 )
        GL.glRasterPos2f(-0.99,-0.99);
        if self.nframes > 0:
            t = time.time()-self.start
            fps = "fps: %5.2f frames: %d"%(self.nframes / t, self.nframes)
            for c in fps:
                GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(c));
        self.nframes += 1


def main():
    root = tk.Tk()
    app = ShaderFrame(root, width=512,height=512)
    app.start = time.time()
    app.pack(fill=tk.BOTH, expand=tk.YES)
    app.animate=1000//60
    app.mainloop()
if __name__ == '__main__':
    main()
