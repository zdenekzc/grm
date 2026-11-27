
(**************************************************************************)
(*                                                                        *)
(*                               Source files                             *)
(*                                                                        *)
(**************************************************************************)

UNIT Fil0;

INTERFACE

Uses SysUtils {func LowerCase - do not use LowerCase from System},
     Classes  {type TStream};

{------------------------------- Characters -------------------------------}

Const letter    = ['A'..'Z', 'a'..'z', '_', chr(128) .. chr(255)];
      digit     = ['0'..'9'];
      lod       = letter + digit;
      HexDigit  = ['0'..'9', 'A'..'F', 'a'..'f'];

      quote1 = '''';
      quote2 = '"';
      backslash = '\';
      cr = ^M;
      lf = ^J;

{--------------------------- Memory allocation ----------------------------}

Type TAlloc = class
        AllocNext: TAlloc;
        AllocPrev: TAlloc;
        constructor Create;
        destructor Destroy; override;
     end;

Var  AllocCount: integer; { number of items }
     AllocSize:  integer; { size of all items }

Var  AllocFirst: TAlloc; { first item }
     AllocLast:  TAlloc; { last item }

Procedure AllocInit;

{--------------------------- Source file names ----------------------------}

Type TSource = class (TAlloc)
        FileName: string;
        next:     TSource;
     end;

Var  SourceFirst: TSource; { seznam zdrojovych souboru }
     SourceLast:  TSource;
     SourceCount: integer; { pocet zdrojovych souboru }

Procedure SourceInit;
Function  SourceAdd (FileName: string): integer;
Function  GetSource (FileInx: integer): string;

{-------------------------------- Location --------------------------------}

Type  TLocation = record
         FileInx: integer;
         CharPos: integer;
         LineNum: integer;
         ColNum:  integer;
      end;

Const NoLoc: TLocation = (FileInx: 0; CharPos: -1; LineNum: 1; ColNum: 0);

{----------------------------- Error messages -----------------------------}

Type ECompile = class (Exception);

Var  ErrMsg:  string;    { error message }
     ErrFile: string;    { file name }
     ErrLoc:  TLocation; { error location }

Procedure Error (msg: string); { compiler error }
Procedure Bug;                 { internal error }

{----------------------------- Input Records ------------------------------}

Const InpBuffSize = 4 * 1024;
Type  InpBuff     = array [0..InpBuffSize-1] of char;

Type  TInp = class (TAlloc)
         Loc:      TLocation;      { current position }
         FileIncl: boolean;        { true => include file }

         FileEnd:  boolean;        { end of file }
         FileExt:  byte;           { extension after end of file }

         BufPos:   integer;        { buffer position }
         BufLen:   integer;        { number of characters in buffer }

         FileVar:  TStream;        { source file }
         FileBuf:  InpBuff;        { buffer }

         SaveCh:   char;           { save current character }
         link:     TInp;           { next open input record }
      end;

{--------------------------------------------------------------------------}

Var  InpCh:       char;      { curent character }
     Inp:         TInp;      { current open file }

     SymLoc:      TLocation; { location of current symbol }
     SearchPath:  string;    { search path for units and include file }

Const InpLineMax = 255;
Var   InpLine: string [InpLineMax]; { current line - for debugging }

{--------------------------------------------------------------------------}

Procedure GetCh;                       { get curent character }
Function  EndOfSource: boolean;        { end of source file }

Procedure CloseAll;                    { close all input files }

Procedure OpenIncl (name: string);     { open include file and read first character }
Procedure CloseIncl;                   { close include file }

Procedure OpenSrc (name: string);     { open module file and read first character }
Procedure CloseSrc;                   { close module }

Procedure OpenStr (txt: string);
Procedure CloseStr;

Procedure InitFil (p_search_path: string); { initialization on new project }

Function FileNameExist (name: string): boolean;

IMPLEMENTATION

(*************************** MEMORY ALLOCATION ****************************)

Constructor TAlloc.Create;
Begin
     inherited Create;

     Assert (AllocNext = nil);
     Assert (AllocPrev = nil);

     inc (AllocCount);
     {$IFNDEF CONV} inc (AllocSize, InstanceSize); {$ENDIF}

     self.AllocPrev := AllocLast;

     if AllocFirst = nil then begin
        AllocFirst := self;
        AllocLast := self;
     end
     else begin
        AllocLast.AllocNext := self;
        AllocLast := self;
     end;
End;

Destructor TAlloc.Destroy;
Begin
     dec (AllocCount);
     {$IFNDEF CONV} dec (AllocSize, InstanceSize); {$ENDIF}

     if AllocPrev=nil then AllocFirst := AllocNext
                      else AllocPrev.AllocNext := AllocNext;

     if AllocNext=nil then AllocLast := AllocPrev
                      else AllocNext.AllocPrev := AllocPrev;

     inherited Destroy;
End;

Procedure AllocInit;
Begin
     AllocFirst := nil; { first item }
     AllocLast  := nil; { last item }

     AllocCount := 0; { number of items }
     AllocSize  := 0; { size of all items }
End;

(****************************** SOURCE FILES ******************************)

Procedure SourceInit;
Begin
     SourceFirst := nil;
     SourceLast := nil;
     SourceCount := 0;
End;

Function SourceAdd (FileName: string): integer;
Var  item: TSource;
Begin
     item := TSource.Create;
     item.FileName := FileName;
     item.next := nil;

     if SourceFirst = nil then begin
        SourceFirst := item;
        SourceLast := item;
     end
     else begin
        SourceLast.next := item;
        SourceLast := item;
     end;

     inc (SourceCount);
     result := SourceCount;
End;

Function GetSource (FileInx: integer): string;
Var  p: TSource;
     n: integer;
Begin
     p := SourceFirst;
     n := 1;

     while (p <> nil) and (n <> FileInx) do begin
        inc (n);
        p := p.next;
     end;

     if p = nil then result := ''
                else result := p.FileName;
End;

(***************************** ERROR MESSAGES *****************************)

Procedure Error (msg: string);
Begin
     ErrMsg := msg;
     ErrLoc := SymLoc;
     ErrFile := GetSource (SymLoc.FileInx);

     writeln;
     write   ('File: ', GetSource (SymLoc.FileInx), ' ');
     write   ('Line: ', SymLoc.LineNum, ' ');
     write   ('Col: ',  SymLoc.ColNum, ' ');
     writeln ('Ofs: ',  SymLoc.CharPos, ' ');
     writeln ('Source: ', InpLine);
     writeln ('Error: ',  msg);

     {$IFNDEF CONV} halt; { !! debug => stack dump } {$ENDIF}
     raise ECompile.Create (msg);
End;

Procedure Bug;
Begin
     Error ('Bug');
End;

(******************************* FILE NAMES *******************************)

Function FileSearch_Alt (name, dirlist: string): string;
Const TmpMax = 255;
Var   inx, len, i: integer;
      tmp: string [TmpMax];
      // info: Linux.Stat;
Begin
     result := '';

     { check current directory }
     if FileExists (name) then
        result := name

     { other directories }
     else begin
        inx := 1; { next character position }
        len := length (dirlist);

        while inx <= len do begin

           i := 0;
           while (inx <= len) and (dirlist [inx] <> ';') do begin

              { store character }
              if i < TmpMax then begin
                 inc (i);
                 tmp [i] := dirlist [inx];
              end;

              { next character }
              inc (inx);
           end;

           if inx <= len then inc (inx); { skip semicolon }

           if i > 0 then begin
              tmp [0] := chr (i);
              if tmp[i] <> '/' then tmp := tmp + '/';
              tmp := tmp + name;

              if FileExists (tmp) then begin
                 result := tmp;
                 inx := len+1; { stop }
              end;
           end;

        end;
     end;
End;

Function LookupFileName (name, path: string): string;
Begin
     if ExtractFilePath (name) <> '' then
        result := name
     else begin
        name := SysUtils.LowerCase (name);

        if ExtractFileExt (name) <> '' then
           result := FileSearch_Alt (name, path)
        else begin
           result := FileSearch_Alt (ChangeFileExt (name, '.pas'), path);
           if result = '' then
              result := FileSearch_Alt (ChangeFileExt (name, '.pp'), path);
        end;
     end;
End;

Function CompleteFileName (name, path: string): string;
Begin
     result := LookupFileName (name, path);

     if result = '' then
        Error ('Cannot find source file ' + name);

     {$IFDEF AAA}
     result := ExpandFileName (result);
     {$ENDIF}
End;

Function FileNameExist (name: string): boolean;
Begin
     result := LookupFileName (name, SearchPath) <> '';
End;

(********************************* INPUT **********************************)

Procedure GetCh;
Label again;
Begin
     again:
     Assert (Inp <> nil, 'source is not open');

     if Inp.BufPos < Inp.BufLen then begin
        { read character from buffer }
        InpCh := Inp.FileBuf [Inp.BufPos];
        inc (Inp.BufPos);
        inc (Inp.Loc.CharPos);
      end

     else if not Inp.FileEnd then begin
        { read next block }
        Inp.BufLen := Inp.FileVar.Read (Inp.FileBuf, InpBuffSize);
        Inp.BufPos := 0;
        Inp.FileEnd := (Inp.BufLen = 0);
        goto again;
     end

     else if Inp.FileIncl then begin
        { close include file }
        CloseIncl;
        { next character is ready }
     end

     else if Inp.FileExt = 0 then begin
        { end of line after last line }
        InpCh := lf;
        inc (Inp.FileExt);
     end

     else Error ('Unexpected end of source text');

     { update position }
     if InpCh = lf then begin
        inc (Inp.Loc.LineNum);
        Inp.Loc.ColNum := 0;
     end
     else begin
        if Inp.Loc.ColNum = 0 then InpLine := '';
        inc (Inp.Loc.ColNum);
        if length (InpLine) < InpLineMax  then begin
           inc (InpLine [0]);
           InpLine [length (InpLine)] := InpCh;
        end;
     end;

End;

Function EndOfSource: boolean;
Begin
     Assert (Inp <> nil, 'source is not open');
     result := Inp.FileEnd and not Inp.FileIncl;
End;

{--------------------------------------------------------------------------}

Procedure InpAdd;
Var  tmp: TInp;
Begin
     tmp := Inp;
     Inp := TInp.Create;
     Inp.link := tmp;
End;

Procedure InpRemove;
Var  tmp: TInp;
Begin
     Assert (Inp <> nil, 'InpAdd / InpRemove mismatch');

     tmp := Inp;
     Inp := Inp.link;
     tmp.Free;
End;


(************************** OPEN / CLOSE STREAM ***************************)

Procedure OpenStream (p_stream: TStream;
                      p_file_inx: integer;
                      p_incl: boolean);
Begin
     { new input record }
     InpAdd;

     { set parameters }
     Inp.Loc         := NoLoc;
     Inp.Loc.FileInx := p_file_inx;

     Inp.FileVar  := p_stream;
     Inp.FileIncl := p_incl;
     Inp.FileEnd  := false;
     Inp.FileExt  := 0;
     Inp.BufPos   := 0;  { ready to read next character }
     Inp.BufLen   := 0;
     Inp.SaveCh   := InpCh; { save current character }

     InpCh := ' '; { not necessary }

     { read first character }
     GetCh;
End;

Procedure CloseStream;
Begin
     Assert (Inp <> nil, 'source is not open');

     { close file }
     Inp.FileVar.Free;
     Inp.FileVar := nil;

     { restore current character }
     InpCh  := Inp.SaveCh;

     { set current input record }
     InpRemove;
End;

Procedure CloseAll;
Begin
     { close all input files }
     while Inp <> nil do
        CloseStream;
End;

(******************************* OPEN FILE ********************************)

Procedure OpenFil (name: string; p_incl: boolean);
Var  stream: TFileStream;
     inx: integer;
Begin
     { open file }
     if name = '' then Error ('Empty file name');
     name := CompleteFileName (name, SearchPath);

     stream := TFileStream.Create (name, fmOpenRead);
     if stream = nil then Error ('Cannot open ' + name);

     inx := SourceAdd (name);

     OpenStream (stream, inx, p_incl);
End;

(***************************** INCLUDE FILES ******************************)

Procedure OpenIncl (name: string);
Begin
     Assert (Inp <> nil, 'module is not open');
     name := CompleteFileName (name, SearchPath);
     OpenFil (name, true);
End;

Procedure CloseIncl;
Begin
     CloseStream;
     Assert (Inp <> nil, 'OpenIncl / CloseIncl mismatch');
End;

(****************************** MODULE FILES ******************************)

Procedure StartFil; forward;

Procedure OpenSrc (name: string);
Begin
     StartFil;
     Assert (Inp = nil, 'Unit is already open');
     OpenFil (name, false);
End;

Procedure CloseSrc;
Begin
     while (Inp <> nil) and Inp.FileIncl do CloseIncl;
     CloseStream;
     Assert (Inp = nil);
End;

(*************************** INPUT FROM STRING ****************************)

Procedure OpenStr (txt: string);
Var  stream: TStringSTream;
Begin
     StartFil;
     Assert (Inp = nil, 'Unit is already open');
     stream := TStringStream.Create (txt);
     OpenStream (stream, 0, false);
End;

Procedure CloseStr;
Begin
     CloseSrc;
End;

(********************************* CLEAR **********************************)

Procedure InitFil (p_search_path: string);
{ new project }
Begin
     SearchPath := p_search_path; { important - valid path }
     SourceInit; { important - empty list }

     ErrMsg := '';
     ErrFile := '';
     ErrLoc := NoLoc;
End;

Procedure StartFil;
{ new unit }
Begin
     Inp := nil;      { important - no open source file }
     SymLoc := NoLoc; { not necessary - GetSymbol }

     InpCh := ' ';    { not necessary - OpenFil }
     Inp := nil;      { not necessary - StartFil}
     SymLoc := NoLoc; { not necessary - GetSymbol }
     InpLine := '';   { not necessary - StartFil }
End;

BEGIN
     AllocInit;     { important }
     InpLine := ''; { not necessary - only for debugging }
END.

