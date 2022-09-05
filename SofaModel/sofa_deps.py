import logging

from Model3D.basesofamodel.load_SOFA import load_SOFA

load_SOFA()
from Sofa.Core import Controller


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


log = logging.getLogger(__name__)
