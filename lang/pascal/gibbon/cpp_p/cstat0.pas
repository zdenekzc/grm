
(**************************************************************************)
(*                                                                        *)
(*                              Statements                                *)
(*                                                                        *)
(**************************************************************************)

UNIT CStat0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     CExpr0;

Function Statement: TStat;

IMPLEMENTATION

(******************************* STATEMENTS *******************************)

Function StatementSeq: TStatSeq; forward;

{--------------------------------------------------------------------------}

Function BreakStatement: TStat;
Var  S: TBreakStat;
Begin
     S := TBreakStat.Create;
     CheckSymbol (BreakSy);
     CheckSymbol (SemicolonSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function ContinueStatement: TStat;
Var  S: TContinueStat;
Begin
     S := TContinueStat.Create;
     CheckSymbol (ContinueSy);
     CheckSymbol (SemicolonSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function ReturnStatement: TStat;
Var  S: TReturnStat;
Begin
     S := TReturnStat.Create;
     CheckSymbol (ReturnSy);
     if sy <> SemicolonSy then
        S.return_expr := Expression ();
     CheckSymbol (SemicolonSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function GotoStatement: TStat;
Var  S: TGotoStat;
Begin
     S := TGotoStat.Create;
     CheckSymbol (GotoSy);
     S.goto_lab := Identifier ();
     CheckSymbol (SemicolonSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function CompoundStatement: TStat;
Var  S: TCompoundStat;
Begin
     S := TCompoundStat.Create;
     CheckSymbol (LBraceSy);
     S.body_seq := StatementSeq ();
     CheckSymbol (RBraceSy);
     result := S;
End;

{--------------------------------------------------------------------------}

Function IfStatement: TStat;
Var  S: TIfStat;
Begin
     S := TIfStat.Create;
     CheckSymbol (IfSy);
     CheckSymbol (LParSy);
     S.cond_expr := Expression ();
     CheckSymbol (RParSy);
     S.then_stat := Statement ();

     if sy = ElseSy then begin
        GetSymbol;
        S.else_stat := Statement ();
     end;

     result := S;
End;

{--------------------------------------------------------------------------}

Function SwitchStatement: TStat;
Var  S: TSwitchStat;
Begin
     S := TSwitchStat.Create;
     CheckSymbol (SwitchSy);

     CheckSymbol (LParSy);
     S.switch_expr := Expression ();
     CheckSymbol (RParSy);

     S.body_stat := Statement ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function WhileStatement: TStat;
Var  S: TWhileStat;
Begin
     S := TWhileStat.Create;
     CheckSymbol (WhileSy);

     CheckSymbol (LParSy);
     S.cond_expr := Expression ();
     CheckSymbol (RParSy);

     S.body_stat := Statement ();
     result := S;
End;

{--------------------------------------------------------------------------}

Function DoStatement: TStat;
Var  S: TDoStat;
Begin
     S := TDoStat.Create;
     CheckSymbol (DoSy);
     S.body_stat := Statement ();
     CheckSymbol (WhileSy);

     CheckSymbol (LParSy);
     S.while_expr := Expression ();
     CheckSymbol (RParSy);

     result := S;
End;

{--------------------------------------------------------------------------}

Function ForStatement: TStat;
Var  S: TCppForStat;
Begin
     S := TCppForStat.Create;
     CheckSymbol (ForSy);

     CheckSymbol (LParSy);
     S.init_stat := Statement ();

     if sy <> SemicolonSy then
        S.cond_expr := Expression ();
     CheckSymbol (SemicolonSy);

     if sy <> RParSy then
        S.step_expr := Expression ();
     CheckSymbol (RParSy);

     S.body_stat := Statement ();
     result := S;
End;

{--------------------------------------------------------------------------}

Procedure ExceptionHandler (sect: TOnSect);
Var  S:   TOnItem;
Begin
     S := TOnItem.Create;
     CheckSymbol (CatchSy);
     CheckSymbol (LParSy);
     { !? }
     CheckSymbol (RParSy);
     S.body_stat := CompoundStatement ();

     sect.Add (S);
End;

Function TryStatement: TStat;
Var  S:   TExceptStat;
     tmp: TStatSeq;
Begin
     S := TExceptStat.Create;
     CheckSymbol (TrySy);
     CheckSymbol (LBraceSy);
     S.body_seq := StatementSeq ();
     CheckSymbol (RBraceSy);

     S.on_list := TOnSect.Create;
     ExceptionHandler (S.on_list);
     while sy = CatchSy do
        ExceptionHandler (S.on_list);

     result := S;
End;

{--------------------------------------------------------------------------}

Function Statement: TStat;
Var  S:    TStat;
     loc:  TLocation;
     expr: TExpr;
     SC:   TCaseLabeledStat;
     SD:   TDefaultLabeledStat;
     SL:   TLabeledStat;
     SE:   TExpressionStat;
Begin
     { umisteni }
     loc := SymLoc;

     { vlastni prikaz }
     case sy of
        BreakSy:     S := BreakStatement ();
        ContinueSy:  S := ContinueStatement ();
        ReturnSy:    S := ReturnStatement ();
        GotoSy:      S := GotoStatement ();
        IfSy:        S := IfStatement ();
        SwitchSy:    S := SwitchStatement ();
        WhileSy:     S := WhileStatement ();
        DoSy:        S := DoStatement ();
        ForSy:       S := ForStatement ();
        TrySy:       S := TryStatement ();

        CaseSy:      begin
                        SC := TCaseLabeledStat.Create;
                        SC.case_expr := Expression ();
                        CheckSymbol (ColonSy);
                        SC.body_stat := Statement ();
                        S := SC;
                     end;

        DefaultSy:   begin
                        SD := TDefaultLabeledStat.Create;
                        CheckSymbol (ColonSy);
                        SD.body_stat := Statement ();
                        S := SD;
                     end;

        LBraceSy:    S := CompoundStatement ();

        SemicolonSy: begin
                        S := TEmptyStat.Create;
                        CheckSymbol (SemicolonSy);
                     end;

        else         begin
                        expr := Expression;
                        if sy = ColonSy then begin
                           GetSymbol (); { skip : }
                           SL := TLabeledStat.Create;
                           SL.label_expr := expr;
                           SL.body_stat := Statement ();
                           S := SL;
                        end
                        else begin
                           SE := TExpressionStat.Create;
                           SE.expr := expr;
                           S := SE;
                        end;
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
     while sy <> RBrackSy do begin
        S := Statement ();
        result.Add (S);
     end;
End;

END.

