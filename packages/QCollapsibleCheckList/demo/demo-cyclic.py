from __future__ import annotations
from typing import Literal
from PyQt6.QtWidgets import QApplication
from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

itemT = Literal["A", "B", "C", "D"]

class CycleData(DataItemAbstract):
   def __init__(self, key: itemT) -> None:
      super().__init__()
      self.k = key

   def isParentOf(self, data: CycleData) -> bool:
      if self.k == "A":
         return True
      k0 = self.k
      k1 = data.k
      if k0 == "B" and k1 =="C":
         return True
      if k0 == "C" and k1 =="D":
         return True
      if k0 == "D" and k1 =="B":
         return True
      return False
   
   def toString(self) -> str:
      return self.k

if __name__ == "__main__":
   app = QApplication([])
   data = [
      CycleData("A"),
      CycleData("B"),
      CycleData("C"),
      CycleData("D"),
   ]

   ccl = CollapsibleCheckList(None, data)
   ccl.show()
   app.exec()
