
import unittest
from resbibman.core.dataClass import TagRule, DataTags

class TestTagRule(unittest.TestCase):

    SEP = TagRule.SEP

    def test_getParents(self):
        s = self.SEP
        tag = f"a{s}b{s}c{s}d"
        self.assertEqual(
            TagRule.allParentsOf(tag),
            DataTags([
                f"a",
                f"a{s}b",
                f"a{s}b{s}c",
            ])
        )

    def test_getChilds(self):
        s = self.SEP

        t = f"a{s}b{s}c"
        t_pool = [
            t,
            f"a{s}b{s}c{s}d",
            f"a{s}b{s}c{s}",
            f"a{s}b",
            f"a",
        ]

        self.assertEqual(
            TagRule.allChildsOf(t, t_pool),
            DataTags([
                f"a{s}b{s}c{s}d",
            ])
        )
    
    def test_renameTag(self):
        s = self.SEP
        tags = DataTags([
            f"a{s}b{s}c{s}d",
            f"a{s}b{s}c",
            f"a{s}b",
            f"b",
            f"d{s}b",
            f"a{s}c{s}b",
        ])
        self.assertEqual(
            TagRule.renameTag(tags, f"a{s}b", "d"),
            DataTags([
                f"d{s}c{s}d",
                f"d{s}c",
                f"d",
                f"b",
                f"d{s}b",
                f"a{s}c{s}b",
            ])
        )
        tags = DataTags([
            f"a{s}b{s}c",
            f"a{s}b",
            f"d{s}c",
            f"a{s}c",
        ])
        self.assertEqual(
            TagRule.renameTag(tags, f"a{s}b{s}c", f"a{s}b{s}c{s}d"),
            DataTags([
                f"a{s}b{s}c{s}d",
                f"a{s}b",
                f"d{s}c",
                f"a{s}c",
            ])
        )
        self.assertEqual(
            TagRule.renameTag(tags, f"x{s}b{s}c", f"a{s}b{s}c{s}d"),
            None
        )
    
    def test_deleteTag(self):
        s = self.SEP
        tags = DataTags([
            f"a{s}b{s}c{s}d",
            f"a{s}b{s}c",
            f"a{s}b",
            f"b{s}c",
        ])
        self.assertEqual(
            TagRule.deleteTag(tags, f"a{s}b"),
            DataTags([f"b{s}c"])
        )
        self.assertEqual(
            TagRule.deleteTag(tags, f"b{s}d"),
            None
        )
    

class TestDataTags(unittest.TestCase):
    SEP = TagRule.SEP

    def test_withParents(self):
        s = self.SEP
        tags = DataTags([
            f"a{s}b{s}c{s}d",
            f"a{s}b{s}c",
            f"a",
        ])
        self.assertEqual(
            tags.withParents(),
            DataTags([
                f"a{s}b{s}c{s}d",
                f"a{s}b{s}c",
                f"a{s}b",
                f"a",
            ])
        )

    def test_withChilds(self):
        s = self.SEP
        tag_pool = DataTags([
            f"a{s}b{s}c",
            f"b{s}c",
            f"d{s}e",
        ])
        aim = DataTags([
            f"a{s}b",
            f"d",
        ])
        self.assertEqual(
            aim.withChildsFrom(tag_pool),
            DataTags([
                f"a{s}b",
                f"a{s}b{s}c",
                f"d",
                f"d{s}e",
            ])
        )
