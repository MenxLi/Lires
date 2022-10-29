from __future__ import annotations
from PyQt6.QtWidgets import QApplication
from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

class StringData(str, DataItemAbstract):
   SEP = "."
   def isParentOf(self, child: StringData) -> bool:
      child_sp = child.split(self.SEP)
      self_sp = self.split(self.SEP)
      if len(self_sp) != len(child_sp)-1:
         return False
      return self_sp == child_sp[:-1]
   
   def toString(self) -> str:
      return f"{self.split(self.SEP)[-1]}"

if __name__ == "__main__":
   app = QApplication([])
   string = [
      "1",
      "1.3",
      "1.2",
      "2.3", 
      "1.2.3",
      "1.2.3.4",
   ]
   string_data = [ StringData(s) for s in string]

   ccl = CollapsibleCheckList[StringData](None, string_data)
   
   def onCheckChange(status: str, item: StringData):
      print(status, item)
      print("Current selected items: ")
      for i in ccl.items_checked:
         print(">> ", i)
      print("\n")

   ccl.onCheckItem.connect(lambda x: onCheckChange("Checked: ", x))
   ccl.onUnCheckItem.connect(lambda x: onCheckChange("Unchecked: ", x))


   # Below are valid signals
   #  ccl.onCheckItem.connect(lambda x: print("Signal - onCheckItem", x))
   #  ccl.onUnCheckItem.connect(lambda x: print("Signal - onUnCheckItem", x))
   #  ccl.onCollapseNode.connect(lambda x: print("Signal - onCollapseNode", x))
   #  ccl.onUnCollapseNode.connect(lambda x: print("Signal - onUnCollapseNode", x))
   #  ccl.onCollapseNodeWidget.connect(lambda x: print("Signal - onCollapseNodeWidget", x))
   #  ccl.onUnCollapseNodeWidget.connect(lambda x: print("Signal - onUnCollapseNodeWidget", x))
   #  ccl.onHoverEnter.connect(lambda x: print("Signal - onHoverEnter", x))
   #  ccl.onHoverLeave.connect(lambda x: print("Signal - onHoverLeave", x))
   #  ccl.onHoverEnterNodeWidget.connect(lambda x: print("Signal - onHoverEnterNodeWidget", x))
   #  ccl.onHoverLeaveNodeWidget.connect(lambda x: print("Signal - onHoverLeaveNodeWidget", x))

   ccl.show()
   app.exec()
