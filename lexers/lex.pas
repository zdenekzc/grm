
(**************************************************************************)
(*                                                                        *)
(*                            Lexical Analysis                            *)
(*                                                                        *)
(**************************************************************************)

UNIT Lex;

INTERFACE

Uses TypInfo, SysUtils,
     Fil, Dir;

{$DEFINE COMMENTS}

{--------------------------------------------------------------------------}

Type TSymbol = ( AndSy, ArraySy, AsSy, AsmSy,
                 BeginSy,
                 CaseSy, ClassSy, ConstSy, ConstructorSy,
                 DestructorSy, DispinterfaceSy, DivSy, DoSy, DowntoSy,
                 ElseSy, EndSy, ExceptSy, ExportsSy,
                 FileSy, FinalizationSy, FinallySy, ForSy, FunctionSy,
                 GotoSy,
                 IfSy, ImplementationSy, InSy, InheritedSy,
                 InitializationSy, InlineSy, InterfaceSy, IsSy,
                 LabelSy, LibrarySy,
                 ModSy,
                 NilSy, NotSy,
                 ObjectSy, OfSy, OnSy, OrSy, OutSy,
                 PackedSy, ProcedureSy, ProgramSy, PropertySy,
                 RaiseSy, RecordSy, RepeatSy, ResourcestringSy,
                 SetSy, ShlSy, ShrSy, StringSy,
                 ThenSy, ThreadvarSy, ToSy, TrySy, TypeSy,
                 UnitSy, UntilSy, UsesSy,
                 VarSy,
                 WhileSy, WithSy,
                 XorSy,

                 AbsoluteSy, AbstractSy, AssemblerSy, AtSy, AutomatedSy,
                 CdeclSy,
                 DefaultSy, DispidSy, DynamicSy,
                 ExportSy, ExternalSy,
                 FarSy, ForwardSy, FriendSy,
                 ImplementsSy, IndexSy,
                 MessageSy,
                 NameSy, NearSy, NodefaultSy,
                 OverloadSy, OverrideSy,
                 PascalSy, PrivateSy, ProtectedSy, PublicSy, PublishedSy,
                 ReadSy, ReadonlySy, RegisterSy, ReintroduceSy, ResidentSy,
                 SafecallSy, StdcallSy, StoredSy,
                 VirtualSy,
                 WriteSy, WriteonlySy,

                 HighSy, LowSy,
                 OffsetSy, PtrSy, SegSy, { assembler }

                 PlusSy, MinusSy, AsteriskSy, SlashSy,
                 PeriodSy, CommaSy, ColonSy, SemicolonSy,
                 EqualSy, LessSy, GreaterSy,
                 UnequalSy, LessEqualSy, GreaterEqualSy,
                 ArrowSy, AtSignSy, RangeSy, AssignSy,
                 LParSy, RParSy, LBrackSy, RBrackSy,

                 AndSignSy, EolSy, { assembler }

                 IdentSy, NumberSy, FloatSy, StrSy);

{--------------------------------------------------------------------------}

Const FirstReserved = AndSy;
      LastReserved  = XorSy;

      FirstDirective = AbsoluteSy;
      LastDirective  = WriteOnlySy;

Const IdentMax  = 255;
      NumberMax = 255;
      StringMax = 255;

Const StoreUpperCase = false;
      CompareUpperCase = true;

Type  TIdent = string;

{--------------------------------------------------------------------------}

Var   sy:         TSymbol;   { current symbol }
      range:      boolean;   { true => next symbol is RangeSy }
      AsmSym:     boolean;   { true => asm symbols }

      IdentVal:   string [IdentMax];   { identifier }
      NumberVal:  string [NumberMax];  { integer / float number }
      StringVal:  string [StringMax];  { string (without quotes) }

{--------------------------------------------------------------------------}

Procedure GetSymbol;                    { get a symbol to variable 'sy' }

Procedure ConvControlCharacters;        { control characters }
Procedure ConvDirective;                { directives }
Procedure ConvClassDirective;           { class directives }
Procedure RemoveDirective;

Procedure MissingSymbol (par: TSymbol); { symbol par expected }
Procedure VerifySymbol (par: TSymbol);  { check sy=par }
Procedure CheckSymbol (par: TSymbol);   { check sy=par and get next symbol }
Function  SymbolToString: string;       { convert current symbol to string }

Function ConvIdent (id: TIdent): TIdent;

Function ReadUntil (stop: char): string;       { clist - import friends }

{--------------------------------------------------------------------------}

Type TNote = class
        new_line:    boolean; { new line, not commant }
        left_mark:   boolean; { first comment line }
        right_mark:  boolean; { last comment line }
        single_line: boolean; { single line form of comment }

        late:        boolean; { poznamka pred minulym lexikalnim symbolem }
        skip:        boolean; { vynechat }
        used:        boolean; { poznamka byla odeslan na vystup }

        comment:     string;
        next:        TNote;
     end;

     TNoteList = class
        first: TNote;
        last:  TNote;
        procedure Add (item: TNote);
     end;

Function GetNotes: TNote;
Function GetStartNotes: TNote;
Function GetStopNotes: TNote;

Procedure JoinNotes (var dst: TNote; src: TNote);

{--------------------------------------------------------------------------}

Procedure ClearLex;
Procedure StartLex;

{$IFDEF FPC}
Function CompareStr (const a, b: string): integer;
{$ENDIF}

IMPLEMENTATION

{--------------------------------------------------------------------------}

{$IFDEF FPC}
Function CompareStr (const a, b: string): integer;
Begin
     if a < b then result := -1
     else if a > b then result := 1
     else result := 0;
End;
{$ENDIF}

(******************************** COMMENTS ********************************)

Const ComMax = 255;

Var   ComLen: integer;
      ComBuf: string [ComMax]; { buffer for current comment }

Var   InpNote:    TNote;     { current comment }
      InpNotes:   TNoteList; { list of comments }
      LateNotes:  TNoteList; { comments before current symbol }
      StoreNotes: boolean;

Procedure StoreComBuf;
Begin
     SetLength (ComBuf, ComLen);
     InpNote.comment := ComBuf;
     ComLen := 0;

     Assert (InpNote <> nil);
     InpNotes.Add (InpNote);
     InpNote := nil;
End;

Procedure InitComment (single_line: boolean);
Begin
     {$IFDEF COMMENTS}
     if StoreNotes then begin
        Assert (InpNote = nil);
        InpNote := TNote.Create;
        if single_line then InpNote.single_line := true
                       else InpNote.left_mark := true;
        ComLen := 0;
     end;
     {$ENDIF}
End;

Procedure StoreCommentCharacter (ch: char);
Begin
     {$IFDEF COMMENTS}
     if StoreNotes then begin
        if ch = lf then begin
           StoreComBuf; { store current record }
           InpNote := TNote.Create; { continue with new record }
        end
        else begin
           if ComLen < ComMax then begin
              inc (ComLen);
              ComBuf [ComLen] := ch;
           end;
        end;
     end;
     {$ENDIF}
End;

Procedure FinishComment;
Begin
     {$IFDEF COMMENTS}
     if StoreNotes then begin
        if not InpNote.single_line then InpNote.right_mark := true;
        StoreComBuf; { store current record }
        InpNote := nil;
     end;
     {$ENDIF}
End;

Procedure StoreNewLine;
Var  note: TNote;
Begin
     {$IFDEF COMMENTS}
     if StoreNotes then begin
        Assert (InpNote = nil);
        note := TNote.Create;
        note.new_line := true;
        InpNotes.Add (note);
     end;
     {$ENDIF}
End;

Procedure Join (dst: TNoteList; src: TNoteList);
Begin
     if src.first <> nil then begin

        if dst.first = nil then begin
           dst.first := src.first;
           dst.last := src.last;
        end
        else begin
           Assert (dst.last <> nil);
           dst.last.next := src.first;
           dst.last := src.last;
        end;

        { clear source }
        src.first := nil;
        src.last := nil;
     end;
End;

Procedure ShiftNotes;
{ Mark InpNotes as late }
Var  p: TNote;
Begin
     {$IFDEF COMMENTS}
     if InpNotes.First <> nil then begin

        { mark as late }
        p := InpNotes.First;
        while p <> nil do begin
           p.late := true;
           p := p.next;
        end;

        Join (LateNotes, InpNotes);
     end;
     {$ENDIF}
End;

Function GetNotes: TNote;
Begin
     Join (LateNotes, InpNotes);
     result := LateNotes.First;

     { clear list of late notes }
     LateNotes.First := nil;
     LateNotes.Last := nil;
End;

Function GetStartNotes: TNote;
Var  p: TNote;
Begin
     result := GetNotes;

     p := result;

     while (p <> nil) and p.late do
        p := p.next;

     while (p <> nil) and p.new_line do begin
        p.skip := true;
        p := p.next;
     end;
End;

Function GetStopNotes: TNote;
Begin
     if (InpNotes.last <> nil) and InpNotes.last.new_line then
        InpNotes.last.skip := true;

     result := GetNotes;
End;


(*
Function Stop (p: TNote): boolean;
Begin
     result := p.new_line and ((p.next = nil) or p.new_line);
End;

Function GetStopNotes: TNote;
{ Odebrat komentare ze seznamu
  zastavit pred dvema volnymi radkami nebo pred konccovou volnou radkou }
Var  p: TNote;
Begin
     p := InpNotes.First;

     if (p = nil) or Stop (p) then
        result := nil
     else begin
        while (p.next <> nil) and not Stop (p) do
           p := p.next;

        if p.next <> nil then begin
           { zkratit seznam InpNotes }
           result := InpNotes.First;
           InpNotes.First := p.next;
           p.next := nil;
        end
        else result := GetNotes;
     end;
End;
*)

Procedure TNoteList.Add (item: TNote);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure JoinNotes (var dst: TNote; src: TNote);
Var  p: TNote;
Begin
     if src <> nil then begin
        if dst = nil then
           dst := src
        else begin
           p := dst;
           while p.next <> nil do p := p.next;
           p.next := src;
        end;
     end;
End;

(**************************** LEXICAL ANALYSIS ****************************)

Const KeyMax = 66;

Type  KeyStr = string;
      KeyRec = record t: KeyStr; s: TSymbol; end;

Const KeyTab: array [1..KeyMax] of KeyRec =
      (( t:'AND'              ; s:AndSy              ),
       ( t:'ARRAY'            ; s:ArraySy            ),
       ( t:'AS'               ; s:AsSy               ),
       ( t:'ASM'              ; s:AsmSy              ),
       ( t:'BEGIN'            ; s:BeginSy            ),
       ( t:'CASE'             ; s:CaseSy             ),
       ( t:'CLASS'            ; s:ClassSy            ),
       ( t:'CONST'            ; s:ConstSy            ),
       ( t:'CONSTRUCTOR'      ; s:ConstructorSy      ),
       ( t:'DESTRUCTOR'       ; s:DestructorSy       ),
       ( t:'DISPINTERFACE'    ; s:DispinterfaceSy    ),

       ( t:'DIV'              ; s:DivSy              ),
       ( t:'DO'               ; s:DoSy               ),
       ( t:'DOWNTO'           ; s:DowntoSy           ),
       ( t:'ELSE'             ; s:ElseSy             ),
       ( t:'END'              ; s:EndSy              ),
       ( t:'EXCEPT'           ; s:ExceptSy           ),
       ( t:'EXPORTS'          ; s:ExportsSy          ),
       ( t:'FILE'             ; s:FileSy             ),
       ( t:'FINALIZATION'     ; s:FinalizationSy     ),
       ( t:'FINALLY'          ; s:FinallySy          ),
       ( t:'FOR'              ; s:ForSy              ),
       ( t:'FUNCTION'         ; s:FunctionSy         ),
       ( t:'GOTO'             ; s:GotoSy             ),
       ( t:'IF'               ; s:IfSy               ),
       ( t:'IMPLEMENTATION'   ; s:ImplementationSy   ),
       ( t:'IN'               ; s:InSy               ),
       ( t:'INHERITED'        ; s:InheritedSy        ),
       ( t:'INITIALIZATION'   ; s:InitializationSy   ),
       ( t:'INLINE'           ; s:InlineSy           ),
       ( t:'INTERFACE'        ; s:InterfaceSy        ),
       ( t:'IS'               ; s:IsSy               ),
       ( t:'LABEL'            ; s:LabelSy            ),
       ( t:'LIBRARY'          ; s:LibrarySy          ),
       ( t:'MOD'              ; s:ModSy              ),
       ( t:'NIL'              ; s:NilSy              ),
       ( t:'NOT'              ; s:NotSy              ),
       ( t:'OBJECT'           ; s:ObjectSy           ),
       ( t:'OF'               ; s:OfSy               ),
       ( t:'ON'               ; s:OnSy               ),
       ( t:'OR'               ; s:OrSy               ),
       ( t:'OUT'              ; s:OutSy              ),
       ( t:'PACKED'           ; s:PackedSy           ),
       ( t:'PROCEDURE'        ; s:ProcedureSy        ),
       ( t:'PROGRAM'          ; s:ProgramSy          ),
       ( t:'PROPERTY'         ; s:PropertySy         ),
       ( t:'RAISE'            ; s:RaiseSy            ),
       ( t:'RECORD'           ; s:RecordSy           ),
       ( t:'REPEAT'           ; s:RepeatSy           ),
       ( t:'RESOURCESTRING'   ; s:ResourcestringSy   ),
       ( t:'SET'              ; s:SetSy              ),
       ( t:'SHL'              ; s:ShlSy              ),
       ( t:'SHR'              ; s:ShrSy              ),
       ( t:'STRING'           ; s:StringSy           ),
       ( t:'THEN'             ; s:ThenSy             ),
       ( t:'THREADVAR'        ; s:ThreadvarSy        ),
       ( t:'TO'               ; s:ToSy               ),
       ( t:'TRY'              ; s:TrySy              ),
       ( t:'TYPE'             ; s:TypeSy             ),
       ( t:'UNIT'             ; s:UnitSy             ),
       ( t:'UNTIL'            ; s:UntilSy            ),
       ( t:'USES'             ; s:UsesSy             ),
       ( t:'VAR'              ; s:VarSy              ),
       ( t:'WHILE'            ; s:WhileSy            ),
       ( t:'WITH'             ; s:WithSy             ),
       ( t:'XOR'              ; s:XorSy              ));

Const AsmMax = 5;

Const AsmTab: array [1..AsmMax] of KeyRec =
      (( t:'HIGH'             ; s:HighSy             ),
       ( t:'LOW'              ; s:LowSy              ),
       ( t:'OFFSET'           ; s:OffsetSy           ),
       ( t:'PTR'              ; s:PtrSy              ),
       ( t:'SEG'              ; s:SegSy              ));

Const AsmLetter = ['@', '%', '.', '$'];
      AsmLod    = ['@'];

Procedure GetIdent;
Var   len: integer;
      a, b, c: integer;
      cmp: integer;
      tmp: string;
Begin
     len := 1;
     if StoreUpperCase then IdentVal [len] := UpCase (InpCh)
                       else IdentVal [len] := InpCh;
     GetCh;

     while (InpCh in lod) or AsmSym and (InpCh in AsmLod ) do begin
        inc (len);
        if len > IdentMax then Error ('Identifier too long');
        if StoreUpperCase then IdentVal [len] := UpCase (InpCh)
                          else IdentVal [len] := InpCh;
        GetCh;
     end;

     IdentVal [0] := chr (len);
     sy := IdentSy;

     tmp := IdentVal;
     if CompareUpperCase then tmp := UpperCase (tmp);

     a := 1;                               { RESERWED WORD }
     b := KeyMax;
     while a<=b do begin
        c := (a+b) shr 1; { a <= c < b }
        cmp := CompareStr (tmp, KeyTab[c].t);
        if cmp < 0 then b := c-1
        else if cmp > 0 then a := c+1
        else begin sy := KeyTab[c].s; a := b+1; end;
     end;

     if AsmSym and (sy = IdentSy) then begin
        a := 1;
        b := AsmMax;
        while a<=b do begin
           c := (a+b) shr 1; { a <= c < b }
           cmp := CompareStr (tmp, AsmTab[c].t);
           if cmp < 0 then b := c-1
           else if cmp > 0 then a := c+1
           else begin sy := AsmTab[c].s; a := b+1; end;
        end;
     end;
End;

{--------------------------------- Number ---------------------------------}

Var num_len:     integer;
    number_test: int64;
    float_test:  extended;

Procedure Store; { store one character to 'NumberVal' }
Begin
     inc (num_len);
     if num_len > NumberMax then Error ('Number is too long');
     NumberVal [num_len] := UpCase (InpCh);
     GetCh;
End;

Procedure Digits;  { digit <digit> }
Var  hex: boolean;
Begin
     if not (InpCh in digit) then Error ('Digit expected');

     if AsmSym then begin
        hex := false;

        while InpCh in HexDigit do begin
           if not (InpCh in digit) then hex := true;
           Store;
        end;

        if (InpCh = 'h') or (InpCh = 'H') then Store
        else if hex then Error ('Error in numeric constant');
     end
     else begin
        while InpCh in digit do Store;
     end;
End;

Procedure GetNumber;
Var  float: boolean;
     code:  integer;
Begin
     float := false;
     num_len := 0;
     Digits;                                     { digit <digit> }

     if InpCh='.' then begin                     { '.' digit <digit> }
        Store;
        if InpCh='.' then begin                  { number and '..' }
           GetCh;
           dec (num_len);
           range := true;
        end
        else begin
           float := true;
           Digits;
        end;
     end;

     if not range then                           { 'E' ['+'|'-'] digit <digit>}
        if (InpCh='E') or (InpCh='e') then begin
           float := true;
           Store;
           if (InpCh='+') or (InpCh='-') then Store;
           Digits;
        end;

     { set length }
     NumberVal [0] := chr (num_len);

     if float then begin                         { floating point number }
        sy := FloatSy;
        val (NumberVal, float_test, code);
        if code<>0 then Error ('Bad float number');
     end
     else begin                                  { integer number }
        sy := NumberSy;
        if not AsmSym then begin { !? sestnactkova asm cisla, atd. }
           val (NumberVal, number_test, code);
           if code<>0 then Error ('Bad number');
        end;
     end;
End;

Procedure GetHexNumber;
Var  code:  integer;
Begin
     num_len := 0;
     Store; { store '$' }
     if not (InpCh in HexDigit) then Error ('Hexadecimal digit expected');
     while InpCh in HexDigit do Store;
     NumberVal [0] := chr (num_len);

     if AsmSym and (num_len = 1) then begin
        sy := IdentSy;
        IdentVal := '$';
     end
     else begin
        sy := NumberSy;
        val (NumberVal, number_test, code);
        if code<>0 then Error ('Bad number');
     end;
End;

{--------------------------------- String ---------------------------------}

Var str_len: integer;

Procedure StoreCh (par: char);
Begin
     inc (str_len);
     if str_len > StringMax then Error ('String too long');
     StringVal[str_len] := par;
End;

Procedure GetString;
Var  n: integer;
     t: char;
Begin
     str_len := 0;

     while InpCh in [quote, '#', '^'] do begin

        if InpCh = quote then begin
           repeat
              repeat
                 GetCh;
                 if InpCh = lf then
                    Error ('String exceeds line');
                 StoreCh (InpCh);
              until InpCh = quote;
              GetCh;
           until InpCh <> quote;
           dec (str_len);
        end

        else if InpCh = '#' then begin
           GetCh; { skip # }

           if InpCh = '$' then begin
              GetCh; { skip '$' }
              if not (InpCh in HexDigit) then
                 Error ('Hexadecimal digit expected');
              n := 0;
              while InpCh in HexDigit do begin
                 t := UpCase (InpCh);
                 if t >= 'A' then n := n*16 + ord (t) - ord ('A') + 10
                             else n := n*16 + ord (t) - ord ('0');
                 // if n > 255 then Error ('Bad character code');
                 GetCh;
              end;
           end

           else begin
              if not (InpCh in digit) then Error ('Digit expected');
              n := 0;
              while InpCh in digit do begin
                 n := n*10 + ord (InpCh) - ord ('0');
                 // if n > 255 then Error ('Bad character code');
                 GetCh;
              end;
           end;

           StoreCh (chr (n));
        end

        else begin
           GetCh; { skip ^ }
           n := ord (InpCh) - 64;
           if (n < 0) or (n > 31) then Error ('Bad control character');
           GetCh; { skip character }
           StoreCh (chr (n));
        end;

     end; {while}

     { set length }
     StringVal [0] := chr (str_len);

     sy := StrSy;
End;

{--------------------------------------------------------------------------}

Procedure Select2 (first: TSymbol; key: char; second: TSymbol);
Begin
     if InpCh <> key then sy := first
                  else begin GetCh; sy:=second; end;
End;

Procedure Select3 (first: TSymbol; key2: char; second: TSymbol;
                                   key3: char; third: TSymbol);
Begin
     if InpCh = key2 then begin GetCh; sy := second end
     else if InpCh = key3 then begin GetCh; sy := third end
     else sy := first;
End;

{--------------------------------------------------------------------------}

Procedure GetSymbol;
Label start, again, stop;
Var   dir: boolean;
      old: char;
      SkipNewLine: boolean; { true => do not store one new line }
Begin
     SkipNewLine := false;
     ShiftNotes;
     start:

     { if range already set }
     if range then begin                             { '..' }
        sy := RangeSy;
        range := false;
        SymLoc := Inp.Loc;
        goto stop;
     end;

     again:
     StoreNotes := (Cond = nil) or Cond.CondInp;

     if AsmSym then
        while (InpCh <= ' ') and (InpCh <> lf) do GetCh
     else
        while InpCh <= ' ' do begin
           if InpCh = lf then begin
              if not SkipNewLine then StoreNewLine;
              SkipNewLine := false;
           end;
           GetCh;
        end;

     SymLoc := Inp.Loc;

     if InpCh = '(' then begin
        GetCh;  { skip '(' }
        if InpCh = '.' then begin
           GetCh;                                     { '(.' }
           sy := LBrackSy;
        end
        else if InpCh <> '*' then begin
           sy := LParSy;                              { '(' }
        end
        else begin
           GetCh; { skip '*' }                        { comment }

           dir := (InpCh = '$');
           if dir then InitDirective
                  else InitComment (false);

           old := InpCh;
           GetCh;

           while (old <> '*') or (InpCh <> ')') do begin
              if dir then StoreDirectiveCharacter (old)
                     else StoreCommentCharacter (old);
              old := InpCh;
              GetCh;
           end;
           GetCh; { skip ')' }

           if dir then begin
              CompilerDirective;
              SkipNewLine := true;
           end
           else FinishComment;

           if AsmSym then sy := EolSy
                     else goto again;
        end;
     end

     else if InpCh = '{' then begin                   { comment }
        GetCh;
        dir := (InpCh = '$');
        if dir then InitDirective
               else InitComment (false);

        while InpCh <> '}' do begin
           if dir then StoreDirectiveCharacter (InpCh)
                  else StoreCommentCharacter (InpCh);
           GetCh;
        end;
        GetCh;

        if dir then begin
           CompilerDirective;
           SkipNewLIne := true;
        end
        else FinishComment;

        if AsmSym then sy := EolSy
                  else goto again;
     end

     else if InpCh = '/' then begin
        GetCh;
        if InpCh <> '/' then begin                   { / }
           sy := SlashSy;
        end
        else begin
           GetCh; { skip / }
           InitComment (true);

           while InpCh <> lf do begin                 { comment }
              StoreCommentCharacter (InpCh);
              GetCh;
           end;

           FinishComment;
           GetCh; { skip lf }
           StoreNewLine;

           if AsmSym then sy := EolSy
                     else goto again;
        end;
     end

     else if InpCh in letter then GetIdent            { IDENTIFIER }
     else if InpCh in digit then GetNumber            { NUMBER }
     else if InpCh = '$' then GetHexNumber            { HEXADECIMAL NUMBER }
     else if InpCh in [quote, '#'] then GetString     { STRING }

     else if AsmSym and (InpCh in AsmLetter) then GetIdent { napr. @@4a }
     else if AsmSym and (InpCh = lf)  then begin           { end of line }
        GetCh;
        sy := EolSy;
     end

     else begin                                       { SPECIAL SYMBOLS }
        old := InpCh;
        GetCh;
        case old of
           '@': sy := AtSignSy;
           '&': sy := AndSignSy; { assembler }
           '+': sy := PlusSy;
           '-': sy := MinusSy;
           '*': sy := AsteriskSy;
           '/': sy := SlashSy;
           ',': sy := CommaSy;
           ';': sy := SemicolonSy;
           '[': sy := LBrackSy;
           ')': sy := RParSy;
           ']': sy := RBrackSy;
           '^': sy := ArrowSy;
           '=': sy := EqualSy;

           '.': select3 (PeriodSy,  '.', RangeSy, ')', RBrackSy);
           ':': select2 (ColonSy,   '=', AssignSy);
           '(': select2 (LParSy,    '.', LBrackSy);
           '>': select2 (GreaterSy, '=', GreaterEqualSy);
           '<': select3 (LessSy,    '=', LessEqualSy, '>', UnequalSy);

           else Error ('Unknown symbol');
        end;
     end;

     stop:
     if (Cond <> nil) and not Cond.CondInp then goto start;
End;

{--------------------------------------------------------------------------}

Function ReadUntil (stop: char): string;
Const max = 255;
Var   len: integer;
      buf: string [255];
Begin
     while (InpCh <= ' ') and (InpCh <> lf) do
        GetCh;

     len := 0;
     while InpCh <> stop do begin
        if InpCh = lf then Error ('"' + stop + '" expected');
        inc (len);
        if len > max then Error ('Line too long');
        buf [len] := InpCh;
        GetCh;
     end;
     SetLength (buf, len);
     result := buf;
End;

{--------------------------------------------------------------------------}

Function ConvIdent (id: TIdent): TIdent;
Begin
     if CompareUpperCase then result := UpperCase (id)
                         else result := id;
End;

(*************************** CONTROL CHARACTERS ***************************)

Procedure ConvControlCharacters;
Var  n: integer;
Begin
     if sy = ArrowSy then begin
        n := ord (InpCh) - 64;
        if (n >= 0) and (n <= 31) then begin
           GetCh;
           if InpCh in [quote, '#', '^'] then begin
              GetSymbol;
              if length (StringVal) = StringMax then
                 Error ('String too long');
              StringVal := chr (n) + StringVal;
           end
           else begin
              sy := StrSy;
              StringVal := chr (n);
           end;
        end;
     end;
End;

(******************************* DIRECTIVES *******************************)

Const DirMax = 38;

Const DirTab: array [1..DirMax] of KeyRec =
      (( t:'ABSOLUTE'         ; s:AbsoluteSy         ),
       ( t:'ABSTRACT'         ; s:AbstractSy         ),
       ( t:'ASSEMBLER'        ; s:AssemblerSy        ),
       ( t:'AT'               ; s:AtSy               ),
       ( t:'AUTOMATED'        ; s:AutomatedSy        ),
       ( t:'CDECL'            ; s:CdeclSy            ),
       ( t:'DEFAULT'          ; s:DefaultSy          ),
       ( t:'DISPID'           ; s:DispidSy           ),
       ( t:'DYNAMIC'          ; s:DynamicSy          ),
       ( t:'EXPORT'           ; s:ExportSy           ),
       ( t:'EXTERNAL'         ; s:ExternalSy         ),
       ( t:'FAR'              ; s:FarSy              ),
       ( t:'FORWARD'          ; s:ForwardSy          ),
       ( t:'FRIEND'           ; s:FriendSy           ),
       ( t:'IMPLEMENTS'       ; s:ImplementsSy       ),
       ( t:'INDEX'            ; s:IndexSy            ),
       ( t:'MESSAGE'          ; s:MessageSy          ),
       ( t:'NAME'             ; s:NameSy             ),
       ( t:'NEAR'             ; s:NearSy             ),
       ( t:'NODEFAULT'        ; s:NodefaultSy        ),
       ( t:'OVERLOAD'         ; s:OverloadSy         ),
       ( t:'OVERRIDE'         ; s:OverrideSy         ),
       ( t:'PASCAL'           ; s:PascalSy           ),
       ( t:'PRIVATE'          ; s:PrivateSy          ),
       ( t:'PROTECTED'        ; s:ProtectedSy        ),
       ( t:'PUBLIC'           ; s:PublicSy           ),
       ( t:'PUBLISHED'        ; s:PublishedSy        ),
       ( t:'READ'             ; s:ReadSy             ),
       ( t:'READONLY'         ; s:ReadonlySy         ),
       ( t:'REGISTER'         ; s:RegisterSy         ),
       ( t:'REINTRODUCE'      ; s:ReintroduceSy      ),
       ( t:'RESIDENT'         ; s:ResidentSy         ),
       ( t:'SAFECALL'         ; s:SafecallSy         ),
       ( t:'STDCALL'          ; s:StdcallSy          ),
       ( t:'STORED'           ; s:StoredSy           ),
       ( t:'VIRTUAL'          ; s:VirtualSy          ),
       ( t:'WRITE'            ; s:WriteSy            ),
       ( t:'WRITEONLY'        ; s:WriteonlySy        ));

Function FindDirective: TSymbol;
Var  a, b, c: integer;
     cmp: integer;
     tmp: string;
Begin
     tmp := IdentVal;
     if CompareUpperCase then tmp := UpperCase (tmp);

     a := 1;
     b := DirMax;
     FindDirective := IdentSy;

     while a<=b do begin
        c := (a+b) shr 1; { a <= c < b }
        cmp := CompareStr (tmp, DirTab[c].t);
        if cmp < 0 then b := c-1
        else if cmp > 0 then a := c+1
        else begin FindDirective := DirTab[c].s; a:=b+1; end;
     end;
End;

Procedure ConvDirective;
Begin
     if sy = IdentSy then
        sy := FindDirective;
End;

Procedure ConvClassDirective;
Var  tmp: TSymbol;
Begin
     if sy = IdentSy then begin
        tmp := FindDirective;
        if tmp in [AutomatedSy, PrivateSy,
                   ProtectedSy, PublicSy, PublishedSy,
                   FriendSy]
           then sy := tmp;
     end;
End;

Procedure RemoveDirective;
Begin
     if (sy >= FirstDirective) and (sy <= LastDirective) then
        sy := IdentSy;
End;

(************************** CHECK CURRENT SYMBOL **************************)

Const SpecMax = 23;

Type  SpecStr = string [2];
      SpecRec = record t: SpecStr; s: TSymbol; end;

Const SpecTab: array [1..SpecMax] of SpecRec =
      (( t: '@' ; s: AtSignSy       ),
       ( t: '+' ; s: PlusSy         ),
       ( t: '-' ; s: MinusSy        ),
       ( t: '*' ; s: AsteriskSy     ),
       ( t: '/' ; s: SlashSy        ),
       ( t: '.' ; s: PeriodSy       ),
       ( t: ',' ; s: CommaSy        ),
       ( t: ':' ; s: ColonSy        ),
       ( t: ';' ; s: SemicolonSy    ),
       ( t: '=' ; s: EqualSy        ),
       ( t: '<' ; s: LessSy         ),
       ( t: '>' ; s: GreaterSy      ),
       ( t: '<>'; s: UnequalSy      ),
       ( t: '<='; s: LessEqualSy    ),
       ( t: '>='; s: GreaterEqualSy ),
       ( t: '^' ; s: ArrowSy        ),
       ( t: '..'; s: RangeSy        ),
       ( t: ':='; s: AssignSy       ),
       ( t: '(' ; s: LParSy         ),
       ( t: ')' ; s: RParSy         ),
       ( t: '[' ; s: lBrackSy       ),
       ( t: ']' ; s: RBrackSy       ),
       ( t: '&' ; s: AndSignSy      )); { assembler }

Procedure MissingSymbol (par: TSymbol);
Var  i:   integer;
     msg: string;
Begin
     { vyhledej textovou reprezentaci ocekavaneho symbolu }
     msg := '';

     for i := 1 to KeyMax do
        if KeyTab[i].s = par then msg := KeyTab[i].t;

     for i := 1 to DirMax do
        if DirTab[i].s = par then msg := DirTab[i].t;

     for i := 1 to AsmMax do
        if AsmTab[i].s = par then msg := AsmTab[i].t;

     for i := 1 to SpecMax do
        if SpecTab[i].s = par then msg := '"' + SpecTab[i].t + '"';

     if par = EolSy then
        msg := 'End of line';

     Error (msg + ' expected');
End;

Procedure VerifySymbol (par: TSymbol);
Begin
     { ohlaseni chyby pokud sy <> par }
     if sy <> par then MissingSymbol (par);
End;

Procedure CheckSymbol (par: TSymbol);
Begin
     if sy <> par then MissingSymbol (par);
     GetSymbol; { skip symbol }
End;

(**************************** SYMBOL TO STRING ****************************)

Function SymbolToString: string;
{ Prevod symbolu na retezec znaku - pouze pro ladeni }
Begin
     {$IFDEF FPC}
        result := 'TSymbol (' + IntToStr (ord (sy)) + ')';
     {$ELSE}
        result := TypInfo.GetEnumName (typeinfo (TSymbol), ord (sy));
     {$ENDIF}

     case sy of
        IdentSy:   result := result + ' (' + IdentVal  + ')';
        NumberSy:  result := result + ' (' + NumberVal + ')';
        FloatSy:   result := result + ' (' + NumberVal + ')';
        StrSy:     result := result + ' (' + StringVal + ')';
     end;
End;

(****************************** CHECK TABLES ******************************)

Procedure CheckTables;
Var  i: integer;
     tmp: set of TSymbol;

     procedure check (s: TSymbol);
     begin
          Assert (not (s in tmp));
          Include (tmp, s);
     end;

Begin
     { kontrola usporadani tabulek }
     for i := 1 to KeyMax-1 do
        Assert (KeyTab[i].t < KeyTab[i+1].t);

     for i := 1 to AsmMax-1 do
        Assert (AsmTab[i].t < AsmTab[i+1].t);

     for i := 1 to DirMax-1 do
        Assert (DirTab[i].t < DirTab[i+1].t);

     { kontrola uplnosti tabulek }
     tmp := [];
     for i := 1 to KeyMax  do check (KeyTab[i].s);
     for i := 1 to AsmMax  do check (AsmTab[i].s);
     for i := 1 to DirMax  do check (DirTab[i].s);
     for i := 1 to SpecMax do check (SpecTab[i].s);
     check (EolSy);
     check (IdentSy);
     check (NumberSy);
     check (FloatSy);
     check (StrSy);
     Assert (tmp = [low (TSymbol) .. high (TSymbol)], 'Invalid tables');
End;

(********************************* CLEAR **********************************)

Procedure ClearLex;
{ Start new project }
Begin
     sy := EolSy;      { not necessary - StartLex  }
     range := false;   { not necessary - StartLex  }
     AsmSym := false;  { not necessary - StartLex  }

     IdentVal := '';   { not necessary }
     NumberVal := '';  { not necessary }
     StringVal := '';  { not necessary }

     num_len := 0;     { not necessary }
     number_test := 0; { not necessary }
     float_test := 0;  { not necessary }
     str_len := 0;     { not necessary }

     InpNote  := nil;
     InpNotes := TNoteList.Create;
     LateNotes := TNoteList.Create;
End;

Procedure StartLex;
{ Start new unit }
Begin
     sy := EolSy;     { important }
     range := false;  { important }
     AsmSym := false; { important }

     IdentVal := '';  { not necessary }
     NumberVal := ''; { not necessary }
     StringVal := ''; { not necessary }

     InpNote  := nil;
     InpNotes := TNoteList.Create;
     LateNotes := TNoteList.Create;
End;

BEGIN
     CheckTables;
END.

