UNIT CList0;

INTERFACE

Uses SysUtils {func UpperCase},
     // Classes,
     Support {proc Translate},
     Fil0, Dir0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     List0;

Procedure SendCppModule (module: TModule);

Procedure SendCppCls (cls: TClsType);
Procedure SendCppImpl (module: TModule);

IMPLEMENTATION

Const func_level    = 1;
      unary_level   = 2;
      member_level  = 3;
      mul_level     = 4;
      add_level     = 5;
      shift_level   = 6;
      compare_level = 7;
      equal_level   = 8;
      and_level     = 9;
      xor_level     = 10;
      or_level      = 11;
      log_and_level = 12;
      log_or_level  = 13;
      select_level  = 14;
      assign_level  = 15;
      comma_level   = 16;

(******************************* EXPRESSION *******************************)

Procedure SendExpr (expr: TExpr); forward;

Procedure SendExprExt (expr: TExpr; level: integer);
Begin
     if expr.clevel <= level  then
        SendExpr (expr)
     else begin
        // Send ('/* priority */ ');
        Send ('(');
        SendExpr (expr);
        Send (')');
     end;
End;

Procedure SendComment (comment: string);
Begin
     if comment <> '' then begin
        if not StartOfLine then Send (' ');
        Send ('/* ');
        Send (comment);
        Send (' */');
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendString (txt: string; quo: char);
Const hex: array [0..15] of char =
      ('0', '1', '2', '3', '4', '5', '6', '7',
       '8', '9', 'a', 'b', 'c', 'd', 'e', 'f');
Var   i: integer;
      c: char;
      t: string [255];
Begin
     if txt = '' then t := quo + quo
     else begin
        t := quo;

        for i := 1 to length (txt) do begin
           c := txt[i];
           if c = ^M then t := t + '\r'
           else if c = ^J then t := t + '\n'
           else if ord (c) < 32 then begin
              t := t + '\x' +
                   hex [ord (c) div 16] +
                   hex [ord (c) mod 16];
           end
           else begin
              if c = '\' then t := t + '\\'
              else if c = quo then t := t + '\' + quo
              else t := t + c;
           end;
        end; {for}

        t := t + quo;
     end; {if}

     Send (t);
End;

{--------------------------------------------------------------------------}

Procedure SendArgSect (sect: TArgSect);
Var  item: TArgItem;
Begin
     if sect.long_params then begin
        SendEol;
        IncIndent;
        Send ('(');
        IncrIndent (1);
     end
     else Send (' (');

     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin

        SendExpr (item.value);

        { !?
        if item.width <> nil then begin
           Send (': ');
           SendExpr (item.width);
        end;

        if item.digits <> nil then begin
           Send (': ');
           SendExpr (item.digits);
        end;
        }

        if item.next <> nil then begin
           Send (',');
           if sect.long_params then SendEol
                               else Send (' ');
        end;

        item := item.next;
     end;

     Send (')');
     if sect.long_params then begin
        DecrIndent (1);
        DecIndent;
     end;
End;

Procedure SendInxSect (sect: TInxSect);
Var  item: TInxItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        Send (' [');
        SendExpr (item.value);
        Send (']');
        item := item.next;
     end;
End;

Procedure SendElemSect (sect: TElemSect);
Var  item: TElemItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        SendExpr (item.low);
        if item.high <> nil then begin
           Send (' .. '); { !? }
           SendExpr (item.high);
        end;
        if item.next <> nil then Send (', ');
        item := item.next;
     end;
End;

Procedure SendStructSect (sect: TStructSect);
Var  item: TStructItem;
     compound: boolean;
Begin
     Assert (sect <> nil);
     compound := (sect.arr or sect.rec);

     if compound then Send ('{')
                 else Send ('(');

     item := sect.first;
     while item <> nil do begin

        { !?
        if item.name <> '' then begin
           Send (item.name);
           Send (': ');
        end;
        }

        SendExpr (item.value);

        if item.next <> nil then Send (', ');
        item := item.next;
     end;

     if compound then Send ('}')
                 else Send (')');
End;

{--------------------------------------------------------------------------}

Procedure SendCallExpr (E: TCallExpr);
Begin
     { nazev funkce }
     SendExprExt (E.func, func_level);

     { parametry }
     SendArgSect (E.list);
End;

Procedure SendIdentExpr (E: TIdentExpr);
Begin
     Send (E.ident);
End;

Procedure SendIndexExpr (E: TIndexExpr);
Begin
     SendExprExt (E.left, func_level);
     SendInxSect (E.list);
End;

Procedure SendSuperExpr (E: TSuperExpr);
Begin
     { !? }
     Send (E.ident);
End;

{--------------------------------------------------------------------------}

Procedure SendBinaryExpr (txt: string; E: TBinaryExpr);
Begin
     SendExprExt (E.left, E.clevel);
     Send (' ');
     Send (txt);
     Send (' ');
     SendExprExt (E.right, E.clevel-1);
End;

Procedure SendUnaryExpr (txt: string; E: TUnaryExpr);
Begin
     Send (txt);
     Send (' ');
     if E.param <> nil then
         SendExprExt (E.param, E.clevel);
End;

Procedure SendPostExpr (E: TUnaryExpr; txt: string);
Begin
     SendExprExt (E.param, E.clevel);
     Send (' ');
     Send (txt);
End;

Procedure SendIsExpr (E: TBinaryExpr);
Begin
     Send ('IS (');
     SendExpr (E.left);
     Send (', ');
     SendExpr (E.right);
     Send (')');
End;

Procedure SendAsExpr (E: TBinaryExpr);
Begin
     Send ('AS (');
     SendExpr (E.left);
     Send (', ');
     SendExpr (E.right);
     Send (')');
End;

Procedure SendInExpr (E: TBinaryExpr);
Begin
     { !? }
     Send ('IN (');
     SendExpr (E.left);
     Send (', ');
     SendExpr (E.right);
     Send (')');
End;

Procedure SendAndExpr (E: TBinaryExpr);
Begin
     SendBinaryExpr ('&&', E)
     // !? SendBinaryExpr ('&', E);
End;

Procedure SendOrExpr (E: TBinaryExpr);
Begin
     SendBinaryExpr ('||', E)
     // !? SendBinaryExpr ('|', E);
End;

Procedure SendNotExpr (E: TUnaryExpr);
Begin
     SendUnaryExpr ('!', E)
     // !? SendUnaryExpr ('~', E);
End;

Procedure SendAdrExpr (E: TUnaryExpr);
Begin
     SendUnaryExpr ('&', E);
End;

{--------------------------------------------------------------------------}

Procedure SelectBinaryExpr (expr: TBinaryExpr);
Begin
     case expr.kind of
        MulExp:  SendBinaryExpr ('*', expr);
        RDivExp: SendBinaryExpr ('/', expr);
        DivExp:  SendBinaryExpr ('/', expr);
        ModExp:  SendBinaryExpr ('%', expr);
        AndExp:  SendAndExpr    (expr);
        ShlExp:  SendBinaryExpr ('<<', expr);
        ShrExp:  SendBinaryExpr ('>>', expr);
        AsExp:   SendAsExpr     (expr);

        AddExp:  SendBinaryExpr ('+', expr);
        SubExp:  SendBinaryExpr ('-', expr);
        OrExp:   SendOrExpr     (expr);
        XorExp:  SendBinaryExpr ('^', expr);

        EqExp:   SendBinaryExpr ('==', expr);
        NeExp:   SendBinaryExpr ('!=', expr);
        LtExp:   SendBinaryExpr ('<',  expr);
        GtExp:   SendBinaryExpr ('>',  expr);
        LeExp:   SendBinaryExpr ('<=', expr);
        GeExp:   SendBinaryExpr ('>=', expr);
        InExp:   SendInExpr (expr);
        IsExp:   SendIsExpr (expr);

        FieldExp:     SendBinaryExpr ('.',  expr);

        ScopeExp:     SendBinaryExpr ('::',  expr);
        PtrFieldExp:  SendBinaryExpr ('->',  expr);

        MemberExp:    SendBinaryExpr ('.*',  expr);
        PtrMemberExp: SendBinaryExpr ('->*', expr);

        BitAndExp:    SendBinaryExpr ('&',   expr);
        BitOrExp:     SendBinaryExpr ('|',   expr);
        BitXorExp:    SendBinaryExpr ('^',   expr);
        LogAndExp:    SendBinaryExpr ('&&',  expr);
        LogOrExp:     SendBinaryExpr ('||',  expr);

        AssignExp:    SendBinaryExpr ('=',   expr);
        MulAssignExp: SendBinaryExpr ('*=',  expr);
        DivAssignExp: SendBinaryExpr ('/=',  expr);
        ModAssignExp: SendBinaryExpr ('%=',  expr);
        AddAssignExp: SendBinaryExpr ('+=',  expr);
        SubAssignExp: SendBinaryExpr ('-=',  expr);
        ShlAssignExp: SendBinaryExpr ('<<=', expr);
        ShrAssignExp: SendBinaryExpr ('>>=', expr);
        AndAssignExp: SendBinaryExpr ('&=',  expr);
        OrAssignExp:  SendBinaryExpr ('|=',  expr);
        XorAssignExp: SendBinaryExpr ('^=',  expr);

        CommaExp:     SendBinaryExpr (',',   expr);

        else     Bug;
     end;
End;

Procedure SelectUnaryExpr (expr: TUnaryExpr);
Begin
     case expr.kind of
        NotExp:        SendNotExpr   (expr);
        PlusExp:       SendUnaryExpr ('+', expr);
        MinusExp:      SendUnaryExpr ('-', expr);
        AdrExp:        SendAdrExpr   (expr);
        DerefExp:      SendUnaryExpr ('*', expr);

        GlobalExp:     SendUnaryExpr ('::', expr);
        DestructorExp: SendUnaryExpr ('~', expr);

        ParExp:        begin
                          Send ('( ');
                          SendExpr (expr.param);
                          Send (' )');
                       end;

        SizeofExp:     begin
                          Send ('sizeof ( ');
                          SendExpr (expr.param);
                          Send (' )');
                       end;

        BitNotExp:     SendUnaryExpr ('~', expr);
        LogNotExp:     SendUnaryExpr ('!', expr);

        PreIncExp:     SendUnaryExpr ('++', expr);
        PreDecExp:     SendUnaryExpr ('--', expr);
        PostIncExp:    SendPostExpr (expr, '++');
        PostDecExp:    SendPostExpr (expr, '--');

        else           Bug;
     end;
End;

Procedure SelectValueExpr (expr: TValueExpr);
Begin
     case expr.kind of
        IntValueExp: Send (expr.value);
        FltValueExp: Send (expr.value);
        ChrValueExp: SendString (expr.value, quote1);
        StrValueExp: SendString (expr.value, quote2); { !? uvozovky }
        else         Bug;
     end;
End;

Procedure SendExpr (expr: TExpr);
Begin
     Assert (expr <> nil);

     case expr.tag of
        BinaryExp: SelectBinaryExpr (expr as TBinaryExpr);
        UnaryExp:  SelectUnaryExpr (expr as TUnaryExpr);
        ValueExp:  SelectValueExpr (expr as TValueExpr);

        IdentExp:  SendIdentExpr (expr as TIdentExpr);
        IndexExp:  SendIndexExpr (expr as TIndexExpr);
        CallExp:   SendCallExpr  (expr as TCallExpr);

        SetExp:    with expr as TSetExpr do begin {!?}
                      Send ('[');
                      SendElemSect (list);
                      Send (']');
                   end;

        StructExp: with expr as TStructExpr do
                      SendStructSect (list);

        NilExp:    Send ('null');

        StringExp: with expr as TStringExpr do begin
                      Send ('string');
                      if param <> nil then begin
                         Send (' (');
                         SendExpr (param);
                         Send (')');
                      end;
                   end;

        SuperExp:  SendSuperExpr (expr as TSuperExpr);

        ThisExp:   Send ('this');

        CondExp:   with expr as TCondExpr do begin
                      SendExpr (cond);
                      Send (' ? ');
                      SendExpr (true_expr);
                      Send (' : ');
                      SendExpr (false_expr);
                   end;

        TextExp:   with expr as TTextExpr do
                      Send (text);

        else       Bug;
     end;
End;

(******************************* STATEMENT ********************************)

Procedure SendStat (stat: TStat); forward;
Procedure SendType (typ: TType); forward;
Procedure SendTypeName (typ: TType); forward;

{--------------------------------------------------------------------------}

Procedure SendCaseList (sect: TElemSect);
Var  item: TElemItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        Send ('case ');
        SendExpr (item.low);
        if item.high <> nil then begin
           Send (' ... '); { !? }
           SendExpr (item.high);
        end;
        Send (': ');
        SendEol;
        item := item.next;
     end;
End;

Procedure SendCaseSect (sect: TCaseSect);
Var  item: TCaseItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        SendCaseList (item.sel_list);

        IncIndent;
        SendStat (item.sel_stat);
        SendEol;
        Send ('break;');
        SendEol;
        DecIndent;

        item := item.next;
     end;
End;

Procedure SendOnSect (sect: TOnSect);
Var  item: TOnItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        Send ('catch (');

        SendTypeName (item.on_type);

        if item.on_ident <> '' then begin
           Send (' ');
           Send (item.on_ident);
        end;

        Send (')');
        SendEol;

        if item.body_stat.tag = CompoundSt then
           SendStat (item.body_stat)
        else begin
           Send ('{');
           SendEol;

           IncIndent;
           SendStat (item.body_stat);
           SendEol;
           DecIndent;

           Send ('}');
        end;

        item := item.next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendStatSeq (sect: TStatSeq);
Var  stat: TStat;
Begin
     Assert (sect <> nil);
     sect.Sort;

     stat := sect.first;

     while stat <> nil do begin
        if stat.tag = TextSt then begin
           if (stat.next <> nil) or not (stat as TTextSTat).optional then begin
              SendStat (stat);
              SendEol;
           end;
        end
        else if stat.tag <> EmptySt then begin
           SendStat (stat);
           if stat.tag <> GroupSt then SendEol;
        end;
        stat := stat.next;
     end;
End;

Procedure SendInnerStat (stat: TStat);
Begin
     if stat.tag = CompoundSt then begin
        SendStat (stat);
     end
     else begin
        IncIndent;
        SendStat (stat);
        DecIndent;
     end;
End;

Procedure SendStat (stat: TStat);
Begin
     Assert (stat <> nil);

     case stat.tag of
        EmptySt:    ;

        AssignSt:   with stat as TAssignStat do begin
                       SendExpr (left_expr);
                       Send (' = ');
                       SendExpr (right_expr);
                       Send (';');
                    end;

        CallSt:     with stat as TCallStat do begin
                       SendExpr (call_expr);
                       Send (';');
                     end;

        CompoundSt: with stat as TCompoundStat do begin
                       Send ('{');
                       SendEol;
                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;
                       Send ('}');
                    end;

        GotoSt:     with stat as TGotoStat do begin
                       Send ('goto ');
                       Send (goto_lab);
                       Send (';');
                    end;

        IfSt:       with stat as TIfStat do begin
                       Send ('if (');
                       SendExpr (cond_expr);
                       Send (')');
                       SendEol;
                       SendInnerStat (then_stat);

                       if else_stat <> nil then begin
                          SendEol;
                          Send ('else');
                          SendEol;
                          SendInnerStat (else_stat);
                       end;
                    end;

        CaseSt:     with stat as TCaseStat do begin
                       Send ('switch (');
                       SendExpr (case_expr);
                       Send (')');
                       SendEol;

                       Send ('{');
                       SendEol;

                       IncIndent;
                       SendCaseSect (case_list);
                       DecIndent;

                       if else_seq <> nil then begin
                          SendEol;
                          IncIndent;
                          Send ('default:');
                          SendEol;

                          IncIndent;
                          SendStatSeq (else_seq);
                          SendEol;
                          Send ('break;');
                          SendEol;
                          DecIndent;

                          DecIndent;
                       end;

                       Send ('}');
                    end;

        WhileSt:    with stat as TWhileStat do begin
                       Send ('while (');
                       SendExpr (cond_expr);
                       Send (')');
                       SendEol;

                       SendInnerStat (body_stat);
                    end;

        RepeatSt:   with stat as TRepeatStat do begin
                       Send ('do {');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('} while (!(');
                       SendExpr (until_expr);
                       Send ('));');
                    end;

        ForSt:      with stat as TForStat do begin
                       Send ('for (');

                       SendExpr (var_expr);
                       Send (' = ');
                       SendExpr (from_expr);
                       Send ('; ');

                       SendExpr (var_expr);
                       if incr then Send (' <= ')
                               else Send (' >= ');
                       SendExpr (to_expr);
                       Send ('; ');

                       SendExprExt (var_expr, unary_level);
                       if incr then Send (' ++')
                               else Send (' --');

                       Send (')');
                       SendEol;

                       SendInnerStat (body_stat);
                    end;

        WithSt:     Bug; { !? }

        RaiseSt:    with stat as TRaiseStat do begin
                       Send ('throw');
                       if raise_expr <> nil then begin
                          Send (' ');
                          SendExpr (raise_expr);
                          {
                          if at_expr <> nil then begin
                             Send (' at ');
                             SendExpr (at_expr);
                          end;
                          }
                       end;
                       Send (';');
                    end;

        FinallySt:  with stat as TFinallyStat do begin
                       // Send ('/* try finally */ ');

                       Send ('{');
                       SendEol;
                       IncIndent;

                       Send ('try');
                       SendEol;

                       Send ('{');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('}');
                       SendEol;

                       Send ('catch (...)');
                       SendEol;

                       Send ('{');
                       SendEol;

                       IncIndent;
                       SendStatSeq (finally_seq);
                       Send ('throw;');
                       SendEol;
                       DecIndent;

                       Send ('}');
                       SendEol;

                       SendStatSeq (finally_seq); { !? opakuje se }

                       DecIndent;
                       Send ('}');
                    end;

        ExceptSt:   with stat as TExceptStat do begin
                       Send ('try');
                       SendEol;

                       Send ('{');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('}');
                       SendEol;

                       SendOnSect (on_list);

                       if else_seq <> nil then begin
                          Send ('catch (...)');
                          SendEol;
                          Send ('{');
                          SendEol;

                          IncIndent;
                          SendStatSeq (else_seq);
                          DecIndent;

                          Send ('}');
                       end;
                    end;

        TextSt:     with stat as TTextStat do
                       Send (text);

        GroupSt:    with stat as TGroupStat do
                       SendStatSeq (body_seq);

        BreakSt:    Send ('break;');

        ContinueSt: Send ('continue;');

        ReturnSt:   with stat as TReturnStat do begin
                       Send ('return');
                       if return_expr <> nil then begin
                          Send (' ');
                          SendExpr (return_expr);
                       end;
                       Send (';');
                    end;

        SwitchSt:   with stat as TSwitchStat do begin
                       Send ('switch (');
                       SendExpr (switch_expr);
                       Send (')');
                       SendEol;

                       SendInnerStat (body_stat);
                    end;

        DoSt:       with stat as TDoStat do begin
                       Send ('do');
                       SendEol;

                       SendInnerStat (body_stat);

                       Send ('while (');
                       SendExpr (while_expr);
                       Send (');');
                       SendEol;
                    end;

        CppForSt:   with stat as TCppForStat do begin
                       Send ('for (');
                       SendStat (init_stat);
                       Send (' ');
                       SendExpr (cond_expr);
                       Send ('; ');
                       SendExpr (step_expr);
                       Send (')');
                       SendEol;

                       SendInnerStat (body_stat);
                    end;

        LabeledSt:  with stat as TLabeledStat do begin
                       SendExpr (label_expr);
                       Send (': ');
                       SendStat (body_stat);
                    end;

        CaseLabeledSt:
                    with stat as TCaseLabeledStat do begin
                       Send ('case ');
                       SendExpr (case_expr);
                       Send (': ');
                       SendStat (body_stat);
                    end;

        DefaultLabeledSt:
                    with stat as TDefaultLabeledStat do begin
                       Send ('defualt: ');
                       SendStat (body_stat);
                    end;

        else        Bug;
     end;
End;

(********************************** TYPE **********************************)

Type TDeclMode = (intf_mode,    { interface part of unit }
                  global_mode,  { implementation part, program, library }
                  local_mode,   { subroutine local declarations }
                  member_mode); { class members, record fields }


Procedure SendDeclSect (sect: TDeclSect; mode: TDeclMode); forward;
Procedure SendDeclSect_ClassMembers (sect: TDeclSect); forward;

{--------------------------------------------------------------------------}

Procedure SendEnumSect (sect: TEnumSect);
Var  item: TEnumItem;
Begin
     Assert (sect <> nil);

     SendEol; { start on new line }

     IncIndent;
     Send ('{');

     item := sect.first;
     while item <> nil do begin
        Send (item.name);
        SendComment (item.comment);
        if item.next <> nil then begin
           Send (',');
           SendEol;
           Send (' ');
        end;
        item := item.next;
     end;

     Send ('}');
     DecIndent;
End;

Procedure SendParameters (sect: TParamSect);
Var  item: TParamItem;
Begin
     if sect.long_params then begin
        SendEol;
        IncIndent;
        Send ('(');
        IncrIndent (1);
     end
     else Send (' (');

     if (sect <> nil) and (sect.first <> nil) then begin

        item := sect.first;
        while item <> nil do begin

           (* !?
           case item.mode of
              ValueParam: { nothing } ;
              VarParam:   Send ('var ');
              ConstParam: Send ('const ');
              OutParam:   Send ('out ');
              else        Bug;
           end;
           *)

           if item.typ <> nil then begin
              SendTypeName (item.typ);
              Send (' ');
           end;

           Send (item.name);

           if item.ini <> nil then begin
              Send (' = ');
              SendExpr (item.ini);
           end;

           if item.next <> nil then begin
              Send (',');
              if sect.long_params then SendEol
                                  else Send (' ');
           end;

           item := item.next;
        end;

     end;

     Send (')');
     if sect.long_params then begin
        DecrIndent (1);
        DecIndent;
     end;
End;

Procedure SendInterfaceSect (ifc: TInterfaceSect);
Var  t: TInterfaceItem;
Begin
     t := ifc.first;
     while t <> nil do begin
        SendTypeName (t.ifc);
        if t.next <> nil then Send (', ');
        t := t.next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendPropertyDecl (item: TPropertyDecl);
Begin
     with item do begin
        Send ('property ');
        Send (name);
        SendParameters (param_list);
        if typ <> nil then begin
           Send (': ');
           SendTypeName (typ);
        end;

        if index <> nil then begin
           Send (' index ');
           SendExpr (index);
        end;

        if a_read <> nil then begin
           Send (' read ');
           SendExpr (a_read);
        end;

        if a_write <> nil then begin
           Send (' write ');
           SendExpr (a_write);
        end;

        if a_stored <> nil then begin
           Send (' stored ');
           SendExpr (a_stored);
        end;

        if a_default <> nil then begin
           Send (' default ');
           SendExpr (a_default);
        end;
        if a_nodefault then Send (' nodefault');

        if a_implements <> nil then begin
           Send (' implements ');
           SendInterfaceSect (a_implements);
        end;

        if a_def_array then Send (' default');

        Send (';');
        SendComment (comment);
        SendEol;
     end;
End;

Procedure SendClsType (cls: TClsType);
Var  any_ifc: boolean;
Begin
     with cls do begin
        case tag of
           ObjectTyp:    Send ('object');
           ClassTyp:     Send ('class');
           InterfaceTyp: Send ('interface');
           else          Bug;
        end;

        any_ifc := (ifc_list <> nil) and (ifc_list.first <> nil);
        if (parent <> nil) or any_ifc then begin
           Send (' : public ');
           if parent <> nil then begin
              SendTypeName (parent);
              if any_ifc then Send (', ');
           end;
           if any_ifc then SendInterfaceSect (ifc_list);
        end;

        SendComment (comment); { !? komentar typu }

        if not forw then begin
           SendEol;
           Send ('{');
           SendEol;
           IncIndent;
           if members <> nil then
              SendDeclSect_ClassMembers (members);
           DecIndent;
           Send ('}');
        end;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendCall (call: TCall);
Begin
     case call of
        RegisterCall: Send ('register ');
        PascalCall:   Send ('pascal ');
        CdeclCall:    Send ('cdecl ');
        StdcallCall:  Send ('stdcall ');
        SafecallCall: Send ('safecall ');
        else          Bug;
     end;
End;

Procedure SendProcType (typ: TProcType);
Begin
     case typ.style of
        ProcedureStyle:   Send ('procedure ');
        FunctionStyle:    Send ('function ');
        else              Bug;
     end;

     SendParameters (typ.param_list);

     if typ.answer <> nil then begin
        Send (': ');
        SendTypeName (typ.answer);
     end;

     if typ.of_object then Send (' of object');
     if typ.call <> NoCall then SendCall (typ.call);
End;

{--------------------------------------------------------------------------}

Procedure SendType (typ: TType);
Begin
     Assert (typ <> nil);

     case typ.tag of
        AliasTyp:      with typ as TAliasType do
                          SendExpr (qual_ident);

        SubrangeTyp:   with typ as TSubrangeType do begin
                          Send ('subrange <');
                          SendExpr (low);
                          Send (', ');
                          SendExpr (high);
                          Send ('>');
                       end;

        EnumTyp:       with typ as TEnumType do begin
                          SendComment (comment); { !? komentar typu }
                          SendEnumSect (elements);
                       end;

        StringTyp:     with typ as TStringType do begin
                          Send ('string');
                          if lim <> nil then begin
                             Send (' <');
                             SendExpr (lim);
                             Send ('>');
                          end;
                       end;

        ArrayTyp:      with typ as TArrayType do begin
                          Send ('array_of <');
                          if not dynamic_array and not open_array then begin
                             SendTypeName (index);
                             Send (', ');
                          end;
                          SendTypeName (elem);
                          Send ('>');
                       end;

        RecordTyp:     with typ as TRecordType do begin
                          Send ('struct');
                          SendEol;
                          Send ('{');
                          SendEol;
                          IncIndent;
                          SendDeclSect (fields, member_mode);
                          DecIndent;
                          Send ('}');
                       end;

        PointerTyp:    with typ as TPointerType do begin
                          Send ('* ');
                          SendTypeName (elem);
                       end;

        SetTyp:        with typ as TSetType do begin
                          Send ('set_of <');
                          if elem <> nil then SendTypeName (elem);
                          Send ('>');
                       end;

        FileTyp:       with typ as TFileType do begin
                          Send ('file_of <');
                          if not untyped_file then begin
                             SendTypeName (elem);
                          end;
                          Send ('>');
                       end;

        ObjectTyp,
        ClassTyp,
        InterfaceTyp:  SendClsType (typ as TClsType);

        ClassOfTyp:    with typ as TClassOfType do begin
                          Send ('class_of <');
                          SendTypeName (elem);
                          Send ('>');
                       end;

        ProcTyp:       SendProcType (typ as TProcType);

        else           Bug;
     end;
End;

Procedure SendTypeName (typ: TType);
Begin
     if typ.name <> '' then
        Send (typ.name)
     else
        SendType (typ);
End;

(****************************** DECLARATION *******************************)

Procedure SendLabelDecl (decl: TLabelDecl);
Begin
     { nothing }
End;

Procedure SendConstDecl (decl: TConstDecl);
Begin
     Send (' const ');
     if decl.typ <> nil then begin
        SendTypeName (decl.typ);
        Send (' ');
     end;
     Send (decl.name);
     Send (' = ');
     SendExpr (decl.val);
     Send (';');
     SendComment (decl.comment);
     SendEol;
End;

Procedure SendTypeDecl (decl: TTypeDecl);
Begin
     Send ('typedef ');
     SendType (decl.typ);
     Send (' ');
     Send (decl.name);
     Send (';');
     SendComment (decl.comment); { !? u tridy a vyctoveho typu by se mohl opakovat }
     SendEol;
End;

Procedure SendVarDecl (decl: TVarDecl);
Begin
     SendTypeName (decl.typ);
     Send (' ');
     Send (decl.name);

     if decl.ini <> nil then begin
        Send (' = ');
        SendExpr (decl.ini);
     end;

     Send (';');
     SendComment (decl.comment);
     SendEol;
End;

{--------------------------------------------------------------------------}

Procedure SendProcDecl (decl: TProcDecl;
                        p_context: string;
                        mode: TDeclMode);
Begin
     with decl do begin
        if a_inline then Send ('inline ');
        if mode = member_mode then
           if a_virtual or a_dynamic or a_override then Send ('virtual ');
        if static_proc then Send ('static ');
        if call <> NoCall then SendCall (call);

        if (style = ProcedureStyle) and (answer <> nil) then
           style := FunctionStyle;

        case style of
           ProcedureStyle:   Send ('void ');
           FunctionStyle:    begin
                                SendTypeName (answer);
                                Send (' ');
                             end;
        end;

        if mode = global_mode then
           if context <> '' then
              p_context := context;

        if p_context <> '' then begin
           Send (p_context);
           Send ('::');
        end;

        Send (name);
        SendParameters (param_list);

        { !?
        if a_forward then Send (' forward;');
        if a_reintroduce then Send (' reintroduce;');
        if a_overload then Send (' overload;');

        if a_external then begin
           Send (' external ');
           if a_lib <> nil then SendExpr (a_lib);
           if a_name <> nil then begin
              Send (' name ');
              SendExpr (a_name);
           end;
           if a_index <> nil then begin
              Send (' index ');
              SendExpr (a_index);
           end;
           Send (';');
        end;

        if a_message <> nil then begin
           Send (' message ');
           SendExpr (a_message);
           Send (';');
        end;
        }

        if mode = member_mode then
           if a_abstract then Send (' = 0;');

        SendComment (comment);

        { procedure body }
        if (mode in [global_mode, local_mode]) and (body <> nil) then begin
           SendEol;

           Send ('{');
           SendEol;
           IncIndent;

           if local <> nil then SendDeclSect (local, local_mode);
           SendStatSeq (body);

           DecIndent;
           Send ('}');
           SendEol;
        end
        else begin
           Send (';');
           SendEol;
        end;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendTextDecl (decl: TTextDecl);
Begin
     with decl do begin
        Send (text);
        SendEol;
     end;
End;

{--------------------------------------------------------------------------}

Function IsCls (decl: TDecl): boolean;
{ Test for complete class, object or interface declaration }
Var  typ: TType;
     cls: TClsType;
Begin
     result := false;
     if decl.tag = TypeDcl then begin
        typ := (decl as TTypeDecl).typ;
        if typ.tag in [ObjectTyp, ClassTyp, InterfaceTyp] then begin
           cls := typ as TClsType;
           if not cls.forw then
              result := true;
        end;
     end;
End;

Function IsClass (decl: TDecl): boolean;
{ Test for complete class declaration }
Var  typ: TType;
     cls: TClsType;
Begin
     result := false;
     if decl.tag = TypeDcl then begin
        typ := (decl as TTypeDecl).typ;
        if typ.tag = ClassTyp then begin
           cls := typ as TClsType;
           if not cls.forw then
              result := true;
        end;
     end;
End;

Function IsBig (decl: TDecl): boolean;
Var  typ: TType;
Begin
     result := IsCls (decl);
     if not result and (decl.tag = TypeDcl) then begin
        typ := (decl as TTypeDecl).typ;
        result := typ.tag in [EnumTyp, RecordTyp];
     end;
End;

Procedure SendDecl (decl: TDecl;
                    mode: TDeclMode);
Var  stop:  boolean;
Begin
     case decl.tag of
        LabelDcl:    SendLabelDecl (decl as TLabelDecl);
        ConstDcl:    SendConstDecl (decl as TConstDecl);
        TypeDcl:     SendTypeDecl (decl as TTypeDecl);
        VarDcl:      SendVarDecl (decl as TVarDecl);

        ProcDcl:     SendProcDecl (decl as TProcDecl, '', mode);

        PropertyDcl: SendPropertyDecl (decl as TPropertyDecl);
        TextDcl:     SendTextDecl (decl as TTextDecl);
        else         Bug;
     end;

     { empty line after declaration }
     stop := false;

     { end of section }
     if mode in [intf_mode, global_mode] then
        stop := (decl.next = nil) or
                (decl.next.tag <> decl.tag);

     { class declarations }
     if IsBig (decl) or
        (decl.next <> nil) and IsBig (decl.next) then
        stop := true;

     { subroutines }
     if (decl.tag = ProcDcl) and (mode in [global_mode, local_mode]) then
        stop := true;

     if stop then SendLn ('');
End;

{--------------------------------------------------------------------------}

Function NewForwardClass (id: TIdent): TTypeDecl;
Var  typ: TClassType;
Begin
     typ := TClassType.Create;
     typ.forw := true;

     result := TTypeDecl.Create;
     result.name := id;
     result.typ := typ;
End;

Procedure ScanForwardClasses (sect: TDeclSect);
Var  decl, start, tmp: TDecl;
     count, i: integer;
Begin
     decl := sect.first;
     while decl <> nil do begin

        { count full class declarations }
        start := decl;
        count := 0;
        while (decl <> nil) and IsClass (decl) do begin
           inc (count);
           decl := decl.next;
        end;

        { create forward declarations }
        if count > 1 then begin
           tmp := start;
           for i := 1 to count do begin
              start.InsertBefore (NewForwardClass (tmp.name));
              tmp := tmp.next;
           end;
        end;

        if decl <> nil then
           decl := decl.next;
     end;
End;

Procedure SendDeclSect (sect: TDeclSect; mode: TDeclMode);
Var  decl: TDecl;
Begin
     sect.Sort;

     if mode in [intf_mode, global_mode] then
        ScanForwardClasses (sect);

     decl := sect.first;
     while decl <> nil do begin
        SendDecl (decl, mode);
        decl := decl.next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendAccess (access: TAccess);
Begin
     case access of
        PrivateAccess:   Send ('private:');
        ProtectedAccess: Send ('protected:');
        PublicAccess:    Send ('public:');
        PublishedAccess: Send ('published:'); {!?}
        AutomatedAccess: Send ('automated:'); {!?}
        else             Bug;
     end;
     SendEol;
End;

Procedure SendDeclSect_ClassMembers (sect: TDeclSect);
Var  item: TDecl;
     prev: TAccess;
     any:  boolean;
Begin
     sect.Sort;

     any := false;
     item := sect.first;

     while item <> nil do begin

        if not any or (item.access <> prev) then
           if item.tag <> TextDcl then begin
              SendAccess (item.access);
              any := true;
              prev := item.access;
           end;

        if item.tag <> TextDcl then IncIndent;
        SendDecl (item, member_mode);
        if item.tag <> TextDcl then DecIndent;

        if item.tag = TextDcl then
           any := false; { write again access specificaton }

        item := item.next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendProcImpl (proc: TProcDecl; p_context: string);
Begin
     if not proc.skip_impl then begin
        if proc.comment_impl then SendLn ('/*');

        SendProcDecl (proc, p_context, global_mode);

        if proc.comment_impl then SendLn ('*/');
        SendLn ('');
     end;
End;

Procedure SendClassImpl (decl: TTypeDecl);
Var  cls:    TClsType;
     member: TDecl;
     proc:   TProcDecl;
     any:    boolean;
Begin
     cls := decl.typ as TClsType;

     { members }
     if cls.members <> nil then begin
        any := false;
        member := cls.members.first;
        while member <> nil do begin

           { method }
           if member.tag = ProcDcl then begin
              proc := member as TProcDecl;
              if not proc.a_abstract and not proc.skip_impl then begin

                 if not any then begin
                    Send ('/* ');
                    Send (decl.name);
                    Send (' */');
                    SendEol;
                    SendLn ('');
                    any := true;
                 end;

                 SendProcImpl (proc, decl.name);

              end;
           end;

           member := member.next;
        end;
     end;
End;

Procedure SendMethods (sect: TDeclSect);
Var  decl: TDecl;
     type_decl: TTypeDecl;
Begin
     decl := sect.first;
     while decl <> nil do begin

        { type declaration }
        if decl.tag = TypeDcl then begin
           type_decl := decl as TTypeDecl;
           if type_decl.typ.tag in [ClassTyp, ObjectTyp] then
              SendClassImpl (type_decl);
        end;

        decl := decl.next;
     end;
End;

Procedure SendSubroutines (sect: TDeclSect);
Var  decl: TDecl;
Begin
     decl := sect.first;
     while decl <> nil do begin

        { subroutines }
        if decl.tag = ProcDcl then
           SendProcImpl (decl as TProcDecl, '');

        decl := decl.next;
     end;
End;

(********************************* MODULE *********************************)

Const quo = '"';

Procedure SendIncl (fname, comment: string);
Begin
     Send ('#include ' + quo);
     Send (fname);
     Send (quo);
     SendComment (comment);
     SendEol;
End;

Procedure SendImports (sect: TImportSect);
Var  p: TImportItem;
Begin
     p := sect.first;
     while p <> nil do begin
        SendIncl (LowerCase (p.name) + '.h', p.comment);
        p := p.next;
     end;
End;

Procedure SendInfo (name, ext: string);
Begin
     Send ('/* ');
     Send (name);
     if ext <> '' then begin
        Send ('.');
        Send (ext);
     end;
     Send (' */');
     SendEol;
     SendEol;
End;

{--------------------------------------------------------------------------}

Const namespaces = true;

Procedure OpenNamespace (name: string);
Begin
     if namespaces then begin
        Send ('namespace ');
        Send (name);
        Send (' {');
        SendEol;
        SendEol;
     end;
End;

Procedure CloseNamespace (name: string);
Begin
     if namespaces then begin
        SendEol;
        Send ('}');
        Send (' // ');
        Send (name);
        SendEol;
        SendEol;
     end;
End;

Procedure UsingNamespace (name: string);
Begin
     if namespaces then begin
        Send ('using namespace ');
        Send (name);
        Send (';');
        SendEol;
     end;
End;

Procedure UsingNamespaces (sect: TImportSect);
Var  p: TImportItem;
Begin
     if sect <> nil then begin
        p := sect.first;
        while p <> nil do begin
           UsingNamespace (LowerCase (p.name));
           p := p.next;
        end;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendImpl (module: TModule);
Begin
     with module do begin
        SendDeclSect (impl_decl, global_mode);

        SendMethods (intf_decl);
        SendMethods (impl_decl);
        SendSubroutines (intf_decl);
     end;
End;

Procedure SendUnit (module: TModule);
Var  def: string;
Begin
     with module do begin

        { INTERFACE }

        SendInfo (name, 'h');
        if module.comment <> '' then begin
           SendComment (module.comment);
           SendEol;
        end;

        def := '__' + UpperCase (name) + '_H__';
        Send ('#ifndef ' + def);
        SendEol;
        Send ('#define ' + def);
        SendEol;
        SendLn ('');

        SendImports (intf_imports);
        SendLn ('');

        OpenNamespace (name);
        UsingNamespaces (intf_imports);
        if namespaces then SendLn ('');

        SendDeclSect (intf_decl, intf_mode);

        CloseNamespace (name);

        Send ('#endif /* ' + def + ' */');
        SendEol;
        SendLn ('');

        { IMPLEMENTATION }

        SendInfo (name, 'cc');

        SendImports (impl_imports);
        SendIncl (name + '.h', '');
        SendLn ('');

        OpenNamespace (name);
        UsingNamespaces (intf_imports);
        UsingNamespaces (impl_imports);
        if namespaces then SendLn ('');

        SendImpl (module);

        { !?
        if init <> nil then begin
           if finish <> nil then Send ('initialization')
                            else Send ('BEGIN');
           SendEol;
           IncIndent;
           SendStatSeq (init);
           DecIndent;
        end;

        if finish <> nil then begin
           Send ('finalization');
           SendEol;
           IncIndent;
           SendStatSeq ( finish);
           DecIndent;
        end;
        }

        CloseNamespace (name);
     end;
End;

Procedure SendModule (module: TModule);
Begin
     with module do begin
        SendInfo (name, 'cc');
        if comment <> '' then begin
           SendComment (comment);
           SendEol;
        end;

        SendImports (intf_imports);
        SendLn ('');

        OpenNamespace (name);
        UsingNamespaces (intf_imports);
        if namespaces then SendLn ('');

        SendDeclSect (intf_decl, global_mode);
        SendMethods (intf_decl);
        SendSubroutines (intf_decl);

        Send ('int main (int argc, char * * argv)');
        SendEol;

        SendLn ('{');
        IncIndent;
        SendStatSeq (init);
        DecIndent;
        SendLn ('}');

        CloseNamespace (name);
     end;
End;

Procedure SendCppModule (module: TModule);
Begin
     OpenOut;

     case module.kind of
        UnitMod:    SendUnit (module);
        ProgramMod: SendModule (module);
        LibraryMod: SendModule (module);
        else        Bug;
     end;

     CloseOut;
End;

(***************************************************************************)

Procedure SendCppCls (cls: TClsType);
Begin
     OpenOut;

     Assert (cls <> nil);
     SendLn ('');
     SendComment ('file: ' + cls.Name + '.ii');
     SendLn ('');
     SendLn ('');

     if cls.members <> nil then
        SendDeclSect_ClassMembers (cls.members);

     CloseOut;
End;

Procedure SendCppImpl (module: TModule);
Begin
     OpenOut;

     Assert (module <> nil);
     SendLn ('');
     SendComment ('file: ' + module.Name + '.ii');
     SendLn ('');
     SendLn ('');

     SendImpl (module);

     CloseOut;
End;

END.
