from __future__ import annotations
from typing import List
from PyQt6.QtWidgets import QApplication
from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

class Person:
   def __init__(self, name: str, family: str, age: int) -> None:
      self.name = name
      self.family: str = family
      self.age = age

   def getFamilyMember(self) -> List[str]:
      return [s for s in self.family.split(".") if s]

   def __str__(self) -> str:
      return f"{self.name} ({self.age})"

class PersonData(DataItemAbstract):

   def __init__(self, person: Person) -> None:
      super().__init__()
      self.p = person

   def isParentOf(self, child: PersonData) -> bool:        
      child_family = child.p.getFamilyMember()
      self_family_with_self = self.p.getFamilyMember() + [self.p.name]
      return child_family == self_family_with_self
    
   def toString(self) -> str:
      return str(self.p)

   # implement __ge__ and __lt__ to sort widget in incremental order
   def __ge__(self, d: PersonData) -> bool:
      return self.p.age >= d.p.age

   def __lt__(self, d: PersonData) -> bool:
      return self.p.age < d.p.age


if __name__ == "__main__":
   app = QApplication([])
   persons = [
      Person("Child1", "GrandParent0.Parent1", 3),
      Person("Child2", "GrandParent0.Parent1", 6),
      Person("Child3", "GrandParent1.Parent2", 5),
      Person("Parent1", "GrandParent0", 41),
      Person("Parent2", "GrandParent1", 33),
      Person("Parent3", "GrandParent1", 34),
      Person("GrandParent0", "", 79),
      Person("GrandParent1", "", 77),
   ]
   person_data = [ PersonData(p) for p in persons ]

   ccl = CollapsibleCheckList(init_items=person_data)
   ccl.show()
   app.exec()
