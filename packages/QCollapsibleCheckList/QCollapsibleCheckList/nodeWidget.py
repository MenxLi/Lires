
from __future__ import annotations
from typing import Generic, List, Optional, TYPE_CHECKING
import os

from .dataModel import GraphNode, DataItemT
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon, QEnterEvent, QFont
from PyQt6 import QtCore
from .utils import debug

if TYPE_CHECKING:
    from .collapsibleCheckList import CollapsibleCheckList

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")


class NodeVlayout(QVBoxLayout, Generic[DataItemT]):
    def __init__(self, indentation = 0):
        super().__init__()
        self.setContentsMargins(indentation, 0 , 0, 0)

    def insertWidget(self, *args, **kwargs) -> None:
        raise ReferenceError("Please use addWidget for NodeVlayout")

    def addWidget(self, wid: NodeWidget[DataItemT]) -> None:
        def widAt(idx: int) -> NodeWidget[DataItemT]:
            w = self.itemAt(idx).widget()
            if isinstance(w, NodeWidget):
                return w
            else:
                raise ValueError("NodeVlayout can only take NodeWidget")

        total_count = self.count()
        # import pdb; pdb.set_trace()
        debug(f"Total count: {total_count}")
        debug(f"Adding widget: {wid}")
        try:
            if total_count == 0:
                debug("add first wid")
                return super().addWidget(wid)

            if wid.node < widAt(0).node:
                debug("add wid to first")
                super().insertWidget(0, wid)
                return

            if wid.node >= widAt(total_count-1).node:
                debug("add wid to last")
                super().insertWidget(total_count, wid)
                return

            for i in range(0, total_count - 1):
                w0 = widAt(i)
                w1 = widAt(i+1)
                if wid.node < w1.node and wid.node >= w0.node:
                    super().insertWidget(i+1, wid)
                    debug(f"insert to {i+1}")
                    return
            debug("...")
        except NotImplementedError:
            debug("isLargerThan method not implemented")
        return super().addWidget(wid)


class NodeWidget(QWidget, Generic[DataItemT]):
    INDENTATION = 20
    BUTTON_SIZE = (16, 16)
    LINE_TOPBOTTM_MARGIN = 0

    class _CheckFrame(QFrame):...   # For styling

    def __init__(self, parent: CollapsibleCheckList[DataItemT], node: GraphNode[DataItemT], parent_node_wid: Optional[NodeWidget[DataItemT]] = None) -> None:
        super().__init__(parent)
        self._parent = parent
        self.node = node
        self.initUI()

        self.child_widgets: List[NodeWidget[DataItemT]] = []
        self.parent_widget: Optional[NodeWidget[DataItemT]] = parent_node_wid
        self.installEventFilter(self)

    def setParentNodeWidget(self, parent_node_wid: NodeWidget[DataItemT]) -> NodeWidget:
        """
        return child it self
        """
        self.parent_widget = parent_node_wid
        return self

    def _updateCollapseBtnStyle(self, btn: QPushButton):
        if self.node.childs == []:
            btn.setStyleSheet(r"border-radius: 8px; background-color: rgba(100, 100, 100, 50)")
            btn.setIcon(QIcon())
            btn.setEnabled(False)
            return
        
        btn.setEnabled(True)
        btn.setStyleSheet(r"border-radius: 8px; background-color: rgba(100, 100, 100, 150)")
        if self._collapsed:
            clp_icon = QIcon(os.path.join(ICON_DIR, "menu-right.svg"))
        else:
            clp_icon = QIcon(os.path.join(ICON_DIR, "menu-down.svg"))
        btn.setIcon(clp_icon)


    def initUI(self):
        self.vlayout = QVBoxLayout()

        self.clp_btn = QPushButton("")
        self.clp_btn.setCheckable(True)
        self.clp_btn.setFixedSize(*self.BUTTON_SIZE)
        self._updateCollapseBtnStyle(self.clp_btn)

        self.cb = QCheckBox(self)
        self.cb.setMinimumHeight(0)
        self.cb.setChecked(self.check_status)

        self.lbl = QLabel(self.node.value.toString())
        self.lbl.setMinimumHeight(0)

        self.select_frame = self._CheckFrame(self)
        if self._parent.config["hover_highlight_color"]:
            self.select_frame.setStyleSheet(":hover{"
                                       f"background-color: {self._parent.config['hover_highlight_color']}"
                                       "}")

        _layout = QHBoxLayout()
        _layout.setContentsMargins(0,self.LINE_TOPBOTTM_MARGIN,0,self.LINE_TOPBOTTM_MARGIN)
        _layout.addWidget(self.cb)
        _layout.addWidget(self.lbl)
        _layout.addStretch()
        self.select_frame.setLayout(_layout)

        layout = QHBoxLayout()
        layout.addWidget(self.clp_btn)
        layout.addWidget(self.select_frame)
        self.vlayout.addLayout(layout)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vlayout)

        self.clp_btn.clicked.connect(self.onCollapseClicked)
        self.cb.stateChanged.connect(lambda _: self.onCheckChange(self.cb.isChecked()))

        ccl_font = self._parent.getFont()
        if ccl_font:
            self.setFont(ccl_font)

    def setFont(self, a0: QFont) -> None:
        self.lbl.setFont(a0)
        return super().setFont(a0)
    
    def setHighlight(self, status: bool):
        if status:
            self.lbl.setStyleSheet("color: red;")
        else:
            self.lbl.setStyleSheet("")

    def enterEvent(self, event: QEnterEvent) -> None:
        self._parent.onHoverEnter.emit(self.data)
        self._parent.onHoverEnterNodeWidget.emit(self)
        self._parent._hovering_wid = self
        return super().enterEvent(event)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self._parent.onHoverLeave.emit(self.data)
        self._parent.onHoverLeaveNodeWidget.emit(self)
        self._parent._hovering_wid = None
        return super().leaveEvent(a0)
    
    @property
    def _collapsed(self):
        return not hasattr(self, "c_frame")
    
    @property
    def data(self) -> DataItemT:
        return self.node.value

    def onCheckChange(self, status: bool):
        self.check_status = status
        self._setSiblingWidsChecked(status)

        debug(f"On check change - {status}, {self}")
        debug(f"Sibling wids {self.sibling_wids}")
        debug(f"Parent item checked {self._parent.items_checked}")

    @property
    def check_status(self) -> bool:
        return self._parent.check_status[self.data.dataitem_uid]
    
    @check_status.setter
    def check_status(self, status: bool):
        old = self.check_status
        new = status

        item = self.node.value
        self._parent.check_status[item.dataitem_uid] = status

        if old == True and new == False:
            self._parent.onUnCheckItem.emit(item)
        elif old == False and new == True:
            self._parent.onCheckItem.emit(item)

    def isCBChecked(self) -> bool:
        return self.cb.isChecked()
    
    def setChecked(self, status: bool):
        self.check_status = status
        self.cb.setChecked(status)

    def _setSiblingWidsChecked(self, status: bool):
        for wid in self.sibling_wids:
            if not wid is self:
                if not wid.isCBChecked() == status:
                    wid.setChecked(status)

    @property
    def sibling_wids(self) -> List[NodeWidget]:
        return self._parent.shown_item_wids[self.node.value.dataitem_uid]

    def onNodeUpdate(self):
        debug(f"update... {self}")
        if not self.node.in_graph:
            # indicate has been poped out of the graph
            self.removeSelf()
            return

        for wid in self.child_widgets:
            wid.onNodeUpdate()

        # may have childs added/removed
        self._updateCollapseBtnStyle(self.clp_btn)

        # deal with parent here
        # is it possible self.parent_widget was deleted earlier??
        #       (should be impossible? because we always update child first in the recursion)
        if self.parent_widget is None:
            # previously no parent (as the root widget)
            if self.node.parents:
                # should be added as a child to someone else
                self.removeSelf()
                return
        else:
            if self.parent_widget.node.uid not in [ p.uid for p in self.node.parents ]:
                # previous parent is not current parents
                self.removeSelf()
                return

        # no need to deal with child if collapsed
        if self._collapsed:
            debug(f"Skipped node update - {self}")
            return

        wids_uid = [ wid.node.uid for wid in self.child_widgets ]
        childs_uid = [ c.uid for c in self.node.childs ]

        # add a new child
        for c in self.node.childs:
            if c.uid not in wids_uid:
                self._createAddChildNodeWid(c)

        # removed a child
        for wid in self.child_widgets:
            if wid.node.uid not in childs_uid:
                wid.removeSelf()

    def _createAddChildNodeWid(self, n: GraphNode) -> NodeWidget:
        wid = self._parent._createNodeWid(n).setParentNodeWidget(self)
        self.child_widgets.append(wid)
        self.c_frame.layout().addWidget(wid)
        return wid

    def onCollapseClicked(self):
        if self._collapsed:
            self._unCollapseFrame()
            self._parent.onManualUnCollapseWidget.emit(self)
        else:
            self._collapseFrame()
            self._parent.onManualCollapseWidget.emit(self)

    def _collapseFrame(self):
        if self._collapsed:
            return
        self._removeChilds()
        self._parent.onCollapseNode.emit(self.node)
        self._parent.onCollapseNodeWidget.emit(self)
        self._updateCollapseBtnStyle(self.clp_btn)

    def _unCollapseFrame(self):
        if not self.node.childs:
            return
        self._appendChilds()
        self._parent.onUnCollapseNode.emit(self.node)
        self._parent.onUnCollapseNodeWidget.emit(self)
        self._updateCollapseBtnStyle(self.clp_btn)


    def _appendChilds(self):
        if not self.node.childs:
            return

        frame_layout = NodeVlayout(indentation=self.INDENTATION)
        self.c_frame = QFrame(self)
        self.c_frame.setLayout(frame_layout)
        for c in self.node.childs:
            self._createAddChildNodeWid(c)
        self.vlayout.addWidget(self.c_frame)

    def _removeChilds(self):
        for i in range(len(self.child_widgets))[::-1]:
            wid = self.child_widgets.pop(i)
            wid.removeSelf()
        if hasattr(self, "c_frame"):
            frame: QFrame = getattr(self, "c_frame")
            self.vlayout.removeWidget(frame)
            frame.deleteLater()
            delattr(self, "c_frame")

    def removeSelf(self):
        self._removeChilds()
        # remove from global siblings
        for i in range(len(self.sibling_wids))[::-1]:
            if self.sibling_wids[i] is self:
                self.sibling_wids.pop(i)
        # remove from father widgets' child reference
        if self.parent_widget and not self.parent_widget._collapsed:
            p_child_wids = self.parent_widget.child_widgets
            for i in range(len(p_child_wids))[::-1]:
                if p_child_wids[i].node.uid == self.node.uid:
                    p_child_wids.pop(i)
            if p_child_wids == []:
                self.parent_widget._collapseFrame()
        # remove from parent's root_nodes
        for i in range(len(self._parent.root_node_wids))[::-1]:
            wid = self._parent.root_node_wids[i]
            if wid is self:
                self._parent.root_node_wids.pop(i)
        self.deleteLater()

    def __str__(self) -> str:
        return "NodeWidget - [{}]".format(self.node.value.toString())
