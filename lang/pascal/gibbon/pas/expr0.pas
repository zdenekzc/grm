
(**************************************************************************)
(*                                                                        *)
(*                              Expressions                               *)
(*                                                                        *)
(**************************************************************************)

UNIT Expr0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF};

Const ExprSet = [IdentSy, NumSy, FltSy, StrSy, StringSy,
                 NotSy, NilSy, PlusSy, MinusSy, AtSignSy, InheritedSy,
                 LParSy, LBrackSy];

Procedure IdentChk (E: TExpr); { check if E is identifier }
Procedure QualIdentChk (E: TExpr); { check if E is qualified identifier }

Function ExtractIdentFromExpr (E: TExpr): TIdent; { expression to identifier }
Function ExprToAlias (E: TExpr): TAliasType; { expression to alias-type }

Function Identifier: TIdent;     { identifier }
Function QualIdent:  TQualIdent; { qualified identifier }

Function Expression: TExpr; { expression }
Function SimpleExpr: TExpr; { simple expression }

Function Variable:    TExpr; { variable }
Function StructConst: TExpr; { structured constant }

IMPLEMENTATION

(********************************** NEW ***********************************)

Function NewBinaryExpr (loc: TLocation; kind: TBinaryKind; L, R: TExpr): TBinaryExpr;
Begin
     result := TBinaryExpr.Create;
     result.loc := loc;
     result.kind := kind;
     result.left := L;
     result.right := R;
End;

Function NewUnaryExpr (loc: TLocation; kind: TUnaryKind; P: TExpr): TUnaryExpr;
Begin
     result := TUnaryExpr.Create;
     result.loc := loc;
     result.kind := kind;
     result.param := P;
End;

Function NewValueExpr (loc: TLocation; kind: TValueKind; txt: string): TValueExpr;
Begin
     result := TValueExpr.Create;
     result.loc := loc;
     result.kind := kind;
     result.value := txt;
End;

Function NewIdentExpr (loc: TLocation; id: string): TIdentExpr;
Begin
     result := TIdentExpr.Create;
     result.loc := loc;
     result.ident := id;
End;

Function NewIndexExpr (loc: TLocation; L: TExpr; R: TInxSect): TIndexExpr;
Begin
     result := TIndexExpr.Create;
     result.loc := loc;
     result.left := L;
     result.list := R;
End;

Function NewCallExpr (loc: TLocation; L: TExpr; R: TArgSect): TCallExpr;
Begin
     result := TCallExpr.Create;
     result.loc := loc;
     result.func := L;
     result.list := R;
End;

Function NewSetExpr (loc: TLocation; L: TElemSect): TSetExpr;
Begin
     result := TSetExpr.Create;
     result.loc := loc;
     result.list := L;
End;

Function NewStructExpr (loc: TLocation; L: TStructSect): TStructExpr;
Begin
     result := TStructExpr.Create;
     result.loc := loc;
     result.list := L;
End;

Function NewNilExpr (loc: TLocation): TNilExpr;
Begin
     result := TNilExpr.Create;
     result.loc := loc;
End;

Function NewStringExpr (loc: TLocation; P: TExpr): TStringExpr;
Begin
     { je mozne P = nil }
     result := TStringExpr.Create;
     result.loc := loc;
     result.param := P;
End;

Function NewSuperExpr (loc: TLocation; id: string): TSuperExpr;
Begin
     { je mozne id = '' }
     result := TSuperExpr.Create;
     result.loc := loc;
     result.ident := id;
End;

(********************************* CHECK **********************************)

Procedure IdentChk (E: TExpr);
Begin
     if E.tag <> IdentExp then
        Error ('Identifier required');
End;

Procedure QualIdentChk (E: TExpr);
Var  B: TBinaryExpr;
Begin
     if (E.tag <> IdentExp) and (E.tag <> BinaryExp) then
        Error ('Qualified identifier required');

     if E.tag = BinaryExp then begin
        B := E as TBinaryExpr;

        if B.kind <> FieldExp then
           Error ('Qualified identifier required');

        QualIdentChk (B.left);
     end;
End;

(****************************** CONVERSIONS *******************************)

Function ExtractIdentFromExpr (E: TExpr): TIdent;
Begin
     IdentChk (E);
     result := (E as TIdentExpr).ident;
     { !? - vymazani vyrazu }
End;

Function ExprToAlias (E: TExpr): TAliasType;
Begin
     result := TAliasType.Create;
     QualIdentChk (E);
     result.qual_ident := E;
End;

(****************************** IDENTIFIERS *******************************)

Function Identifier: TIdent;
Begin
     if sy <> IdentSy then
        Error ('Identifier expected');
     result := IdentVal;
     GetSymbol;
End;

Function IdentExpr: TIdentExpr;
Var  loc: TLocation;
     id:  TIdent;
Begin
     loc := SymLoc;
     id := Identifier ();
     result := NewIdentExpr (loc, id);
End;

Function QualIdent: TQualIdent;
Begin
     result := Expression ();
     QualIdentChk (result);
End;

(******************************* ARGUMENTS ********************************)

Procedure Argument (sect: TArgSect);
Var  item: TArgItem;
Begin
     item := TArgItem.Create;
     item.value := Expression ();

     if sy = ColonSy then begin
        GetSymbol;
        item.width := Expression ();

        if sy = ColonSy then begin
           GetSymbol;
           item.digits := Expression ();
        end;
     end;

     sect.Add (item);
End;

Function Arguments: TArgSect;
Begin
     result := TArgSect.Create;

     if sy <> RParSy then begin
        Argument (result);

        while sy = CommaSy do begin
           GetSymbol;
           Argument (result);
        end;
     end;
End;

(**************************** SET CONSTRUCTOR *****************************)

Procedure SetElem (sect: TElemSect);
Var  item: TElemItem;
Begin
     item := TElemItem.Create;
     item.low := Expression ();

     if sy = RangeSy then begin
        GetSymbol;
        item.high := Expression ();
     end;

     sect.Add (item);
End;

Function SetExpr: TSetExpr;
Var  loc: TLocation;
     sect: TElemSect;
Begin
     loc := SymLoc;
     CheckSymbol (LBrackSy);
     sect := TElemSect.Create;

     if sy <> RBrackSy then begin
        SetElem (sect);
        while sy = CommaSy do begin
           GetSymbol;
           SetElem (sect);
        end;
     end;

     CheckSymbol (RBrackSy);
     result := NewSetExpr (loc, sect);
End;

(************************** STRUCTURED CONSTANTS **************************)

Procedure StructItem (sect: TStructSect);
Const InvStruct = 'Invalid structured constant';
Var   E: TExpr;
      item: TStructItem;
Begin
     item := TStructItem.Create;
     E := Expression ();

     if sy = ColonSy then begin
        sect.rec := true;
        if sect.arr then Error (InvStruct);

        item.name := ExtractIdentFromExpr (E);
        GetSymbol ();

        item.value := Expression ();
     end
     else begin
        sect.arr := true;
        if sect.rec then Error (InvStruct);

        item.value := E;
     end;

     sect.Add (item);
End;

Function StructSect: TExpr;
Var  loc: TLocation;
     sect: TStructSect;
Begin
     loc := SymLoc;
     CheckSymbol (LParSy);
     sect := TStructSect.Create;

     if sy <> RParSy then begin
        StructItem (sect);

        if sect.rec then
           while sy = SemicolonSy do begin
              GetSymbol ();
              StructItem (sect);
           end
        else
           while sy = CommaSy do begin
              GetSymbol ();
              StructItem (sect);
           end;
     end;

     CheckSymbol (RParSy);
     result := NewStructExpr (loc, sect);
End;

(******************************* REFERENCE ********************************)

Function Reference (E: TExpr): TExpr;
Var loc: TLocation;
    S:   TInxSect;
    I:   TInxItem;
    A:   TArgSect;
    id:  TIdent;
    N:   TExpr;
Begin
     while sy in [LBrackSy, PeriodSy, ArrowSy, LParSy] do begin

        if sy = LBrackSy then begin            { ARRAY INDEX }
           loc := SymLoc;
           GetSymbol;

           S := TInxSect.Create;

           I := TInxItem.Create;
           I.value := Expression ();
           S.Add (I);

           while sy = CommaSy do begin
              GetSymbol;

              I := TInxItem.Create;
              I.value := Expression ();
              S.Add (I);
           end;

           E := NewIndexExpr (loc, E, S);
           CheckSymbol (RBrackSy);
        end

        else if sy = PeriodSy then begin       { RECORD FIELD }
           loc := SymLoc;
           GetSymbol;
           N := IdentExpr ();
           E := NewBinaryExpr (loc, FieldExp, E, N);
        end

        else if sy = ArrowSy then begin        { POINTER ACCESS }
           loc := SymLoc;
           GetSymbol;
           E := NewUnaryExpr (loc, DerefExp, E);
        end

        else if sy = LParSy then begin         { FUNCTION CALL }
           loc := SymLoc;
           GetSymbol;
           A := Arguments ();
           CheckSymbol (RParSy);
           E := NewCallExpr (loc, E, A);
        end;
     end;

     result := E;
End;

(********************************* FACTOR *********************************)

Function Factor: TExpr;
Var  E, P: TExpr;
     id: TIdent;
     loc: TLocation;
Begin
     ConvControlCharacters;

     { variable reference / function call / value typecast / constant ident }
     if sy = IdentSy then begin
        E := NewIdentExpr (SymLoc, IdentVal);
        GetSymbol;
        E := Reference (E);
     end

     { unsigned number }
     else if sy = NumSy then begin
        E := NewValueExpr (SymLoc, IntValueExp, NumberVal);
        GetSymbol;
     end

     { real number }
     else if sy = FltSy then begin
        E := NewValueExpr (SymLoc, FltValueExp, NumberVal);
        GetSymbol;
     end

     { character string }
     else if sy = StrSy then begin
        E := NewValueExpr (SymLoc, StrValueExp, StringVal);
        GetSymbol;
     end

     { nil }
     else if sy = NilSy then begin
        loc := SymLoc;
        GetSymbol;
        E := NewNilExpr (loc);
     end

     { (expression) }
     else if sy = LParSy then begin
        E := StructSect (); { expression or structured constant }
        E := Reference (E);
     end

     { not factor }
     else if sy = NotSy then begin
        loc := SymLoc;
        GetSymbol;
        P := Factor ();
        E := NewUnaryExpr (loc, NotExp, P);
     end

     { + factor }
     else if sy = PlusSy then begin
        loc := SymLoc;
        GetSymbol;
        P := Factor ();
        E := NewUnaryExpr (loc, PlusExp, P);
     end

     { - factor }
     else if sy = MinusSy then begin
        loc := SymLoc;
        GetSymbol;
        P := Factor ();
        E := NewUnaryExpr (loc, MinusExp, P);
     end

     { set constructor }
     else if sy = LBrackSy then begin
        E := SetExpr ();
     end

     { adress factor }
     else if sy = AtSignSy then begin
        loc := SymLoc;
        GetSymbol;
        P := Factor ();
        E := NewUnaryExpr (loc, AdrExp, P);
     end

     { inherited }
     else if sy = InheritedSy then begin
        loc := SymLoc;
        GetSymbol;

        id := '';
        if sy = IdentSy then begin
           id := IdentVal;
           GetSymbol;
        end;

        E := NewSuperExpr (loc, id);
        E := Reference (E);
     end

     { string typecast / string type }
     else if sy = StringSy then begin
        loc := SymLoc;
        GetSymbol; { skip reserved word string }

        if sy = LParSy then begin
           CheckSymbol (LParSy);
           P := Expression ();
           CheckSymbol (RParSy);
           E := NewStringExpr (loc, P);
        end
        else begin
           E := NewStringExpr (loc, nil);
        end;
     end

     else begin
        Error ('Expression syntax');
        E := nil; { compiler }
     end;

     result := E;
End;

(********************************** TERM **********************************)

Function Term: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := Factor;

     while sy in [AsteriskSy, SlashSy, DivSy, ModSy,
                  AndSy, ShlSy, ShrSy, AsSy] do begin

        case sy of
           AsteriskSy: kind := MulExp;
           SlashSy:    kind := RDivExp;
           DivSy:      kind := DivExp;
           ModSy:      kind := ModExp;
           AndSy:      kind := AndExp;
           ShlSy:      kind := ShlExp;
           ShrSy:      kind := ShrExp;
           AsSy:       kind := AsExp;
           else        Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := Factor ();
        E := NewBinaryExpr (loc, kind, E, R);
     end;

     result := E;
End;

(*************************** SIMPLE EXPRESSION ****************************)

Function SimpleExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := Term;

     while sy in [PlusSy, MinusSy, OrSy, XorSy] do begin

        case sy of
           PlusSy:  kind := AddExp;
           MinusSy: kind := SubExp;
           OrSy:    kind := OrExp;
           XorSy:   kind := XorExp;
           else     Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := Term ();
        E := NewBinaryExpr (loc, kind, E, R);
    end;

     result := E;
End;

(******************************* EXPRESSION *******************************)

Function Expression: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := SimpleExpr ();

     if sy in [LessSy, GreaterSy, LessEqualSy, GreaterEqualSy,
               UnEqualSy, EqualSy, InSy, IsSy] then begin

        case sy of
           LessSy:         kind := LtExp;
           GreaterSy:      kind := GtExp;
           LessEqualSy:    kind := LeExp;
           GreaterEqualSy: kind := GeExp;
           UnEqualSy:      kind := NeExp;
           EqualSy:        kind := EqExp;
           InSy:           kind := InExp;
           IsSy:           kind := IsExp;
           else            Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := SimpleExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     end;

     result := E;
End;

(******************************* VARIABLES ********************************)

Function Variable: TExpr;
Begin
     result := Expression ();
     // !? CheckVariable (result);
End;

(************************** STRUCTURED CONSTANTS **************************)

Function StructConst: TExpr;
Begin
     result := Expression ();
End;

END.

