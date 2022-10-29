from __future__ import annotations
from PyQt6.QtWidgets import QApplication
from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

class StringData(str, DataItemAbstract):
   SEP = "->"
   def isParentOf(self, d: StringData) -> bool:
      d_split = d.split(self.SEP)
      self_split = self.split(self.SEP)
      if len(d_split) <= len(self_split):
         return False
      for i, j in zip(self_split, d_split):
         if i != j:
               return False
      return True
   
   def toString(self) -> str:
      return f"{self.split(self.SEP)[-1]} ({self})"

   # implement __ge__ and __lt__ to sort widget in incremental order
   def __ge__(self, d: StringData) -> bool:
      return len(self) >= len(d)
   def __lt__(self, d: StringData) -> bool:
      return len(self) < len(d)

if __name__ == "__main__":
   app = QApplication([])
   string_status = [
      ("1", False),
      ("1->3", False),
      ("1->2", False),
      ("2->3", False),
      ("1->2->3", True),
      ("1->2->3->4", False),
   ]
   string_data = [ StringData(s[0]) for s in string_status]
   init_status = [ s[1] for s in string_status ]

   ccl = CollapsibleCheckList(None, string_data, init_status)
   ccl.show()
   app.exec()
