class JSONHighlighter(QSyntaxHighlighter):
    rules = {
        "([-0-9.]+)(?!([^\"]*\"[\\s]*\\:))": Qt.darkRed,
        "(?:[ ]*\\,[ ]*)(\"[^\"]*\")": Qt.darkGreen,
        "(\"[^\"]*\")\\s*\\": Qt.darkGreen,
        "(\"[^\"]*\")\\s*\\:": QColor.fromRgbF(0.7,0.5,1,1),
        ":+(?:[: []*)(\"[^\"]*\")": QColor.fromRgbF(0,0.5,1,1),
    }
    rules = [[QRegExp(pat), fmt] for pat, fmt in rules.items()]
    
    def __init__(self, document):
        super(JSONHighlighter, self).__init__(document)
   
        rules = []

        # numbers
        rule = QRegExp("([-0-9.]+)(?!([^\"]*\"[\\s]*\\:))")
        rules.append((rule, Qt.darkRed))

        # middle
        rule = QRegExp("(?:[ ]*\\,[ ]*)(\"[^\"]*\")")
        rules.append((rule, Qt.darkGreen))

        # last
        rule = QRegExp("(\"[^\"]*\")(?:\\s*\\])")
        rules.append((rule, Qt.darkGreen))

        # string
        rule = QRegExp("(\"[^\"]*\")\\s*\\:")
        rules.append((rule, QColor.fromRgbF(0.7,0.5,1,1)))

        rule = QRegExp(":+(?:[: []*)(\"[^\"]*\")")
        rules.append((rule, QColor.fromRgbF(0,0.5,1,1)))

        self.rules = [[QRegExp(pat), fmt] for pat, fmt in rules]
        
    def highlightBlock(self, text):
        # object
        for exp, fmt in self.rules:
            index = exp.indexIn(text)
            while (index >= 0):
                index = exp.pos(1);
                length = len(exp.cap(1))
                self.setFormat(index, length, fmt)
                index = exp.indexIn(text, index + length)
