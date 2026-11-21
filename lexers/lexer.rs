
// lexer.rs

#![allow(warnings, unused)]

use std::fs;

/* ---------------------------------------------------------------------- */

const eos : isize = 0;
const identifier : isize = 1;
const number : isize = 2;
const real_number : isize = 3;
const character_literal : isize = 4;
const string_literal : isize = 5;
const separator : isize = 6;
const end_of_line : isize = 7;

/* ---------------------------------------------------------------------- */

pub struct Lexer
{
   charFileInx: usize,
   charLineNum: isize,
   charColNum: isize,
   charByteOfs: usize, // character offset (from 0)

   tokenFileInx: usize,
   tokenLineNum: isize,
   tokenColNum: isize,
   tokenByteOfs: usize, // token (in self.token)

   prevFileInx: usize,
   prevLineNum: isize,
   prevColNum: isize,
   prevByteOfs: usize, // previous token

   pub ch : char,
   pub token: isize,
   pub tokenText: String,
   tokenValue: String,

   source: String,
   sourceLen: usize,

   fileNames : Vec <String>,
}

/* ---------------------------------------------------------------------- */

impl Lexer
{
   pub fn new () -> Lexer
   {
      Lexer
      {
         charFileInx: 0,
         charLineNum: 0,
         charColNum: 0,
         charByteOfs: 0, // character offset (from 0)

         tokenFileInx: 0,
         tokenLineNum: 0,
         tokenColNum: 0,
         tokenByteOfs: 0, // token (in self.token)

         prevFileInx: 0,
         prevLineNum: 0,
         prevColNum: 0,
         prevByteOfs: 0, // previous token

         ch : '\0',
         token: eos,
         tokenText: "".to_string (),
         tokenValue: "".to_string (),

         source : "".to_string (),
         sourceLen : 0,

         fileNames : Vec::from ( [ String::new () ]),
      }
   }

   /*
   fn reset (& mut self)
   {
       self.charFileInx = 0;
       self.charLineNum = 1;
       self.charColNum = 1;
       self.charByteOfs = 0; // character offset (from 0)

       self.tokenFileInx = 0;
       self.tokenLineNum = 1;
       self.tokenColNum = 1;
       self.tokenByteOfs = 0; // token (in self.token)

       self.prevFileInx = 0;
       self.prevLineNum = 1;
       self.prevColNum = 1;
       self.prevByteOfs = 0; // previous token

       self.ch = '\0';
       self.token = eos;
       self.tokenText = String::new();
       self.tokenValue = String::new();
   }
   */

   /* ------------------------------------------------------------------- */

    fn indexToFileName (& mut self, inx: usize) -> String
    {
        if inx < 0
        {
           return String::new();
        }
        else
        {
           let value = &self.fileNames [inx];
           return value.to_string();
        }
    }

    fn fileNameToIndex (& mut self, name: String) -> usize
    {
        let mut inx : usize = 0;
        let len = self.fileNames.len ();
        while inx < len && self.fileNames [inx] != name
        {
           inx = inx + 1;
        }
        if inx == len
        {
           self.fileNames.push (name);
        }
        return inx;
    }

   /* ------------------------------------------------------------------- */

   fn openFile (& mut self, fileName: String)
   {
       let text = fs::read_to_string (&fileName)
                  .expect ("Cannot read source file");

       self.source = text;
       self.sourceLen = self.source.len ();
       self.charFileInx = self.fileNameToIndex (fileName);

       self.nextChar ();
       self.nextToken ();
   }

   fn openString (& mut self, sourceText: String)
   {
       self.source = sourceText;
       self.sourceLen = self.source.len ();

       self.nextChar ();
       self.nextToken ();
   }

   fn close (& mut self)
   {
   }

   /* ------------------------------------------------------------------- */

   fn nextChar (& mut self)
   {
       if self.charByteOfs < self.sourceLen
       {
          let code = self.source.chars().nth(0).unwrap(); // !?
          self.ch = code;

          self.charByteOfs = self.charByteOfs + 1;
          if self.ch == '\n'
          {
             self.charLineNum = self.charLineNum + 1;
             self.charColNum = 1;
          }
          else if self.ch != '\r'
          {
             self.charColNum = self.charColNum + 1;
          }
       }
       else
       {
          self.ch = '\0';
       }
   }

   /* ------------------------------------------------------------------- */

   fn isLetter (& self, c: char) -> bool
   {
       return c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || c == '_';
   }

   fn isDigit (& self, c: char) -> bool
   {
       return c >= '0' && c <= '9';
   }

   fn isLetterOrDigit (& self, c: char) -> bool
   {
       return self.isLetter (c) || self.isDigit (c);
   }

   /* ------------------------------------------------------------------- */

   pub fn nextToken (& mut self)
   {
       while (self.ch != '\0' && self.ch <= ' ')
       {
          self.nextChar ();
       }

       self.tokenText = "".to_string ();

       if self.isLetter (self.ch)
       {
          self.token = identifier;
          while self.isLetterOrDigit (self.ch)
          {
             self.tokenText.push (self.ch);
             self.nextChar ();
          }
       }
       else
       {
          self.token = separator;
          self.tokenText.push (self.ch);
          self.nextChar ();
       }
   }

   /* ------------------------------------------------------------------- */

   pub fn readIdentifier (& mut self) -> String { return "".to_string (); }
   pub fn readNumber (& mut self) -> String { return "".to_string (); }
   pub fn readChar (& mut self) -> String { return "".to_string (); }
   pub fn readString (& mut self) -> String { return "".to_string (); }

   pub fn getTokenFileInx (& mut self) -> i32 { return 0; }
   pub fn getTokenLine (& mut self) -> i32 { return 0; }
   pub fn getTokenCol (& mut self) -> i32 { return 0; }

/* ------------------------------------------------------------------- */

} // end of impl Lexer

/* ---------------------------------------------------------------------- */

/*
fn main ()
{
   let mut lexer = Lexer::new ();
   lexer.openFile (String::from ("../../view/cmm/cmm.g"));
   while (lexer.token != eos)
   {
      let b = & lexer.tokenText;
      let s =  String::from_utf8 (b.to_vec ()). expect ("Found invalid UTF-8");
      print! ("{} ", s);
      lexer.nextToken ();
   }
   lexer.close ();
}
*/


// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
