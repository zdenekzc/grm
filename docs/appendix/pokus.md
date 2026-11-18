# An Experiment

```python
    def readIdent (self, lexer) :
        result = lexer.tokenText
        if not lexer.isIdentifier () :
           lexer.error ("Identifier expected")
        lexer.nextToken ()
        return result

    def parseItem (self, lexer) :
        if lexer.isIdentifier () :
           result = lexer.tokenText
           lexer.nextToken ()
        elif lexer.isNumber () :
           result = lexer.tokenText
           lexer.nextToken ()
        elif lexer.isSeparator ('(') :
           lexer.checkSeparator ('(')
           result = self.parseExpr ()
           lexer.checkSeparator (')')
        else :
           lexer.error ("Identifier or number expected")
        return result

    def parseFactor (self, lexer) :
        result = self.parseItem (lexer)
        while lexer.isSeparator ("*") or lexer.isSeparator ("/") :
           arit = lexer.tokenText
           lexer.nextToken () # skip + or -
           b = self.parseItem (lexer)
           result = result + " " + arit + " " + b
        return result

    def parseExpr (self, lexer) :
        result = self.parseFactor (lexer)
        while lexer.isSeparator ("+") or lexer.isSeparator ("-") :
           arit = lexer.tokenText
           lexer.nextToken () # skip + or -
           b = self.parseFactor (lexer)
           # a = a + b
           result = "(" + result + ") " + arit + " (" + b + ")"
        return result

        self.put ("expression " + a )
```

```python
    # simple statements

    def readIdent (self, lexer) :
        result = lexer.tokenText
        if not lexer.isIdentifier () :
           lexer.error ("Identifier expected")
        lexer.nextToken ()
        return result

    def parseItem (self, lexer) :
        if lexer.isIdentifier () :
           result = lexer.tokenText
           lexer.nextToken ()
        elif lexer.isNumber () :
           result = lexer.tokenText
           lexer.nextToken ()
        else :
           lexer.error ("Identifier or number expected")
        return result

    def parseExpr (self, lexer) :
        a = self.parseItem (lexer)
        if lexer.isSeparator ("+") :
           lexer.nextToken () # skip +
           b = self.parseItem (lexer)
           # a = a + b
           a = a + " + " + b
        return a

        self.put ("expression " + a )

    def parseSimpleStat (self, lexer) :
        a = self.parseExpr (lexer)
        lexer.checkSeparator ('=')
        b = self.parseExpr (lexer)
        lexer.checkSeparator (';')
        self.put ("simple " + a + " = " + b)

    def parseWhile (self, lexer) :
        self.openBranch ("while")
        self.setLine (lexer)
        lexer.checkKeyword ("while")
        lexer.checkSeparator ('(')
        self.parseExpr (lexer)
        lexer.checkSeparator (')')
        self.parseStat (lexer)
        self.closeBranch ()

    def parseIf (self, lexer) :
        self.openBranch ("if")
        self.setLine (lexer)
        lexer.checkKeyword ("if")
        lexer.checkSeparator ('(')
        self.parseExpr (lexer)
        lexer.checkSeparator (')')

        self.openBranch ("then")
        self.parseStat (lexer)
        self.closeBranch ()

        if lexer.isKeyword ("else") :
           lexer.nextToken () # preskoc else
           self.openBranch ("else")
           self.parseStat (lexer)
           self.closeBranch ()
        self.closeBranch ()

    def parseCompoundStat (self, lexer) :
        lexer.checkSeparator ("{")
        while not lexer.isSeparator ("}") :
            self.parseStat (lexer)
        lexer.checkSeparator ("}")

    def parseStat (self, lexer) :
        if lexer.isKeyword ("if") :
           self.parseIf (lexer)
        elif lexer.isKeyword ("while") :
           self.parseWhile (lexer)
        elif lexer.isSeparator ("{") :
           self.parseCompoundStat (lexer)
        else :
           self.parseSimpleStat (lexer)
```
