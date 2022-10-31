from __future__ import annotations
from typing import Literal
from PyQt6.QtWidgets import QApplication
from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

itemT = Literal["Root", "A", "B", "C"]

class CycleData(str, DataItemAbstract):
   def __init__(self, key: itemT) -> None:
      super().__init__()

   def isParentOf(self, data: CycleData) -> bool:
      k0 = str(self)
      k1 = str(data)
      if k0 == "Root" and k1 == "A":
         return True
      if k0 == "A" and k1 == "B":
         return True
      if k0 == "B" and k1 == "C":
         return True
      if k0 == "C" and k1 == "A":
         return True
      return False
   
   def toString(self) -> str:
      return str(self)

if __name__ == "__main__":
   app = QApplication([])
   data = [
      CycleData("Root"),
      CycleData("A"),
      CycleData("B"),
      CycleData("C"),
   ]

   ccl = CollapsibleCheckList(None, data)
   ccl.show()
   app.exec()
