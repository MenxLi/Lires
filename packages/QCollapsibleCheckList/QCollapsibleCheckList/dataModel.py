from __future__ import annotations
from typing import Dict, List, NewType, Optional, Generic, TypeVar
from abc import ABC, abstractmethod
from uuid import uuid4

DataItemT = TypeVar("DataItemT", bound="DataItemAbstract")
uidT = NewType("uidT", str)

class DataGraph(Generic[DataItemT]):
    # A Directed Graph
    def __init__(self, data: List[DataItemT] = []) -> None:
        self._data = list(set(data))
        self.__node_list = [GraphNode(d).setInGraphStatus(True) for d in self.data]
        self.onDataChange()

    @property
    def data(self) -> List[DataItemT]:
        return self._data

    @property
    def nodes(self) -> List[GraphNode[DataItemT]]:
        return self.__node_list

    @property
    def rel_matrix(self):
        """
        The relationship matrix
        """
        return self.__rel_matrix

    def onDataChange(self):
        self.__update_rel_matrix()
        self.__updateNode()

    def getNodeByItem(self, item: DataItemT):
        for i in range(len(self.data)):
            if self.data[i].dataitem_uid == item.dataitem_uid:
                return self.nodes[i]
        raise ValueError("Item not found in the graph")

    def __updateNode(self):
        nodeslist = self.__node_list
        data = self.data
        for i in range(len(data)):
            nodeslist[i].parents = [ nodeslist[j] for j in range(len(data)) if self.rel_matrix[j][i] == 1]
            nodeslist[i].childs = [ nodeslist[j] for j in range(len(data)) if self.rel_matrix[i][j] == 1]

    def __update_rel_matrix(self):
        self.__rel_matrix = [ [False for _ in range(len(self.data)) ] for _ in range(len(self.data)) ]
        data = self.data
        for i in range(len(data)):
            for j in range(len(data)):
                if i == j:
                    continue
                self.__rel_matrix[i][j] = data[i].isParentOf(data[j])

    def add(self, d: DataItemT) -> Optional[GraphNode]:
        for d_ in self.data:
            if d is d_:
                return None
        new_node = GraphNode(d)
        new_node.in_graph = True
        self._data.append(d)
        self.__node_list.append(new_node)
        self.onDataChange()
        return new_node

    def remove(self, d: DataItemT) -> Optional[GraphNode]:
        pop_node = None
        for i in range(len(self._data))[::-1]:
            d_ = self._data[i]
            if d.dataitem_uid == d_.dataitem_uid:
                self._data.pop(i)
                pop_node = self.__node_list.pop(i).setInGraphStatus(False)
        self.onDataChange()
        return pop_node

class GraphNode(Generic[DataItemT]):
    value: DataItemT
    parents: List[GraphNode[DataItemT]] = []
    childs: List[GraphNode[DataItemT]] = []
    def __init__(
        self, 
        value: DataItemT,
        parents: List[GraphNode[DataItemT]] = [],
        childs: List[GraphNode[DataItemT]] = []
        ) -> None:
        super().__init__()
        self.value = value
        self.parents = parents
        self.childs = childs

        self.in_graph: Optional[bool] = None

    def setInGraphStatus(self, status: bool) -> GraphNode:
        self.in_graph = status
        return self

    @property
    def uid(self):
        return self.value.dataitem_uid

    def __ge__(self, n: GraphNode):
        return self.value >= n.value

    def __lt__(self, n:GraphNode):
        return self.value < n.value

    def __str__(self) -> str:
        return f"Node[{self.value.toString()}](N-parents: {len(self.parents)}, N-childs: {len(self.childs)})"

    __repr__ = __str__


class DataItemAbstract(ABC):

    @property
    def dataitem_uid(self) -> uidT:
        return uidT(str(id(self)))

    @abstractmethod
    def isParentOf(self, d: DataItemAbstract) -> bool:
        ...

    @abstractmethod
    def toString(self) -> str:
        ...

    def __ge__(self, d: DataItemAbstract) -> bool:
        raise NotImplementedError("__gt__ method has not been implemented")

    def __lt__(self, d: DataItemAbstract) -> bool:
        raise NotImplementedError("__le__ method has not been implemented")


