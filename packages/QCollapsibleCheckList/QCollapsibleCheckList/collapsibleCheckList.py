from __future__ import annotations
from typing import Dict, Generic, List, Literal, Tuple, TypedDict, overload,  Optional, Any

from PyQt6.QtGui import QFont

from .utils import debug
from .nodeWidget import NodeWidget, NodeVlayout
from .dataModel import DataGraph, DataItemAbstract, GraphNode, DataItemT, uidT
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt6 import QtCore

class CCLConfigT(TypedDict):
    font: Optional[QFont]
    hover_highlight_color: Optional[str]
    left_click_line: Literal["check", "fold", "none"]
    right_click_line: Literal["check", "fold", "none"]

class CollapsibleCheckList(QWidget, Generic[DataItemT]):

    MAX_UNCOLLAPSE_RECURSION_DEPTH = 20

    onCheckItem = QtCore.pyqtSignal(DataItemAbstract)
    onUnCheckItem = QtCore.pyqtSignal(DataItemAbstract)

    onHoverEnter = QtCore.pyqtSignal(DataItemAbstract)
    onHoverLeave = QtCore.pyqtSignal(DataItemAbstract)

    onCollapseNode = QtCore.pyqtSignal(GraphNode)
    onUnCollapseNode = QtCore.pyqtSignal(GraphNode)

    onManualCollapseWidget = QtCore.pyqtSignal(NodeWidget)
    onManualUnCollapseWidget = QtCore.pyqtSignal(NodeWidget)

    onHoverEnterNodeWidget = QtCore.pyqtSignal(NodeWidget)
    onHoverLeaveNodeWidget = QtCore.pyqtSignal(NodeWidget)

    onCollapseNodeWidget = QtCore.pyqtSignal(NodeWidget)
    onUnCollapseNodeWidget = QtCore.pyqtSignal(NodeWidget)

    def __init__(self, 
                 parent = None, 
                 init_items: List[DataItemT] = [], 
                 init_check_status : Optional[List[bool]] = None,
                 # configurations
                 hover_highlight_color: Optional[str] = None,
                 left_click_line: Literal["check", "fold", "none"] = "none",
                 right_click_line: Literal["check", "fold", "none"] = "none",
                 ) -> None:
        super().__init__(parent)

        # attributes will be accessed by CheckItemWidget
        self.check_status: Dict[uidT, bool] = {}
        self.shown_item_wids: Dict[uidT, List[NodeWidget]] = {}
        self.root_node_wids: List[NodeWidget] = []
        self._hovering_wid: Optional[NodeWidget] = None
        self.config: CCLConfigT = {
            "font": None,
            "hover_highlight_color": hover_highlight_color,
            "left_click_line": left_click_line,
            "right_click_line": right_click_line
        }

        self.initUI()
        self.initData(init_items, init_check_status)
        self.installEventFilter(self)
    
    def initUI(self):
        layout = QVBoxLayout()
        container = QWidget(self)
        container.setLayout(layout)

        self.vlayout = NodeVlayout()
        layout.addLayout(self.vlayout)
        layout.addStretch()

        scroll = QScrollArea(self)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        _lo = QVBoxLayout()
        _lo.addWidget(scroll)
        self.setLayout(_lo)
    
    def initData(self, init_items: List[DataItemT], init_check_status : Optional[List[bool]] = None):
        if init_check_status is None:
            init_check_status = [False for _ in init_items]
        assert len(init_items) == len(init_check_status)

        # maybe flush old data references
        # may not clean wid if it's not attached to root node
        if self.root_node_wids != []:
            _t = [wid for wid in self.root_node_wids]
            for _w in _t: 
                _w.removeSelf()
        self.check_status = {}
        self._hovering_wid = None

        self.graph = DataGraph(init_items)

        for d, status in zip(init_items, init_check_status):
            # import pdb;pdb.set_trace()
            self.check_status[d.dataitem_uid] = status
            self.shown_item_wids[d.dataitem_uid] = []

        # import pdb; pdb.set_trace()

        for n in self.graph.nodes:
            if n.parents == []:
                wid = self._createNodeWid(n)
                self.root_node_wids.append(wid)
                self.vlayout.addWidget(wid)

    def _createNodeWid(self, node: GraphNode[DataItemT]) -> NodeWidget[DataItemT]:
        wid = NodeWidget(self, node)
        self.shown_item_wids[node.value.dataitem_uid].append(wid)
        return wid

    def setFont(self, a0: QFont) -> None:
        self.config["font"] = a0
        for v in self.shown_item_wids.values():
            for wid in v:
                wid.setFont(a0)
        return super().setFont(a0)

    def getFont(self) -> Optional[QFont]:
        return self.config["font"]

    def addItem(self, i: DataItemT, check_status: bool = False) -> bool:
        """
        return if successfully added item,
        failed indicate the dataitem is already in the graph
        """
        debug("Add item - {}".format(i))
        if not self.graph.add(i):
            return False
        debug("Added item - {}".format(i))

        self.check_status[i.dataitem_uid] = check_status
        self.shown_item_wids.setdefault(i.dataitem_uid, [])

        last_node = self.graph.nodes[-1]
        debug(f"current root node_wids: {[wid.node for wid in self.root_node_wids]}")
        if last_node.parents == []:
            # root node
            wid = self._createNodeWid(last_node)
            self.root_node_wids.append(wid)
            self.vlayout.addWidget(wid)
        for wid in [ w for w in self.root_node_wids ]:
            # have to use this trick
            # because the root node may be deleted on the way updating
            debug(f"UPDATING NODE WIDGET: {wid}")
            wid.onNodeUpdate()
        return True

    def removeItem(self, i: DataItemT):
        pop_node = self.graph.remove(i)
        if pop_node is None:
            return
        for wid in self.root_node_wids:
            wid.onNodeUpdate()

    def setCollapse(self, item: DataItemT, status: bool):
        """
        should not be used for circular graph
        """
        def _recursivly_uncollapse(it):
            # add and test counter
            MAX_RECURSION_DEPTH = self.MAX_UNCOLLAPSE_RECURSION_DEPTH
            _UNCOLLAPSE_REC_COUNT = getattr(self, "_UNCOLLAPSE_REC_COUNT")
            if _UNCOLLAPSE_REC_COUNT > MAX_RECURSION_DEPTH:
                raise RecursionError("MAX_RECURSION_DEPTH excedeed on uncollapse widget.")
            setattr(self, "_UNCOLLAPSE_REC_COUNT", _UNCOLLAPSE_REC_COUNT + 1)

            parents = [n.value for n in self.graph.getNodeByItem(it).parents]
            for p in parents:
                _recursivly_uncollapse(p)
            for wid in self.getShownWid(it):
                if wid._collapsed:
                    wid._unCollapseFrame()


        if status:
            # want to collapse it
            if self.getShownWid(item):
                for wid in self.getShownWid(item):
                    if not wid._collapsed:
                        wid._collapseFrame()
            return
        else:
            # want to uncollapse it
            # do it recursively,
            # set a counter to stop infinite loop
            setattr(self, "_UNCOLLAPSE_REC_COUNT", 0)
            _recursivly_uncollapse(item)
            delattr(self, "_UNCOLLAPSE_REC_COUNT")

    def getShownWid(self, item: DataItemT):
        return self.shown_item_wids[item.dataitem_uid]

    @property
    def item_hover(self) -> Optional[DataItemT]:
        if self._hovering_wid is None:
            return None
        else: return self._hovering_wid.node.value

    @property
    def items_all(self) -> List[DataItemT]:
        return [d for d in self.graph.data]

    @property
    def items_checked(self) -> List[DataItemT]:
        ret = []
        for i in self.graph.data:
            if self.check_status[i.dataitem_uid]:
                ret.append(i)
        return ret

    @property
    def items_unchecked(self) -> List[DataItemT]:
        ret = []
        for i in self.graph.data:
            if not self.check_status[i.dataitem_uid]:
                ret.append(i)
        return ret

    def setItemChecked(self, data: DataItemT, status: bool):
        assert data.dataitem_uid in self.shown_item_wids.keys(), "Invalid data"
        for wid in self.shown_item_wids[data.dataitem_uid]:
            wid.setChecked(status)
            break
        # we may have set check status on wid.setChecked,
        # but if no node wid is shown up (they are collapsed), we have to do it this way
        if self.check_status[data.dataitem_uid] != status:
            self.check_status[data.dataitem_uid] = status
            if status == True:
                self.onCheckItem.emit(data)
            else:
                self.onUnCheckItem.emit(data)

    @overload
    def isItemChecked(self, a: int) -> bool: ...
    @overload
    def isItemChecked(self, a: DataItemT) -> bool: ...
    def isItemChecked(self, a) -> bool:
        if isinstance(a, int):
            data = self.graph.data[a]
        else:
            data = a
        return self.check_status[data.dataitem_uid]

    def eventFilter(self, a0, a1: Any) -> bool:
        if a1.type() == QtCore.QEvent.Type.MouseButtonPress:
            print(self.focusWidget())
            if a1.button() == QtCore.Qt.MouseButton.LeftButton:
                if self.config["left_click_line"] == "check":
                    if self.item_hover:
                        self.setItemChecked(self.item_hover, not self.isItemChecked(self.item_hover))
                elif self.config["left_click_line"] == "fold":
                    if self._hovering_wid:
                        self._hovering_wid.onCollapseClicked()
            if a1.button() == QtCore.Qt.MouseButton.RightButton:
                if self.config["right_click_line"] == "check":
                    if self.item_hover:
                        self.setItemChecked(self.item_hover, not self.isItemChecked(self.item_hover))
                elif self.config["right_click_line"] == "fold":
                    if self._hovering_wid:
                        self._hovering_wid.onCollapseClicked()

        return super().eventFilter(a0, a1)
