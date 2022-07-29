from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import loadPrcFile, GeomNode, WindowProperties, PointLight

from Collapser import Controller, Piece3D, Piece6D

loadPrcFile("conf.prc")
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData, TransparencyAttrib
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter, TextNode
from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import *



def convert_to_vertexes(area: str, row: int, col: int, num_rows: int):
    def get_group(index, max_num=7):
        return index // max_num
    verts_group = []
    verts_flat = []
    for i, cube in enumerate(area):
        if cube == "1":
            x, y, z = get_abs_pos(num_rows, row, col, i)
            verts = get_verts_from_pos(x, y, z)
            verts_group.append(verts)
            verts_flat += verts
    # reduce number of vertexes?
    to_remove = []
    for i, vert in enumerate(verts_flat):
        count = verts_flat.count(vert)
        if count >= 2:
            to_remove.append(i)


def get_verts_from_pos(x, y, z, width=1, height=1, depth=1):
    return [(x, y, z), (x + width, y, z), (x + width, y, z + height),
            (x, y, z + height), (x, y + depth, z), (x + width, y + depth, z),
            (x + width, y + depth, z + height), (x, y + depth, z + height)]


def get_abs_pos(nr, r, c, x):
    """
    Converts from row, column, cell from grid to absolute position x, y, z
    :param nr: number of rows
    :param r: current row
    :param c: current column
    :param x: current cell
    :return: (horizontal pos, depth pos, vertical pos)
    """
    h_pos = c * 3 + (x % 3)
    d_pos = (nr * 3) - (r * 3) - (2 - x // 9)
    v_pos = 2 - int((x % 9) // 3)
    return h_pos, d_pos, v_pos


def create_cube(x, y, z, width=1, height=1, depth=1, colors=None):
    _format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData('cube', _format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, 'color')

    """# front
    vertex.addData3(x, y, z)  # 0 blf
    vertex.addData3(x + width, y, z)  # 1 brf
    vertex.addData3(x + width, y, z + height)  # 2 trf
    vertex.addData3(x, y, z + height)  # 3 tlf

    # back
    vertex.addData3(x, y + depth, z)  # 4  blb
    vertex.addData3(x + width, y + depth, z)  # 5 brb
    vertex.addData3(x + width, y + depth, z + height)  # 6 trb
    vertex.addData3(x, y + depth, z + height)  # 7 tlb"""
    vertex_data = get_verts_from_pos(x, y, z, width, height, depth)
    for vert in vertex_data:
        vertex.addData3(vert)

    if colors:
        if len(colors) < 4:
            colors = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        for i in range(8):
            color.addData4f(colors)
    else:
        for i in range(2):
            color.addData4f(1.0, 0.0, 0.0, 1.0)
            color.addData4f(0.0, 1.0, 0.0, 1.0)
            color.addData4f(0.0, 0.0, 1.0, 1.0)
            color.addData4f(1.0, 1.0, 1.0, 1.0)

    tris = GeomTriangles(Geom.UHDynamic)
    # front
    tris.addVertices(0, 1, 2)
    tris.addVertices(2, 3, 0)

    # right
    tris.addVertices(5, 2, 1)
    tris.addVertices(5, 6, 2)

    # left
    tris.addVertices(0, 3, 4)
    tris.addVertices(4, 3, 7)

    # back
    tris.addVertices(6, 5, 4)
    tris.addVertices(6, 4, 7)

    # top
    tris.addVertices(6, 3, 2)
    tris.addVertices(7, 3, 6)

    # bottom
    tris.addVertices(4, 1, 0)
    tris.addVertices(5, 1, 4)

    cube = Geom(vdata)
    cube.addPrimitive(tris)
    return cube


def create_colored_rect(x, z, width, height, colors=None):
    _format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData('square', _format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, 'color')

    vertex.addData3(x, 0, z)
    vertex.addData3(x + width, 0, z)
    vertex.addData3(x + width, 0, z + height)
    vertex.addData3(x, 0, z + height)

    if colors:
        if len(colors) < 4:
            colors = (1.0, 1.0, 1.0, 1.0)
        color.addData4f(colors)
        color.addData4f(colors)
        color.addData4f(colors)
        color.addData4f(colors)
    else:
        color.addData4f(1.0, 0.0, 0.0, 1.0)
        color.addData4f(0.0, 1.0, 0.0, 1.0)
        color.addData4f(0.0, 0.0, 1.0, 1.0)
        color.addData4f(1.0, 1.0, 1.0, 1.0)

    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 2)
    tris.addVertices(2, 3, 0)

    square = Geom(vdata)
    square.addPrimitive(tris)
    return square


keyMap = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "vert": False,
    "vert_down": False,
    "esc": False
}


def updateKeyMap(key, state):
    global keyMap
    keyMap[key] = state
    # print(keyMap)


def toggleKeyMap(key):
    keyMap[key] = not keyMap[key]


class Visualizer(ShowBase):
    def __init__(self, collapser: Controller):
        super().__init__()
        self.disable_mouse()
        self.props = WindowProperties()
        self.props.setCursorHidden(True)
        self.props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(self.props)
        mid_x = collapser.grid.rows * 3 // 2
        mid_y = collapser.grid.cols * 3 // 2
        self.cam.setPos(mid_x, mid_y, 12)
        if collapser.is6D:
            self.a = 0
            self.b = 0
            self.c = 0

            self.pos_6d = OnscreenText(
                text=self._format_6d_pos(),
                pos=(-1.5, 0.75)
            )

        plight = PointLight("plight")
        plight.setColor((1, 1, 1, 1))
        self.plnp = self.render.attachNewNode(plight)
        self.plnp.setPos(mid_x, mid_y, 30)
        self.render.setLight(self.plnp)
        # self.light_model = self.loader.loadModel('models/misc/sphere')
        # self.light_model.setScale(0.2, 0.2, 0.2)
        # self.light_model.reparentTo(self.plnp)

        self.collapser = collapser
        # self.collapser.grid.collapse_random_cell()
        self.collapser.collapse()
        self.visualize_grid()
        self.accept("delete", self.update_grid)
        # self.accept("arrow_left", self.reset)
        if collapser.is6D:
            self.accept("arrow_up", self.move_6D, ["up"])
            self.accept("arrow_down", self.move_6D, ["down"])
            self.accept("arrow_right", self.move_6D, ["right"])
            self.accept("arrow_left", self.move_6D, ["left"])
            self.accept("-", self.move_6D, ["backward"])
            self.accept("+", self.move_6D, ["forward"])

        self.accept("w", updateKeyMap, ["up", True])
        self.accept("a", updateKeyMap, ["left", True])
        self.accept("s", updateKeyMap, ["down", True])
        self.accept("d", updateKeyMap, ["right", True])
        self.accept("space", updateKeyMap, ["vert", True])
        self.accept("shift-space", updateKeyMap, ["vert_down", True])
        self.accept("escape", toggleKeyMap, ["esc"])

        self.accept("w-up", updateKeyMap, ["up", False])
        self.accept("a-up", updateKeyMap, ["left", False])
        self.accept("s-up", updateKeyMap, ["down", False])
        self.accept("d-up", updateKeyMap, ["right", False])
        self.accept("space-up", updateKeyMap, ["vert", False])
        self.accept("shift-up", updateKeyMap, ["vert_down", False])
        self.timer = 0
        self.stop_timer = False
        self.speed = 30
        self.angle_h = 0
        self.angle_p = 0
        # self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.update_key, "update")

        self.protected_objs = ["render/" + x for x in [self.camera.name, self.plnp.name]]
        print(self.protected_objs)

    def _format_6d_pos(self):
        return f"A:{self.a + 1}\nB:{self.b + 1}\nC:{self.c + 1}"

    def move_6D(self, key):
        if self.collapser.is6D:
            def clamp(num):
                return max([min([2, num]), 0])

            if key == "up":
                self.b += 1
            elif key == "down":
                self.b -= 1
            elif key == "right":
                self.a += 1
            elif key == "left":
                self.a -= 1
            elif key == "forward":
                self.c += 1
            elif key == "backward":
                self.c -= 1

            self.a = clamp(self.a)  # horizontal
            self.b = clamp(self.b)  # vertical
            self.c = clamp(self.c)  # depth

            self.clear()
            self.visualize_grid()

            self.pos_6d.setText(self._format_6d_pos())

    def reset(self):
        self.collapser.reset()
        self.clear()

    def clear(self):
        for child in self.render.children:
            if str(child) not in self.protected_objs:
                print(str(child))
                child.remove_node()

    def update_grid(self):
        self.reset()
        self.collapser.collapse()
        self.visualize_grid()
        """
        stop = self.collapser.grid.collapse_next_cell()
        self.visualize_grid()
        self.stop_timer = stop"""

    def update(self, task):  # not using right now
        dt = globalClock.getDt()
        if not self.stop_timer:
            self.timer += dt
            if self.timer >= 0.5:
                self.update_grid()
                self.timer = 0
        return task.cont

    def update_key(self, task):
        dt = globalClock.getDt()
        x, y = 0, 0
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
        # print(self.cam.getPos())
        if not keyMap["esc"]:
            if not self.props.cursor_hidden:
                self.props.setCursorHidden(True)
                self.win.requestProperties(self.props)
                x, y = 0, 0
            self.angle_h -= x * 180
            self.angle_p += y * 60
            self.angle_p = max(min(self.angle_p, 90), -90)  # clamp from -90 to 90 degrees FOV
            if abs(self.angle_h) >= 720:  # keeps the numbers from getting too big
                self.angle_h -= (720 * (self.angle_h / abs(self.angle_h)))
            self.cam.setH(self.angle_h)
            self.cam.setP(self.angle_p)
            self.cam.setR(self.cam, -self.cam.getR())
            self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
        else:
            if self.props.cursor_hidden:
                self.props.setCursorHidden(False)
                self.win.requestProperties(self.props)

        lr, fb, ud = 0, 0, 0

        if keyMap["left"]:
            lr -= self.speed * dt
        elif keyMap["right"]:
            lr += self.speed * dt

        if keyMap["up"]:
            fb += self.speed * dt
        elif keyMap["down"]:
            fb -= self.speed * dt

        if keyMap["vert"]:
            ud += self.speed * dt
        elif keyMap["vert_down"]:
            ud -= self.speed * dt

        self.cam.setPos(self.cam, lr, fb, ud)

        return task.cont

    def visualize_grid(self):

        grid = self.collapser.grid.grid
        cube = GeomNode(f"map")
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if isinstance(grid[row][col], Piece3D):
                    piece_geom = []
                    for i in range(len(grid[row][col].data)):
                        if grid[row][col].data[i] == "1":
                            color = grid[row][col].color
                            horizontal_pos, depth_pos, vertical_pos = get_abs_pos(len(grid), row, col, i)
                            piece_geom.append(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
                            # cube.addGeom(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
                    [cube.addGeom(x) for x in piece_geom]
                elif isinstance(grid[row][col], Piece6D):
                    piece_3d = grid[row][col]["data_6D"][(self.b * 3) + (self.c * 9) + self.a]
                    piece_geom = []
                    for i, ele in enumerate(piece_3d.data):
                        if piece_3d.data[i] == "1":
                            color = piece_3d.color
                            horizontal_pos, depth_pos, vertical_pos = get_abs_pos(len(grid), row, col, i)
                            piece_geom.append(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
                            # cube.addGeom(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
                    [cube.addGeom(x) for x in piece_geom]
        self.render.attachNewNode(cube)

    """def visualize_grid(self):
        def get_pos(g, r, c, x):
            h_pos = c * 3 + (x % 3)
            d_pos = (len(g) * 3) - (r * 3) - (2 - x // 9)
            v_pos = 2 - int((x % 9) // 3)
            return h_pos, d_pos, v_pos
        grid = self.collapser.grid.grid
        cube = GeomNode(f"map")
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if isinstance(grid[row][col], Piece3D):
                    for i in range(len(grid[row][col].data)):
                        if grid[row][col].data[i] == "1":
                            color = grid[row][col].color
                            horizontal_pos, depth_pos, vertical_pos = get_pos(grid, row, col, i)
                            cube.addGeom(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
                elif isinstance(grid[row][col], Piece6D):
                    piece_3d = grid[row][col]["data_6D"][(self.b * 3) + (self.c * 9) + self.a]
                    for i, ele in enumerate(piece_3d.data):
                        if piece_3d.data[i] == "1":
                            color = piece_3d.color
                            horizontal_pos, depth_pos, vertical_pos = get_pos(grid, row, col, i)
                            cube.addGeom(create_cube(horizontal_pos, depth_pos, vertical_pos, 1, 1, 1, color))
        self.render.attachNewNode(cube)"""
