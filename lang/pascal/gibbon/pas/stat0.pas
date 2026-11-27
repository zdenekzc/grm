
(**************************************************************************)
(*                                                                        *)
(*                              Statements                                *)
(*                                                                        *)
(**************************************************************************)

UNIT Stat0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     Expr0;

// Function CompoundStatement: TStat;
Function StatementSeq: TStatSeq;

IMPLEMENTATION

(******************************* STATEMENTS *******************************)

Const EmptySet = [SemicolonSy,
                  EndSy, UntilSy,
                  ElseSy, FinallySy, ExceptSy, OnSy,
                  FinalizationSy];

Function Statement: TStat; forward;

{--------------------------------------------------------------------------}

Function GotoStatement: TStat;
Var  S: TGotoStat;
Begin
     S := TGotoStat.Create;
     CheckSymbol (GotoSy);
     S.goto_lab := Identifier ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function CompoundStatement: TStat;
Var  S: TCompoundStat;
Begin
     S := TCompoundStat.Create;
     CheckSymbol (BeginSy);
     S.body_seq := StatementSeq ();
     CheckSymbol (EndSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function IfStatement: TStat;
Var  S: TIfStat;
Begin
     S := TIfStat.Create;
     CheckSymbol (IfSy);
     S.cond_expr := Expression ();
     CheckSymbol (ThenSy);
     S.then_stat := Statement ();

     if sy = ElseSy then begin
        GetSymbol;
        S.else_stat := Statement ();
     end;

     result := S;
End;

{--------------------------------------------------------------------------}

Procedure CaseElem (sect: TElemSect);
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

Function CaseExpr: TElemSect;
Begin
     result := TElemSect.Create;
     CaseElem (result);

     while sy = CommaSy do begin
        GetSymbol;
        CaseElem (result);
     end;
End;

Procedure CasePart (sect: TCaseSect);
Var  S: TCaseItem;
Begin
     S := TCaseItem.Create;
     S.sel_list := CaseExpr ();

     CheckSymbol (ColonSy);
     S.sel_stat := Statement ();
     sect.Add (S);
End;

Function CaseStatement: TStat;
Var  S: TCaseStat;
Begin
     S := TCaseStat.Create;
     CheckSymbol (CaseSy);

     S.case_expr := Expression ();
     CheckSymbol (OfSy);

     S.case_list := TCaseSect.Create;
     CasePart (S.case_list);

     while sy = SemicolonSy do begin
        GetSymbol;
        if not (sy in [ElseSy, EndSy]) then
           CasePart (S.case_list);
     end;

     if sy = ElseSy then begin
        GetSymbol;
        S.else_seq := StatementSeq ();
     end;

     if sy = SemicolonSy then GetSymbol;
     CheckSymbol (EndSy);

     result := S;
End;

{--------------------------------------------------------------------------}

Function WhileStatement: TStat;
Var  S: TWhileStat;
Begin
     S := TWhileStat.Create;
     CheckSymbol (WhileSy);
     S.cond_expr := Expression ();
     CheckSymbol (DoSy);
     S.body_stat := Statement ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function RepeatStatement: TStat;
Var  S: TRepeatStat;
Begin
     S := TRepeatStat.Create;
     CheckSymbol (RepeatSy);
     S.body_seq := StatementSeq ();
     CheckSymbol (UntilSy);
     S.until_expr := Expression ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function ForStatement: TStat;
Var  S: TForStat;
Begin
     S := TForStat.Create;
     CheckSymbol (ForSy);

     S.var_expr := Variable ();
     IdentChk (S.var_expr);
     CheckSymbol (AssignSy);
     S.from_expr := Expression ();

     if sy = ToSy then begin
        GetSymbol;
        S.incr := true;
     end
     else if sy = DowntoSy then begin
        GetSymbol;
        S.incr := false;
     end
     else Error ('"TO" or "DOWNTO" expected');

     S.to_expr := Expression ();

     CheckSymbol (DoSy);
     S.body_stat := Statement ();

     result := S;
End;

{--------------------------------------------------------------------------}

Procedure WithVariable (sect: TWIthSect);
Var  item: TWithItem;
Begin
     item := TWithItem.Create;
     item.expr := Variable ();
     sect.Add (item);
End;

Function WithStatement: TStat;
Var  S: TWithStat;
Begin
     S := TWithStat.Create;
     CheckSymbol (WithSy);

     S.with_list := TWithSect.Create;
     WithVariable (S.with_list);

     while sy = CommaSy do begin
        GetSymbol;
        WithVariable (S.with_list);
     end;

     CheckSymbol (DoSy);
     S.body_stat := Statement ();

     result := S;
End;

{--------------------------------------------------------------------------}

Function RaiseStatement: TStat;
Var  S: TRaiseStat;
Begin
     S := TRaiseStat.Create;
     CheckSymbol (RaiseSy);

     if not (sy in EmptySet) then begin
        S.raise_expr := Expression ();
     end;

     result := S;
End;

{--------------------------------------------------------------------------}

Procedure ExceptionHandler (sect: TOnSect);
Var  S:   TOnItem;
     tmp: TExpr;
Begin
     S := TOnItem.Create;
     CheckSymbol (OnSy);
     tmp := Expression ();

     if sy = ColonSy then begin
        S.on_ident := ExtractIdentFromExpr (tmp);
        GetSymbol;
        tmp := Expression ();
     end;

     QualIdentChk (tmp);
     S.on_type := ExprToAlias (tmp);

     CheckSymbol (DoSy);
     S.body_stat := Statement ();

     sect.Add (S);
End;

Function ExceptPart (tmp: TStatSeq): TExceptStat;
Var  S: TExceptStat;
Begin
     S := TExceptStat.Create;
     S.body_seq := tmp;
     CheckSymbol (ExceptSy);
     S.on_list := TOnSect.Create;

     if sy = OnSy then begin
        ExceptionHandler (S.on_list);
        while sy = SemicolonSy do begin
           GetSymbol;
           if sy <> OnSy then break;
           ExceptionHandler (S.on_list);
        end;

        if sy = ElseSy then begin
           GetSymbol;
           S.else_seq := StatementSeq ();
        end;
     end
     else begin
        S.else_seq := StatementSeq ();
     end;

     result := S;
End;

Function FinallyPart (tmp: TStatSeq): TFinallyStat;
Var  S: TFinallyStat;
Begin
     S := TFinallyStat.Create;
     S.body_seq := tmp;
     CheckSymbol (FinallySy);
     S.finally_seq := StatementSeq ();
     result := S;
End;

Function TryStatement: TStat;
Var  S:   TStat;
     tmp: TStatSeq;
Begin
     CheckSymbol (TrySy);
     tmp := StatementSeq ();

     S := nil; { compiler }
     if sy = FinallySy then S := FinallyPart (tmp)
     else if sy = ExceptSy then S := ExceptPart (tmp)
     else Error ('"EXCEPT" or "FINALLY" expected');

     CheckSymbol (EndSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function EmptyStatement: TStat;
Var  S: TEmptyStat;
Begin
     S := TEmptyStat.Create;
     result := S;
End;

{--------------------------------------------------------------------------}

Function AssignStatement (tmp: TExpr): TStat;
Var  S: TAssignStat;
Begin
     S := TAssignStat.Create;
     S.left_expr := tmp;
     CheckSymbol (AssignSy);
     S.right_expr := Expression ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function CallStatement (tmp: TExpr): TStat;
Var  S: TCallStat;
Begin
     S := TCallStat.Create;
     S.call_expr := tmp;
     result := S;
End;

{--------------------------------------------------------------------------}

Function LabeledStatement (tmp: TExpr): TLabeledStat;
Var  S: TLabeledStat;
Begin
     IdentChk (tmp);
     S := TLabeledStat.Create;
     S.label_expr := tmp;
     CheckSymbol (ColonSy);
     S.body_stat := Statement ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function Statement: TStat;
Var  S:   TStat;
     SL:  TLabeledStat;
     loc: TLocation;
     tmp: TExpr;
Begin
     { umisteni }
     loc := SymLoc;

     { vlastni prikaz }
     case sy of
        GotoSy:    S := GotoStatement ();
        BeginSy:   S := CompoundStatement ();
        IfSy:      S := IfStatement ();
        CaseSy:    S := CaseStatement ();
        WhileSy:   S := WhileStatement ();
        RepeatSy:  S := RepeatStatement ();
        ForSy:     S := ForStatement ();
        WithSy:    S := WithStatement ();
        RaiseSy:   S := RaiseStatement ();
        TrySy:     S := TryStatement ();

        else       if sy in EmptySet then
                      S := EmptyStatement ()
                   else begin
                      tmp := Expression ();
                      if sy = ColonSy then begin
                         // S := LabeledStatement ();
                         IdentChk (tmp);
                         SL := TLabeledStat.Create;
                         SL.label_expr := tmp;
                         CheckSymbol (ColonSy);
                         SL.body_stat := Statement ();
                         S := SL;
                      end
                      else if sy = AssignSy then begin
                         loc := SymLoc;
                         S := AssignStatement (tmp)
                      end
                      else S := CallStatement (tmp);
                   end;
     end;

     S.loc := loc;
     result := S;
End;

{--------------------------------------------------------------------------}

Function StatementSeq: TStatSeq;
Var  S: TStat;
Begin
     result := TStatSeq.Create;

     S := Statement ();
     result.Add (S);

     while sy = SemicolonSy do begin
        GetSymbol;
        S := Statement ();
        result.Add (S);
     end;
End;

END.

