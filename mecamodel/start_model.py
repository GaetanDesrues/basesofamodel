import logging
from typing import Type, Optional

import treefiles as tf

from basesofamodel.base_model import BaseModel, BaseScene
from mecamodel.main_scene import MecaScene


class MecaModel(BaseModel):
    pass


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
