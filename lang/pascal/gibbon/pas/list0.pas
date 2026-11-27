UNIT List0;

INTERFACE

Uses // SysUtils,
     Classes,
     Fil0, Dir0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF};

{------------------------------ OUTPUT LIST -------------------------------}

Const OutBufSize = 1024 - 16;
Type  TOutputBuffer = array [0..OutBufSize-1] of char;

Type TOutputItem = class
     private
        Next:  TOutputItem;
        Prev:  TOutputItem;

        Len:   integer;
        Buf:   TOutputBuffer;
     end;

     TOutputSect = class
     private
        First: TOutputItem;
        Last:  TOutputItem;

        procedure Add (item: TOutputItem);

     private
        Indent: integer; { odsazeni od leveho okraje }
        Start:  boolean; { true => zacatek radku }
        Count:  integer; { delka vystupu }

        procedure NewBuf;
        procedure SendChr (c: char);

     public
        { store text }
        Procedure Send (txt: string);   { store string }
        Procedure SendEol;              { store end of line }
        Procedure SendLn (txt: string); { store string plus end }

        Procedure SetIndent (indent: integer); { set indentation }
        Procedure IncrIndent (n: integer); { increment indentation }
        Procedure DecrIndent (n: integer); { decrement indentation }
        Procedure IncIndent; { increment indentation by 3 columns }
        Procedure DecIndent; { decrement indentation }

        { recall text }
        function GetSize: integer;
        function GetString: string;

        procedure WriteToStream (stream: TStream);
        procedure Save (FileName: string);

        {$IFDEF OTHER}
        function GetStream: TMemoryStream;
        procedure Save2 (FileName: string);
        {$ENDIF}


        constructor Create;
        destructor Destroy; override;
     end;

{--------------------------------- OUTPUT ---------------------------------}

Var OutList: TOutputSect;

Procedure OpenOut;  { open output }
Procedure CloseOut; { close output }

Procedure Send (txt: string); { send string to output }
Procedure SendEol;            { send end of line to output }
Procedure SendLn (txt: string);

Function StartOfLine: boolean;

Procedure SetIndent (indent: integer);
Procedure IncIndent;
Procedure DecIndent;
Procedure IncrIndent (n: integer);
Procedure DecrIndent (n: integer);

IMPLEMENTATION

(****************************** OUTPUT LIST *******************************)

Procedure TOutputSect.Add (item: TOutputItem);
Begin
     Assert (item <> nil);
     Assert (item.Prev = nil);
     Assert (item.Next = nil);

     item.Prev := Last;
     item.Next := nil;

     if First = nil then First := item
                    else Last.Next := item;

     Last := item;
End;

Destructor TOutputSect.Destroy;
Var  p, t: TOutputItem;
Begin
     p := first;
     while p <> nil do begin
        t := p.next;
        p.Free;
        p := t;
     end;
End;

(******************************* STORE TEXT *******************************)

Const OutLimit = 1000000; { max. delka vystupu - pouze pro kontrolu }

Constructor TOutputSect.Create;
Begin
     Indent := 0;
     Start := true;
     Count := 0;
End;

Procedure TOutputSect.NewBuf;
Begin
     Add (TOutputItem.Create);
     Assert (Last.Len = 0);
End;

Procedure TOutputSect.SendChr (c: char);
Begin
     if (Last = nil) or (Last.Len + 1 > OutBufSize) then NewBuf;
     Last.Buf [Last.Len] := c;

     inc (Last.Len);
     inc (Count);
End;

Procedure TOutputSect.Send (txt: string);
Var  i, len, inx, step: integer;
Begin
     if Start then begin
        for i := 1 to Indent do SendChr (' ');
        Start := false;
        inc (Count, Indent);
     end;

     len := length (txt);
     inx := 1;
     while inx <= len do begin
        if (Last = nil) or (Last.Len >= OutBufSize) then NewBuf;
        step := len-inx+1;
        if Last.Len+step > OutBufSize then step := OutBufSize-Last.Len;

        move (txt[inx], Last.Buf[Last.Len], step);

        inc (Last.Len, step);
        inc (inx, step);
     end;

     inc (Count, length (txt));
     if Count > OutLimit then Error ('Output too long');
End;

Procedure TOutputSect.SendEol;
Begin
     // SendChr (cr);
     SendChr (lf);
     Start := true;
End;

Procedure TOutputSect.SendLn (txt: string);
Begin
     Send (txt);
     SendEol;
End;

Procedure TOutputSect.SetIndent (indent: integer);
Begin
     Indent := indent;
End;

Procedure TOutputSect.IncrIndent (n: integer);
Begin
     inc (Indent, n);
End;

Procedure TOutputSect.DecrIndent (n: integer);
Begin
     dec (Indent, n);
End;

Procedure TOutputSect.IncIndent;
Begin
     inc (Indent, 3);
End;

Procedure TOutputSect.DecIndent;
Begin
     dec (Indent, 3);
End;

(****************************** RECALL TEXT *******************************)

Function TOutputSect.GetSize: integer;
Var  p: TOutputItem;
Begin
     result := 0;
     p := First;
     while p <> nil do begin
        inc (result, p.len);
        p := p.Next;
     end;
End;

Function TOutputSect.GetString: string;
Var  size: integer;
     p: TOutputItem;
     ref: PChar;
Begin
     size := GetSize;

     { create string }
     result := '';
     SetLength (result, size);

     { store data }
     ref := PChar (result);
     p := First;

     while p <> nil do begin
        move (p.Buf[0], PChar (ref)^, p.len);
        inc (ref, p.len);
        p := p.Next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure TOutputSect.WriteToStream (stream: TStream);
Var  p: TOutputItem;
Begin
     Assert (stream <> nil);
     p := First;
     while p <> nil do begin
        stream.WriteBuffer (p.Buf[0], p.len);
        p := p.Next;
     end;
End;

{$IFDEF OTHER}

Function TOutputSect.GetStream: TMemoryStream;
Begin
     result := TMemoryStream.Create;
     result.Size := GetSize; { pre-allocate }
     WriteToStream (result);
End;

{$ENDIF}

{--------------------------------------------------------------------------}

Procedure TOutputSect.Save (FileName: string);
Var stream: TFileStream;
Begin
     stream := TFileStream.Create (FileName, fmCreate);
     WriteToStream (stream);
End;

{$IFDEF OTHER}

Procedure TOutputSect.Save2 (FileName: string);
Var  f: file;
     p: TOutputItem;
Begin
     Assign (f, FileName);
     Rewrite (f, 1);

     p := First;
     while p <> nil do begin
        BlockWrite (f, p.Buf[0], p.len);
        p := p.Next;
     end;

     Close (f);
End;

{$ENDIF}

(********************************* OUTPUT *********************************)

Procedure OpenOut;
Begin
     OutList.Free;
     OutList := TOutputSect.Create;
End;

Procedure CloseOut;
Begin
End;

Procedure Send (txt: string);
Begin
     OutList.Send (txt);
End;

Procedure SendEol;
Begin
     OutList.SendEol;
End;

Procedure SendLn (txt: string);
Begin
     OutList.SendLn (txt);
End;

Function StartOfLine: boolean;
Begin
     result := OutList.Start;
End;

Procedure SetIndent (indent: integer);
Begin
     OutList.SetIndent (indent);
End;

Procedure IncrIndent (n: integer);
Begin
     OutList.IncrIndent (n);
End;

Procedure DecrIndent (n: integer);
Begin
     OutList.DecrIndent (n);
End;

Procedure IncIndent;
Begin
     OutList.IncIndent;
End;

Procedure DecIndent;
Begin
     OutList.DecIndent;
End;

BEGIN
     OutList := nil; { important }
END.
