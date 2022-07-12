import io
import logging
from datetime import datetime
from typing import Type, Optional

import treefiles as tf

from basesofamodel.load_SOFA import load_SOFA

load_SOFA()
from Sofa import Simulation
from Sofa.Core import Node, Controller
from Sofa.Gui import GUIManager
from SofaRuntime.SofaRuntime import importPlugin


class SOFAControl(Controller):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.root = root
        self.data = []
        self.out = kw.pop("out", None)

    def export(self):
        pass

    def onAnimateBeginEvent(self, event):
        if self.root.time.value == 0:
            self.export()

    def onAnimateEndEvent(self, event):
        self.export()

    def get(self, path, data):
        try:
            obj = self.root[path].findData(data).value
        except:
            return
        return obj

    def set(self, path, data, value):
        try:
            self.root[path].findData(data).value = value
        except:
            return

    # def onAnimateEndEvent(self, event):
    #     V = self.root["APIVersion"].findData("level").value
    #     print("onAnimateBeginEvent", event, V)


class BaseScene:
    def __init__(self, root, params):
        self.ra = lambda x: params[x].value
        self.root = root
        self.root.findData("dt").value = self.ra("dt")
        self.root.findData("gravity").value = [0, 0, 0]
        self.root.addObject("APIVersion", level="21.12.00")

        self.controller: Optional[SOFAControl] = None

    def init(self):
        pass


PLUGINS = {
    "SofaImplicitOdeSolver",
    "SofaExporter",
    "SofaOpenglVisual",
    "SofaDenseSolver",
    "SofaGraphComponent",
    "SofaSimpleFem",
    "SofaDeformable",
    "SofaEngine",
    "SofaGeneralLoader",
    "SofaMeshCollision",
    "SofaPreconditioner",
    "SofaBoundaryCondition",
    "SofaConstraint",
    "SofaMiscFem",
    # "SofaCaribou",
}


class BaseModel:
    PLUGINS = PLUGINS

    def save_params(self):
        tf.dump_json(self.params.out.value / "params.json", self.params.to_dict())

    def __init__(self, params: tf.Params, scene_class: Type[BaseScene] = None):
        self.plugins = self.PLUGINS
        self.params = tf.Params(params)
        self.root = None
        self.scene_class = scene_class
        self.scene: Optional[BaseScene] = None

        if "n" not in self.params:
            log.warning("Iteration number not set, defaulting to n=10")
            self.params["n"] = tf.Param("n", 10)

        if "dt" not in self.params:
            log.warning("Time step not set, defaulting to dt=1e-2")
            self.params["dt"] = tf.Param("dt", 1e-2)

        if "out" not in self.params:
            log.warning(
                f"Output path not set, defaulting to out={tf.f(__file__, 'out')}"
            )
            self.params["out"] = tf.Param("out", tf.f(__file__, "out"))

        self.out = tf.dump(self.params["out"].value)
        log.info(f"Creating SOFA simulation to file://{self.out.abs()}")

        self.set_data_path()  # add path related params
        self.init()

    def init_scene(self):
        """
        graph: create_graph(root: Node, params: tf.TParams)
        """
        for x in self.plugins:
            importPlugin(x)

        self.root = Node("root")
        self.scene = self.scene_class(self.root, self.params)
        self.scene.init()
        Simulation.init(self.root)

    def set_data_path(self):
        pass

    def print_scene(self):
        Simulation.print(self.root)

    def init(self):
        pass

    @tf.timer
    def run(self, gui: bool = False, std_to_file: bool = False):
        if gui:
            self.init_scene()
            GUIManager.Init("")
            GUIManager.createGUI(self.root, __file__)
            GUIManager.SetDimension(900, 700)
            gui = GUIManager.GetGUI()
            gui.setBackgroundImage(tf.f(__file__) / "SOFA_logo_white.dds"),
            GUIManager.MainLoop(self.root)
            GUIManager.closeGUI()
            tf.removeIfExists(self.out.p / "lastUsedGUI.ini")
            tf.removeIfExists(self.out.p / "runSofa.ini")
        else:
            log.info(f"Starting SOFA for {self.params.n.value} iterations")

            if std_to_file:
                out = self.params.out / "Output_Python.stdout"
                err = self.params.out / "Error_Python.stderr"

                fo, fe = open(out, "w"), open(err, "w")
                fob, feb = io.BytesIO(), io.BytesIO()
                with tf.stdout_redirector(fob):
                    with tf.stderr_redirector(feb):
                        self.init_scene()
                        print(f"Starting {self.params.n.value} iterations")
                        for i in range(self.params.n.value):
                            print(
                                f"{datetime.now()}: Iterations {i+1}/{self.params.n.value}"
                            )
                            Simulation.animate(self.root, self.params.dt.value)
                fo.write(fob.getvalue().decode("utf-8"))
                fe.write(feb.getvalue().decode("utf-8"))
                fo.close()
                fe.close()
            else:
                self.init_scene()
                for _ in range(self.params.n.value):
                    Simulation.animate(self.root, self.params.dt.value)


log = logging.getLogger(__name__)
