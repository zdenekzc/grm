
(**************************************************************************)
(*                                                                        *)
(*                           Compiler Directives                          *)
(*                                                                        *)
(**************************************************************************)

UNIT Dir0;

INTERFACE

Uses Fil0;

{---------------------------- Defined Symbols -----------------------------}

Type TDefine = class (TAlloc)
        name:   string;  { symbol }
        value:  boolean; { definovan / nedefinovan }

        left:   TDefine; { levy podstrom }
        right:  TDefine; { pravy podstrom }
     end;

Var  Def: TDefine; { strom symbolu definovanych v soucasnem modulu }

{------------------------ Conditional Compilation -------------------------}

Type TCond = class (TAlloc)
        CondInp:  boolean; { true => cte se vstup }
        CondElse: boolean; { true => else vetev }
        next:     TCond;
     end;

Var  Cond: TCond; { posledni vnoreny prikaz ifdef }

{-------------------------- Compiler Directives ---------------------------}

Procedure InitDirective;
Procedure StoreDirectiveCharacter (par: char);

Procedure PascalDirective;
Procedure CppDirective;

{--------------------------------------------------------------------------}

Procedure StartDir (p_defines: string);

IMPLEMENTATION

(******************** STORE / READ COMPILER DIRECTIVES ********************)

Const DirSize = 255;            { max. delka direktivy }

Var   DirLen: integer;          { pocet znamku v poli DirVal }
      DirVal: string [DirSize]; { text direktivy }

      DirPos: integer;          { pozice prave cteneho znaku }
      DirCh:  char;             { prave cteny znak }

      DirUpc: boolean;          { prevadet na velka pismena }

(**************************** DEFINED SYMBOLS *****************************)

Procedure EnterDef (var root: TDefine; const p_name: string; p_value: boolean);
{ Vlozeni identifikatoru do stromu
  pokud identifikator je jiz ve stromu, je prepsana jeho hodnota }
Var  ptr:  ^TDefine;
     done: boolean;
Begin
     ptr := addr (root);
     done := false;

     while not done do
        if ptr^=nil then begin
           done := true;
           ptr^ := TDefine.Create;
           with ptr^ do begin
              name  := p_name;
              value := p_value;
              left  := nil;
              right := nil;
           end;
        end
        else if p_name < ptr^.name then ptr := addr (ptr^.left)
        else if p_name > ptr^.name then ptr := addr (ptr^.right)
        else begin
           ptr^.value := p_value;
           done := true;
        end;
End;

Function FindDef (root: TDefine; const id: string): boolean;
{ Hledej identifikator ve stromu, vrat jeho hodnotu
  Neni-li nalezen, vrat false }
Var  done: boolean;
     p: TDefine;

Begin
     done := false;
     p := root;
     result := false;

     while not done do
        if p=nil then begin
           result := false;
           done := true;
        end
        else begin
           if id < p.name then p := p.left
           else if id > p.name then p := p.right
           else begin
              result := p.value;
              done := true;
           end;
        end;
End;

Procedure DefineDirective (const txt: string; val: boolean);
Begin
     EnterDef (Def, txt, val);
End;

Procedure InitDefines (txt: string);
{ Definice symbolu zadanych v textovem retezci }
Var  i, k, len: integer;
     name: string;
Begin
     Def := nil;

     i := 1;
     len := length (txt);

     while i <= len do begin
        { preskoc oddelovace }
        while (i <= len) and not (txt[i] in lod) do inc (i);

        k := i;
        while (k <= len) and (txt[k] in lod) do inc (k);
        name := copy (txt, i, k-i);

        EnterDef (Def, name, true);
        i := k;
     end;
End;

(************************ CONDITIONAL COMPILATION *************************)

Procedure CondAdd;
{ Zacatek podmineneho prekladu }
Var  tmp: TCond;
Begin
     tmp := TCond.Create; { create new input record }
     tmp.next := Cond;    { link old input record }
     Cond := tmp;         { set new input record }
End;

Procedure CondRemove;
{ Konec podmineneho prekladu }
Var  tmp: TCond;
Begin
     Assert (Cond <> nil, 'no opent input record');

     { set current input record }
     tmp := Cond;
     Cond := Cond.next;

     { delete old input record }
     tmp.Free;
End;

{--------------------------------------------------------------------------}

Procedure IfDirective (val: boolean);
Var  tmp: TCond;
Begin
     CondAdd;

     tmp := Cond.next;
     if (tmp <> nil) and not tmp.CondInp then val := false;

     Cond.CondInp := val;
     Cond.CondElse := false;
End;

Procedure IfdefDirective (txt: string; flag: boolean);
Var  val: boolean;
Begin
     val := FindDef (Def, txt);
     IfDirective (val = flag);
End;

Procedure ElseDirective;
Var  val: boolean;
     tmp: TCond;
Begin
     if (Cond = nil) or Cond.CondElse then
        Error ('Misplaced else directive');
     Cond.CondElse := true;

     val := not Cond.CondInp;
     tmp := Cond.next;
     if (tmp <> nil) and not tmp.CondInp then val := false;
     Cond.CondInp := val;
End;

Procedure EndifDirective;
Begin
     if Cond = nil then Error ('Misplaced endif directive');
     CondRemove;
End;

(************************ STORE COMPILER DIRECTIVE ************************)

Procedure InitDirective;
{ Priprava pred ukladanim directivy }
Begin
     DirLen := 0;
End;

Procedure StoreDirectiveCharacter (par: char);
{ Uloz jeden znak directivy }
Begin
     if DirLen >= DirSize then begin
        if par > ' ' then Error ('Compiler directive too long');
     end
     else begin
       inc (DirLen);
       DirVal [DirLen] := par;
     end;
End;

(************************ READ COMPILER DIRECTIVE *************************)

Procedure ReadCh;
{ Precti jeden ulozeny znak direktivy }
Begin
     if DirPos > DirLen then
        Error ('Unexpected end of compiler directive')
     else if DirPos = DirLen then begin
        inc (DirPos);
        DirCh := ' ';
     end
     else begin
        inc (DirPos);
        DirCh := DirVal [DirPos];
     end
End;

Procedure ReadInit;
{ Inicializace pred ctenim }
Begin
     DirVal[0] := chr (DirLen);
     DirPos := 0;
     ReadCh;
     DirUpc := false;
End;

{--------------------------------------------------------------------------}

Function ReadToken: string;
{ Precti identifikator - mezery na zacatku nejsou povoleny }
Var  txt: string [DirSize];
Begin
     txt := '';
     if not (DirCh in lod) then Error ('identifier expected');
     while DirCh in lod do begin
        if DirUpc then DirCh := UpCase (DirCh);
        txt := txt + DirCh;
        ReadCh;
     end;
     result := txt;
End;

Function ReadName: string;
{ Preskoc mezery a precti identifikator }
Begin
     while DirCh <= ' ' do ReadCh;
     result := ReadToken;
End;

Function ReadFileName: string;
{ Preskoc mezery a precti jmeno souboru }
Var  txt: string [DirSize];
Begin
     while DirCh <= ' ' do ReadCh;
     txt := '';
     while DirCh > ' ' do begin
        txt := txt + DirCh;
        ReadCh;
     end;
     result := txt;
End;

Function ReadText: string;
{ Preskoc mezery a precti retezec znaku }
Var  txt: string [DirSize];
Begin
     while DirCh <= ' ' do ReadCh;

     if DirCh <> quote1 then Error ('String expected');
     ReadCh; {skip quote }

     txt := '';
     repeat
        while DirCh <> quote1 do begin
           txt := txt + DirCh;
           ReadCh;
        end;
        ReadCh; {skip quote }
        if DirCh = quote1 then txt := txt + quote1;
     until DirCh <> quote1;

     result := txt;
End;

(************************** COMPILER DIRECTIVES ***************************)

Procedure IncludeDirective (fname: string);
Begin
     OpenIncl (fname);
End;

{--------------------------------------------------------------------------}

Procedure PascalDirective;
Var  dir:  string;
Begin
     ReadInit;
     DirUpc := true; { upper case }

     ReadCh; { skip '$' }
     dir := ReadToken;

          if dir = 'IFDEF'    then IfdefDirective (ReadName, true)
     else if dir = 'IFNDEF'   then IfdefDirective (ReadName, false)
     else if dir = 'ELSE'     then ElseDirective
     else if dir = 'ENDIF'    then EndifDirective
     else if dir = 'IFOPT'    then IfDirective (false) { !! unsupported directive }

     else if (Cond = nil) or Cond.CondInp then begin
        if dir = 'DEFINE'     then DefineDirective (ReadName, true)
        else if dir = 'UNDEF' then DefineDirective (ReadName, false)
        else if (dir = 'I') or (dir = 'INCLUDE') then
           IncludeDirective (ReadFileName)
     end;
End;

{--------------------------------------------------------------------------}

Procedure CppIncludeDirective;
Var  stop: char;
     fname: string [DirSize];
Begin
     while DirCh <= ' ' do ReadCh;

     if InpCh = quote2 then stop := quote2
     else if InpCh = '<' then stop := '>'
     else Error ('Invalid include directive');

     ReadCh; { skip " or < }

     fname := '';
     while DirCh <> stop do begin
        fname := fname + DirCh;
        ReadCh;
     end;

     ReadCh; { skip " or > }

     OpenIncl (fname);
End;

Procedure CppDirective;
Var  dir:  string;
Begin
     ReadInit;
     DirUpc := false;

     dir := ReadName;

          if dir = 'ifdef'    then IfdefDirective (ReadName, true)
     else if dir = 'ifndef'   then IfdefDirective (ReadName, false)
     else if dir = 'else'     then ElseDirective
     else if dir = 'endif'    then EndifDirective

     else if (Cond = nil) or Cond.CondInp then begin
             if dir = 'define'  then DefineDirective (ReadName, true)  { !? }
        else if dir = 'undef'   then DefineDirective (ReadName, false) { !? }
        else if dir = 'include' then CppIncludeDirective;
     end;
End;

(********************************* CLEAR **********************************)

Procedure StartDir (p_defines: string);
{ new unit }
Begin
     Def    := nil; { not necessary - InitDefines }
     Cond   := nil; { important }

     DirLen := 0;   { not necessary }
     DirVal := '';  { not necessary }
     DirPos := 0;   { not necessary }
     DirCh  := ' '; { not necessary }

     InitDefines (p_defines); { important }
End;

END.

