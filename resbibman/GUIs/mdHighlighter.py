from typing import List, Tuple
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt

class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """A minimum markdown syntax highlighter """
    BOLD = QFont.Weight.Bold
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = list()
        self.multi_highlight_rules: List[Tuple[QRegularExpression, QRegularExpression, QTextCharFormat]] = list()

        # Key words
        #  self.keywords = []
        #  keyword_format = QTextCharFormat()
        #  keyword_format.setForeground(QColor(0, 255, 100, 255))
        #  keyword_format.setFontWeight(self.BOLD)
        #  self.highlighting_rules += [([pattern, keyword_format]) for pattern in self.keywords]

        # Headings
        for _heading_frac in range(1,5):
            heading_format = QTextCharFormat()
            heading_format.setForeground(QColor(0, 100+20*_heading_frac, 200+10*_heading_frac, 255))
            heading_format.setFontWeight(self.BOLD)
            self.highlighting_rules.append((QRegularExpression("#"*_heading_frac+"[^\n]*$"), heading_format))
        
        # List
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(100, 0, 0, 255))
        list_format.setFontWeight(self.BOLD)
        self.highlighting_rules.append((QRegularExpression("^(\*|-) "), list_format))

        # url
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(150, 150, 150, 255))
        self.highlighting_rules.append((QRegularExpression("!?\[[^\n]*\]\([^\n]*\)"), link_format))

        # quote
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor(0, 200, 100, 255))
        self.highlighting_rules.append((QRegularExpression("^> "), quote_format))

        # horizontal line
        hline_format = QTextCharFormat()
        hline_format.setForeground(QColor(200, 0, 100, 255))
        self.highlighting_rules.append((QRegularExpression("\n---+$"), hline_format))

        # html
        html_format = QTextCharFormat()
        html_format.setForeground(QColor(100, 150, 150, 255))
        self.highlighting_rules.append((QRegularExpression("<[^<]*>"), html_format))

        # bold
        # bold_format = QTextCharFormat()
        # bold_format.setForeground(QColor(255, 150, 150, 255))
        # bold_format.setFontWeight(QFont.Bold)
        # # self.multi_highlight_rules.append((QRegExp("\*\*"), QRegExp("\*\*"), bold_format))
        # self.highlighting_rules.append((QRegExp("\*\*.+\*\*"), bold_format))

        # # italic
        # bolditalic_format = QTextCharFormat()
        # bolditalic_format.setForeground(QColor(255, 150, 150, 255))
        # # italic_format.setFontWeight(QFont.Italic)
        # bolditalic_format.setFontItalic(True)
        # self.highlighting_rules.append((QRegExp("[^\*]\*\*\*[^\*].+[^\*]\*\*\*[^\*]"), bolditalic_format))

        # # html-in
        # html_format_in = QTextCharFormat()
        # html_format_in.setForeground(QColor(50, 240, 250, 255))
        # self.multi_highlight_rules.append((QRegExp("<{^<}*>"), QRegExp("</[^<]*>"), html_format_in))

    def highlightBlock(self, text: str) -> None:
        self._highlight_singleline(text)
        #  self._highlight_multiline(text)
        # self._highlight_multiline_samePattern(text)
    
    def _highlight_singleline(self, text: str):
        for pattern, format in self.highlighting_rules:
            current_ = 0
            expression = QRegularExpression(pattern)
            match = expression.match(text)
            while match.hasMatch():
                index = match.capturedStart() + current_
                length = match.capturedLength()
                self.setFormat(index, length, format)
                current_ += match.capturedEnd()
                match = expression.match(text[current_: len(text)])
            self.setCurrentBlockState(0)
    
    def _highlight_multiline(self, text: str):
        # To be implemented...
        return None
        _state_counter = 0
        for start_pattern, end_pattern, format in self.multi_highlight_rules:
            if start_pattern == end_pattern:
                continue
            _state_counter += 1
            start_index = 0
            if self.previousBlockState() != _state_counter:
                start_index = start_pattern.indexIn(text)
            
            while start_index >=0:
                end_index = end_pattern.indexIn(text, start_index)

                if end_index == -1:
                    self.setCurrentBlockState(_state_counter)
                    length = len(text) - start_index
                else:
                    length = end_index - start_index + end_pattern.matchedLength()

                self.setFormat(start_index, length, format)
                start_index = start_pattern.indexIn(text, start_index + length)

    def _highlight_multiline_samePattern(self, text: str):
        return None
        _state_counter = 999
        for start_pattern, end_pattern, format in self.multi_highlight_rules:
            if start_pattern != end_pattern:
                print('hello')
                continue
            pattern = start_pattern
            _state_counter -= 1
            start_index = 0
            if self.previousBlockState() != _state_counter:
                start_index = pattern.indexIn(text)
            
            while start_index >=0:
                print("SI: ", start_index)
                end_index = pattern.indexIn(text, start_index+pattern.matchedLength())
                print(end_index)

                if end_index == -1:
                    self.setCurrentBlockState(_state_counter)
                    length = len(text) - start_index
                else:
                    length = end_index - start_index + pattern.matchedLength()

                self.setFormat(start_index, length, format)
                if end_index == -1:
                    break
                start_index = pattern.indexIn(text, end_index +pattern.matchedLength()) 
