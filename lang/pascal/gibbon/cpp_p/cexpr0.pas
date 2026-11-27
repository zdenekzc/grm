
(**************************************************************************)
(*                                                                        *)
(*                              Expressions                               *)
(*                                                                        *)
(**************************************************************************)

UNIT CExpr0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF};

Function Identifier: TIdent;
Function QualifiedName: TExpr;

Function Expression: TExpr; { expression }

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

Function NewThisExpr (loc: TLocation): TThisExpr;
Begin
     result := TThisExpr.Create;
     result.loc := loc;
End;

Function NewCondExpr (loc: TLocation; E1, E2, E3: TExpr): TCondExpr;
Begin
     result := TCondExpr.Create;
     result.loc := loc;
     result.cond := E1;
     result.true_expr := E2;
     result.false_expr := E3;
End;

(******************************* IDENTIFIER *******************************)

Function Identifier: TIdent;
Begin
     if sy <> IdentSy then
        Error ('Identifier expected');
     result := IdentVal;
     GetSymbol;
End;

Function IdentExpr: TIdentExpr;
Begin
     result := NewIdentExpr (SymLoc, Identifier ());
End;

Function QualifiedName: TExpr;
Var  loc: TLocation;
     tmp: TExpr;
Begin
     if sy = TildaSy then begin
        loc := SymLoc;
        GetSymbol;
        result := QualifiedName ();
        result := NewUnaryExpr (loc, DestructorExp, result);
     end
     else begin
        result := IdentExpr ();
        while sy = DColonSy do begin
           loc := SymLoc;
           GetSymbol;
           tmp := IdentExpr ();
           result := NewBinaryExpr (loc, ScopeExp, result, tmp);
        end;
     end;
End;

(******************************* ARGUMENTS ********************************)

Function AssignmentExpr: TExpr; forward;
Function CastExpr: TExpr; forward;

Procedure Argument (sect: TArgSect);
Var  item: TArgItem;
Begin
     item := TArgItem.Create;
     item.value := AssignmentExpr ();
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

(****************************** ARRAY INDEX *******************************)

Function ArrayIndex: TInxSect;
Var  item: TInxItem;
Begin
     result := TInxSect.Create;
     item := TInxItem.Create;
     item.value := Expression ();
     result.Add (item);
End;

(******************************* EXPRESSION *******************************)

Function PrimaryExpr: TExpr;
Var  E:   TExpr;
     loc: TLocation;
Begin
     { unsigned number }
     if sy = NumSy then begin
        E := NewValueExpr (SymLoc, IntValueExp, NumberVal);
        GetSymbol;
     end

     { real number }
     else if sy = FltSy then begin
        E := NewValueExpr (SymLoc, FltValueExp, NumberVal);
        GetSymbol;
     end

     { character }
     else if sy = ChrSy then begin
        E := NewValueExpr (SymLoc, ChrValueExp, CharVal);
        GetSymbol;
     end

     { string }
     else if sy = StrSy then begin
        E := NewValueExpr (SymLoc, StrValueExp, StringVal);
        GetSymbol;
     end

     { this }
     else if sy = ThisSy then begin
        E := NewThisExpr (SymLoc);
        GetSymbol;
     end

     { :: }
     else if sy = DColonSy then begin
        loc := SymLoc;
        GetSymbol;

        E := QualifiedName ();
        E := NewUnaryExpr (loc, GlobalExp, E);
     end

     { (expression) }
     else if sy = LParSy then begin
        loc := SymLoc;
        GetSymbol;

        E := Expression ();
        E := NewUnaryExpr (loc, ParExp, E);

        CheckSymbol (RParSy);
     end

     { identifier }
     else if sy = IdentSy then begin
        E := QualifiedName ();
     end

     else begin
        Error ('Expression syntax');
        E := nil; { compiler }
     end;

     result := E;
End;

{--------------------------------------------------------------------------}

Function PostfixExpr: TExpr;
Var E:   TExpr;
    loc: TLocation;
    S:   TInxSect;
    A:   TArgSect;
    N:   TExpr;
Begin
     E := PrimaryExpr;

     while sy in [LBrackSy, LParSy, PeriodSy,
                  ArrowSy, DPlusSy, DMinusSy] do begin

        if sy = LBrackSy then begin            { ARRAY INDEX }
           loc := SymLoc;
           GetSymbol;

           S := ArrayIndex;
           CheckSymbol (RBrackSy);

           E := NewIndexExpr (loc, E, S);
        end

        else if sy = LParSy then begin         { FUNCTION CALL }
           loc := SymLoc;
           GetSymbol;

           A := Arguments ();
           CheckSymbol (RParSy);

           E := NewCallExpr (loc, E, A);
        end

        else if sy = PeriodSy then begin       { FIELD }
           loc := SymLoc;
           GetSymbol;
           N := QualifiedName ();
           E := NewBinaryExpr (loc, FieldExp, E, N);
        end

        else if sy = ArrowSy then begin        { POINTER FIELD }
           loc := SymLoc;
           GetSymbol;
           N := QualifiedName ();
           E := NewBinaryExpr (loc, PtrFieldExp, E, N);
        end

        else if sy = DPlusSy then begin        { INCREMENT }
           loc := SymLoc;
           GetSymbol;
           E := NewUnaryExpr (loc, PostIncExp, E);
        end

        else if sy = DMinusSy then begin       { DECREMENT }
           loc := SymLoc;
           GetSymbol;
           E := NewUnaryExpr (loc, PostDecExp, E);
        end

        else Bug;
     end;

     result := E;
End;

{--------------------------------------------------------------------------}

Function UnaryExpr: TExpr;
Var  loc: TLocation;
     kind: TUnaryKind;
     E: TExpr;
Begin
     if sy in [DPlusSy, DMinusSy] then begin

        if sy = DPlusSy then kind := PreIncExp
                        else kind := PreDecExp;

        loc := SymLoc;
        GetSymbol;

        E := UnaryExpr ();
        E := NewUnaryExpr (loc, kind, E);
     end

     else if sy in [AsteriskSy, AmpersandSy,
                    PlusSy, MinusSy, LogNotSy, TildaSy] then begin

        case sy of
           AsteriskSy:  kind := DerefExp;
           AmpersandSy: kind := AdrExp;
           PlusSy:      kind := PlusExp;
           MinusSy:     kind := MinusExp;
           LogNotSy:    kind := LogNotExp;
           TildaSy:     kind := BitNotExp;
           else         Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        E := CastExpr ();
        E := NewUnaryExpr (loc, kind, E);
     end

     else if sy = SizeofSy then begin
        loc := SymLoc;
        GetSymbol;

        E := UnaryExpr ();
        E := NewUnaryExpr (loc, SizeofExp, E);
     end

     else if sy = NewSy then begin
        { !? }
     end

     else if sy = DeleteSy then begin
        { !? }
     end

     else E := PostfixExpr ();

     result := E;
End;

Function CastExpr: TExpr;
Begin
     result := UnaryExpr (); { !? }
End;

{--------------------------------------------------------------------------}

Function PmExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := CastExpr ();

     while sy in [DotStarSy, ArrowStarSy] do begin

        case sy of
           DotStarSy:   kind := MemberExp;
           ArrowStarSy: kind := PtrMemberExp;
           else          Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := CastExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function MultiplicativeExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := PmExpr ();

     while sy in [AsteriskSy, SlashSy, PercentSy] do begin

        case sy of
           AsteriskSy: kind := MulExp;
           SlashSy:    kind := DivExp;
           PercentSy:  kind := ModExp;
           else        Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := PmExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function AdditiveExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := MultiplicativeExpr ();

     while sy in [PlusSy, MinusSy] do begin

        case sy of
           PlusSy:  kind := AddExp;
           MinusSy: kind := SubExp;
           else     Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := MultiplicativeExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function ShiftExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := AdditiveExpr ();

     while sy in [ShlSy, ShrSy] do begin

        case sy of
           ShlSy: kind := ShlExp;
           ShrSy: kind := ShrExp;
           else   Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := AdditiveExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function RelationalExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := ShiftExpr ();

     while sy in [LessSy, GreaterSy, LessEqualSy, GreaterEqualSy] do begin

        case sy of
           LessSy:         kind := LtExp;
           GreaterSy:      kind := GtExp;
           LessEqualSy:    kind := LeExp;
           GreaterEqualSy: kind := GeExp;
           else            Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := ShiftExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function EqualityExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := RelationalExpr ();

     if sy in [UnEqualSy, EqualSy] then begin

        case sy of
           UnEqualSy: kind := NeExp;
           EqualSy:   kind := EqExp;
           else       Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := EqualityExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function AndExpr: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := EqualityExpr ();

     while sy = AmpersandSy do begin
        loc := SymLoc;
        GetSymbol;
        R := EqualityExpr ();
        E := NewBinaryExpr (loc, BitAndExp, E, R);
     End;

     result := E;
End;

Function XorExpr: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := AndExpr ();

     while sy = CaretSy do begin
        loc := SymLoc;
        GetSymbol;
        R := AndExpr ();
        E := NewBinaryExpr (loc, BitXorExp, E, R);
     End;

     result := E;
End;

Function OrExpr: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := XorExpr ();

     while sy = BarSy do begin
        loc := SymLoc;
        GetSymbol;
        R := XorExpr ();
        E := NewBinaryExpr (loc, BitOrExp, E, R);
     End;

     result := E;
End;

Function LogicalAndExpr: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := OrExpr ();

     while sy = LogAndSy do begin
        loc := SymLoc;
        GetSymbol;
        R := OrExpr ();
        E := NewBinaryExpr (loc, LogAndExp, E, R);
     End;

     result := E;
End;

Function LogicalOrExpr: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := AndExpr ();

     while sy = LogOrSy do begin
        loc := SymLoc;
        GetSymbol;
        R := AndExpr ();
        E := NewBinaryExpr (loc, LogOrExp, E, R);
     End;

     result := E;
End;

Function ConditionalExpr: TExpr;
Var  loc: TLocation;
     E, R1, R2: TExpr;
Begin
     E := LogicalOrExpr ();

     if sy = QuestionSy then begin
        loc := SymLoc;
        GetSymbol;

        R1 := Expression ();
        CheckSymbol (ColonSy);
        R2 := ConditionalExpr ();
        E := NewCondExpr (loc, E, R1, R2);
     end;

     result := E;
End;

Function AssignmentExpr: TExpr;
Var  loc: TLocation;
     kind: TBinaryKind;
     E, R: TExpr;
Begin
     E := ConditionalExpr (); { !? }

     while sy in [AssignSy,
                  MulAssignSy, DivAssignSy, ModAssignSy,
                  AddAssignSy, SubAssignSy,
                  ShlAssignSy, ShrAssignSy,
                  AndAssignSy, OrAssignSy, XorAssignSy] do begin

        case sy of
           AssignSy:      kind := AssignExp;
           MulAssignSy:   kind := MulAssignExp;
           DivAssignSy:   kind := DivAssignExp;
           ModAssignSy:   kind := ModAssignExp;
           AddAssignSy:   kind := AddAssignExp;
           SubAssignSy:   kind := SubAssignExp;
           ShlAssignSy:   kind := ShlAssignExp;
           ShrAssignSy:   kind := ShrAssignExp;
           AndAssignSy:   kind := AndAssignExp;
           OrAssignSy:    kind := OrAssignExp;
           XorAssignSy:   kind := XorAssignExp;
           else           Bug;
        end;

        loc := SymLoc;
        GetSymbol;

        R := AssignmentExpr ();
        E := NewBinaryExpr (loc, kind, E, R);
     End;

     result := E;
End;

Function ConstExpr: TExpr;
Begin
     result := AssignmentExpr ();
End;

Function Expression: TExpr;
Var  loc: TLocation;
     E, R: TExpr;
Begin
     E := AssignmentExpr ();

     while sy = CommaSy do begin
        loc := SymLoc;
        GetSymbol;

        R := AssignmentExpr ();
        E := NewBinaryExpr (loc, CommaExp, E, R);
     end;

     result := E;
End;

END.
