package parser;

import static com.sun.corba.se.impl.util.Utility.printStackTrace;

public class Lexer {
       
    public String token;
    
    public static final int eos = 0; // end of source
    public static final int ident = 1;
    public static final int number = 2;
    public static final int separator = 3;
    public int kind;
    
    public Lexer (String input)
    {
        source = input;

        pos = 0;        
        len = source.length();
        line = 1;
        col = 0;
        nextChar ();      
        nextToken ();
    }
    
    private String source;
    private int pos;
    private int len;
    private char inpCh;
    
    private int line;
    private int col;
    
    private static final char zero = 0;
    
    private void nextChar ()
    {
        if (pos < len)
        {
           inpCh = source.charAt(pos);
           pos ++;
        }
        else
        {
            inpCh = zero;
        }
        
        if (inpCh == '\n') 
        {
            line ++;
            col = 0;
        }
        else
        {
            col ++;
        }
    }
    
    public void nextToken ()
    {
        while (isSpace (inpCh)) nextChar ();
        
        if (isLetter (inpCh))
        {
            kind = ident;
            token = "";
            while (isLetter(inpCh) || isDigit (inpCh))
            {
               token = token + inpCh;
               nextChar ();
            }
        }
        else if (isDigit (inpCh))
        {
            kind = number;
            token = "";
            while (isDigit (inpCh))
            {
               token = token + inpCh;
               nextChar ();
            }
        }
        else if (inpCh != zero)
        {
            kind = separator;
            token = "" + inpCh;
            nextChar ();
        }
        else
        {
            kind = eos;
            token = "";
        }

        String s = "line: " + line + 
                    ", column: " + col + 
                    ", inpCh: " + inpCh + 
                    ", token: " + token + 
                    ", kind: " + kind ;
        System.out.println (s);
    }
    
    private boolean isSpace (char c) 
    { 
        return c <= ' ' && c != zero;
    }
    
    private boolean isLetter (char c) 
    { 
        return c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' || c == '_';
    }
    
    private boolean  isDigit (char c) 
    { 
        return c >= '0' && c <= '9';
    }
    
    /* ---- */
    
    public void error (String s)
    {
        s = s + ", line: " + line + 
                ", column: " + col + 
                ", inpCh: " + inpCh + 
                ", token: " + token + 
                ", kind: " + kind ;
        printStackTrace();
        throw new RuntimeException (s);
    }
    
    private final String quote = "\"";
    
    public boolean isSeparator (String s)
    {
        return kind == separator && token.equals (s);
    }

    public void checkSeparator (String s)
    {
        if (isSeparator(s))
            nextToken();
        else
            error (quote + s + quote + " expected");
    }
    
    public boolean isKeyword (String s)
    {
        return kind == ident && token.equals (s);
    }

    public void checkKeyword (String s)
    {
        if (isKeyword(s))
            nextToken();
        else
            error (quote + s + quote + " expected");
    }
}
