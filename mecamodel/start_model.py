import logging

import treefiles as tf
from Model3D import Analyser

from basesofamodel.base_model import BaseModel
from mecamodel.main_scene import MecaScene


class MecaModel(BaseModel):
    def plot(self):
        an = Analyser(self.params.out.value)
        an.get_features()
        an.left.plot_raw()


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    ps = tf.load_json(tf.f(__file__) / "case_1/params.json")
    params = tf.Params.from_dict(ps)

    params.add("n", int(eval(params.NUMBER_STEPS.value)))
    params.add("dt", float(params.DT.value))
    params.add("out", params.SIMULATION_FOLDER.value)
    params.add("WK_order", 4)
    # print(params.table())

    model = MecaModel(params, MecaScene)
    model.init_scene()
    model.run()

    model.plot()
