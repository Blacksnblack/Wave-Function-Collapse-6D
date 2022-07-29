from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import loadPrcFile, GeomNode, WindowProperties, PointLight

loadPrcFile("conf.prc")

from direct.showbase.ShowBase import ShowBase
from Collapser import Controller
from panda3d.core import NodePath


class Visualizer(ShowBase):
    def __init__(self, fcollapser=None):
        super().__init__()
        self.cam.setPos(0, -40, 5)

        env = self.loader.loadModel("obj_final.bam")
        # print(env.children)
        objs = []
        for i, obj in enumerate(env.children):
            print(obj.name)
            # obj.reparentTo(self.render)
            obj.setPos((i % 3) * 5, ((i // 3) * 5), 0)
            objs.append(obj)
        objs[0].setPos(0, 0, 0)
        objs[0].reparentTo(self.render)
        objs[0].setColorScale(1.0, 0.0, 0.0, 1.0)

        objs[1].setPos(3, 3, 0)
        objs[1].reparentTo(self.render)
        objs[1].setColorScale(0.0, 1.0, 0.0, 1.0)

        print(self.render.children)

        plight = PointLight("plight")
        plight.setColor((1, 1, 1, 1))
        self.plnp = self.render.attachNewNode(plight)
        self.plnp.setPos(0, 0, 15)
        self.render.setLight(self.plnp)
        self.light_model = self.loader.loadModel('models/misc/sphere')
        self.light_model.setScale(0.2, 0.2, 0.2)
        self.light_model.reparentTo(self.plnp)

