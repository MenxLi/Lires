
from typing import Callable, Optional
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QInputDialog, QDialog
from .tagSelector import TagSelector, DataItemAbstract
from .widgets import RefMixin, RefWidgetBase, WidgetMixin
from lires.confReader import saveToConf
from lires.core.dataClass import TagRule, DataTags

class TagModifier(RefMixin, WidgetMixin):
    def __init__(self, origin: RefWidgetBase) -> None:
        super().__init__()
        self.origin = origin
        origin.passRefTo(self)

    def database(self):
        return self.getMainPanel().database

    def promptRenameTag(self):
        def _onConfirm(t: DataTags):
            if len(t) == 0:
                return
            tag = list(t)[0]
            data = self.getMainPanel().db.getDataByTags(DataTags([tag]))
            n_online = len(["" for d in data if not d.is_local])
            # confirm
            text, ok = QInputDialog.getText(self.origin, "Edit tag".format(len(data)), \
                                            "Enter new tag for {} files ({} remote)".format(len(data), n_online), text = tag)
            if not ok:
                return 

            with self.getMainPanel().freeze():
                if self.getMainPanel().db.renameTag(tag, text):
                    curr_tags = self.getTagPanel().tag_selector.getSelectedTags()
                    maybe_change_sel_tags = TagRule.renameTag(curr_tags, tag, text)
                    if maybe_change_sel_tags is not None:
                        new_selected_tags = maybe_change_sel_tags
                        saveToConf(default_tags = new_selected_tags.toOrderedList())
                    self.getMainPanel().reloadData()
                else:
                    self.getMainPanel().statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")

        total_tags = self.getTagPanel().tag_selector.data_model.total_tags
        self.prompt = TagSelectPrompt(None, 
                total_tags, 
                onConfirm=_onConfirm,
                single_select=True,
                window_title="RENAME tag",
                )
        self.prompt.show()

    def promptDeleteTag(self):
        def _onConfirm(tags: DataTags):
            if len(tags) == 0:
                return
            data = self.getMainPanel().db.getDataByTags(tags)
            n_online = len(["" for d in data if not d.is_local])
            # confirm
            if not self.warnDialog("Delete tag: {}".format(tags), info_msg="For {} files ({})".format(len(data), n_online)):
                return
            if not self.warnDialog("Warning again, deleting tag: ***{}***".format(tags), info_msg="For {} files, Sure??".format(len(data))):
                return
            # do
            with self.getMainPanel().freeze():
                for tag in tags:
                    if self.getMainPanel().db.deleteTag(tag):
                        curr_tags = self.getTagPanel().tag_selector.getSelectedTags()
                        maybe_deleted_sel_tags = TagRule.deleteTag(curr_tags, tag)
                        if maybe_deleted_sel_tags is not None:
                            saveToConf(default_tags = maybe_deleted_sel_tags.toOrderedList())
                        self.getMainPanel().reloadData()
                    else:
                        self.getMainPanel().statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")
                        break

        total_tags = self.getTagPanel().tag_selector.data_model.total_tags
        self.prompt = TagSelectPrompt(None, 
                total_tags, 
                onConfirm=_onConfirm,
                single_select=False,
                window_title="DELETE tag(s)"
                )
        self.prompt.show()

class TagSelectPrompt(QDialog):

    def __init__(self, parent, 
            total_tags: DataTags, 
            onConfirm: Callable[[DataTags], None],
            single_select = False,
            window_title: Optional[str] = None,
            ) -> None:
        super().__init__(parent)
        self.tag_sel = TagSelector(self, tag_data = DataTags(), tag_total= total_tags)
        layout = QVBoxLayout()
        layout.addWidget(self.tag_sel)
        self.btn = QPushButton("OK")
        layout.addWidget(self.btn)
        self.setLayout(layout)
        if window_title is not None:
            self.setWindowTitle(window_title)

        def onDone():
            onConfirm(self._getSel())
            self.close()

        self.btn.clicked.connect(onDone)

        if single_select:
            self.tag_sel.ccl.onCheckItem.connect(self.deSelectOthers)
    
    def _getSel(self) -> DataTags:
        return self.tag_sel.getSelectedTags()
    
    def deSelectOthers(self, item: DataItemAbstract):
        for i in self.tag_sel.ccl.items_checked:
            if i.dataitem_uid != item.dataitem_uid:
                self.tag_sel.ccl.setItemChecked(i, False)