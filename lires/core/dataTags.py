from __future__ import annotations
from .base import LiresBase
from typing import Set, Union, List, TypeVar, Optional, Sequence, overload
from .dbConn import LIST_SEP

class TagRule(LiresBase):
    SEP = "->"
    logger = LiresBase.loggers().core
    @classmethod
    def all_parents(cls, tag: str) -> DataTags:
        """
        assume cls.SEP is '.'
        input: a.b.c
        return: [a, a.b]
        """
        sp = tag.split(cls.SEP)
        if len(sp) == 1:
            return DataTags([])
        accum = []
        all_p_tags = []
        for i in range(0, len(sp)-1):
            accum += [sp[i]]
            all_p_tags.append(cls.SEP.join(accum))
        return DataTags(all_p_tags)
    
    @classmethod
    def all_childs(cls, tag: str, tag_pool: Sequence[str] | DataTags) -> DataTags:
        """
        assume cls.SEP is '.'
        input: (a.b, [a, a.b, a.b.c, a.b.d])
        return: [a.b.c, a.b.d]
        """
        ret = []
        for t in tag_pool:
            if t.startswith(tag) and len(t)>len(tag)+len(cls.SEP):
                if t[len(tag): len(tag) + 2] == cls.SEP:
                    ret.append(t)
        return DataTags(ret)
    
    @classmethod
    def rename_tag(cls, src: DataTags, aim_tag: str, new_tag: str) -> Optional[DataTags]:
        """
        return None if tag not in src nor it's all parent tags
        otherwise:
            for tag in src:
                if tag is the aim_tag:
                    change tag to new_tag
                if aim_tag is in the tag's parent tags: 
                    change the parent tag
                    ( e.g. <cls.SEP='.'> tag: a.b.c, aim_tag: a.b, new_tag: d,
                        change the tag to b.c)
                else:
                    keep the tag same
        """
        aim_tag = cls.strip_tag(aim_tag)
        new_tag = cls.strip_tag(new_tag)

        if aim_tag not in src.with_parents():
            return None

        out_tags = []
        for tag in src:
            # first determine if tag is a intermediate node
            if tag == aim_tag:
                out_tags.append(new_tag)
            elif tag.startswith(aim_tag):
                tag = new_tag + tag[len(aim_tag):]
                out_tags.append(tag)
            else:
                out_tags.append(tag)
        return DataTags(out_tags)
    
    @classmethod
    def delete_tag(cls, src: DataTags, aim_tag: str) -> Optional[DataTags]:
        """
        delete aim_tag, as well as it's all child tags from src
        return None if none of tags in src in aim_tag and it's child tags
        e.g. 
            <cls.SEP='.'>
            src: (a.b, a.b.c, b.c)
            aim_tag: a.b
            return - (b.c)
        """
        _delete_something = False
        out_tags = []
        may_delete = DataTags([aim_tag]).with_childs_from(src)
        for t in src:
            if t in may_delete:
                _delete_something = True
                continue
            out_tags.append(t)
        if _delete_something:
            return DataTags(out_tags)
        else:
            return None
    
    @classmethod
    def strip_tag(cls, tag: str) -> str:
        tag_sp = tag.split(cls.SEP)
        tag_sp = [t.strip() for t in tag_sp]
        return cls.SEP.join(tag_sp)

    @classmethod
    def strip_tags_inplace(cls, tags: DataTagT_G) -> DataTagT_G:
        if isinstance(tags, set):
            for t in tags:
                stripped = cls.strip_tag(t)
                if LIST_SEP in stripped:
                    raise cls.Error.LiresProhibitedKeywordError(f"Tag contains prohibited keyword: {LIST_SEP}")
                if stripped == t:
                    continue
                tags.remove(t)
                tags.add(stripped)  # type: ignore
        else:
            for i in range(len(tags)):
                tags[i] = cls.strip_tag(tags[i])
        return tags

class DataTags(Set[str], LiresBase):
    logger = LiresBase.loggers().core
    @overload
    def __init__(self):...
    @overload
    def __init__(self, arg: DataTagT):...

    def __init__(self, arg: Union[DataTagT, None] = None):
        if arg is None:
            super().__init__()
        elif isinstance(arg, DataTags):
            super().__init__(arg)
        else:
            super().__init__(TagRule.strip_tags_inplace(arg))

    def to_ordered_list(self):
        # TODO: rename to to_list(self, ordered: bool = True)
        ordered_list = list(self)
        ordered_list.sort()
        return ordered_list
    
    def union(self, *s: Set|DataTags|list) -> DataTags:
        return DataTags(super().union(*s))
    
    def with_parents(self) -> DataTags:
        parents = DataTags()
        for s in self:
            parents = parents.union(TagRule.all_parents(s))
        return self.union(parents)

    def with_childs_from(self, child_choices: DataTags):
        childs = DataTags()
        for s in self:
            childs = childs.union(TagRule.all_childs(s, child_choices))
        return self.union(childs) # type: ignore
    
    def to_string(self):
        if len(self) > 0:
            return "; ".join(self.to_ordered_list())
        else:
            return "<None>"

DataTagT = Union[DataTags, List[str], Set[str]]
DataTagT_G = TypeVar('DataTagT_G', bound=DataTagT)
