import io
import logging
from datetime import datetime
from typing import Optional

import treefiles as tf


class BaseScene:
    def __init__(self):
        self.ra = None
        self.root = None
        self.controller = None

    def real_init(self, root, params):
        self.ra = lambda x: params[x].value
        self.root = root
        self.root.findData("dt").value = self.ra("dt")
        self.root.findData("gravity").value = [0, 0, 0]
        # self.root.addObject("APIVersion", level="22.06.00")

        self.controller: Optional["SOFAControl"] = None

    def init(self):
        pass


PLUGINS = {
    "Sofa.Component.ODESolver.Backward",
    "Sofa.GL.Component.Rendering3D",
    "Sofa.GL.Component.Rendering2D",
    "Sofa.GL.Component.Shader",
}


class BaseModel:
    PLUGINS = PLUGINS

    def save_params(self):
        tf.dump_json(
            self.params.out_dir / "params.json",
            self.params.to_dict(),
            cls=tf.JsonEncoder,
        )

    def __init__(self, params: tf.Params, scene: Optional[BaseScene] = None):
        self.plugins = self.PLUGINS
        self.params = params if isinstance(params, tf.Params) else tf.Params(params)
        self.root = None
        self.scene = scene

        if "n" not in self.params:
            log.warning("Iteration number not set, defaulting to n=10")
            self.params["n"] = tf.Param("n", 10)

        if "dt" not in self.params:
            log.warning("Time step not set, defaulting to dt=1e-2")
            self.params["dt"] = tf.Param("dt", 1e-2)

        if "out_dir" not in self.params:
            log.warning(
                f"Output path not set, defaulting to out_dir={tf.f(__file__, 'out')}"
            )
            self.params["out_dir"] = tf.Param("out_dir", tf.f(__file__) / "out")

        self.out = tf.dump(self.params["out_dir"].value)
        log.info(f"Creating SOFA simulation to file://{self.out.abs()}")

        self.set_data_path()  # add path related params
        self.init()

    def init_scene(self):
        """
        graph: create_graph(root: Node, params: tf.TParams)
        """
        from Sofa import Simulation
        from Sofa.Core import Node
        import SofaRuntime
        # from SofaRuntime.SofaRuntime import importPlugin

        self.root = Node("root")

        SofaRuntime.PluginRepository.addFirstPath(tf.env("SOFA_ROOT") / "lib")
        # SofaRuntime.DataRepository.addFirstPath(tf.env("SOFA_ROOT") / "bin")

        SofaRuntime.importPlugin("SofaImplicitOdeSolver")
        SofaRuntime.importPlugin("Sofa.Component.ODESolver.Backward")
        self.root.addObject("RequiredPlugin", name="SofaImplicitOdeSolver")

        # for x in self.plugins:
        #     SofaRuntime.importPlugin(x)
        #     # self.root.addObject("RequiredPlugin", name=x)

        # self.scene = self.scene_class(self.root, self.params)
        self.scene.real_init(self.root, self.params)
        self.scene.init()
        Simulation.init(self.root)

    def set_data_path(self):
        pass

    def print_scene(self):
        from Sofa import Simulation

        Simulation.print(self.root)

    def init(self):
        pass

    @tf.timer
    def run(self, gui: bool = False, std_to_file: bool = False):
        from Model3D.basesofamodel.load_SOFA import load_SOFA

        load_SOFA()
        from Sofa import Simulation

        log.info(f"Starting Model at file://{self.params.out_dir.value}")

        self.save_params()

        if gui:
            from Sofa.Gui import GUIManager

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
                out = self.params.out_dir / "Output_Python.stdout"
                err = self.params.out_dir / "Error_Python.stderr"

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
