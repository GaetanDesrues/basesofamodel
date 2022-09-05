import logging
import os

import treefiles as tf
from MeshObject import Mesh
from dotenv import load_dotenv

load_dotenv(tf.f(__file__) / ".env")

from SofaModel import BaseScene, BaseModel


class Scene(BaseScene):
    def init(self):
        r = self.root
        p = self.ra

        r.addObject("DefaultAnimationLoop")
        r.addObject("DefaultVisualManagerLoop")

        r.addObject("MeshVTKLoader", filename=p("mesh_out"))

        meca = r.addChild("meca")
        meca.addObject("TetrahedronSetTopologyContainer", name="ct")
        meca.addObject("EulerImplicitSolver")
        meca.addObject("CGLinearSolver")
        meca.addObject("MechanicalObject")

        visu = meca.addChild("visu")
        visu.addObject("VisualModel", src="@../ct", color="#bb0a1e")
        visu.addObject("IdentityMapping")


class Model(BaseModel):
    def set_data_path(self):
        self.params.add("mesh_out", self.out / "mesh.vtk")
        if not tf.isfile(self.params.mesh_out.value):
            Mesh.Sphere().write(self.params.mesh_out.value)


class Params(tf.Params):
    def __init__(self, *items, out=None):
        super().__init__(*items)
        self.add("out_dir", out)
        self.add("n", 10)
        self.add("dt", 1e-2)


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    out = tf.f(__file__, "out").dump()

    print(os.environ["SOFA_ROOT"])

    params = Params(out=out)
    params.n(20)

    model = Model(params, Scene())
    model.run(gui=True)
