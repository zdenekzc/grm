UNIT PList0;

INTERFACE

Uses // SysUtils,
     // Classes,
     Support {proc Translate},
     Fil0, Dir0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     List0;

Procedure SendPascalModule (module: TModule);

Procedure SendPascalCls (cls: TClsType);
Procedure SendPascalImpl (module: TModule);

IMPLEMENTATION

(******************************* EXPRESSION *******************************)

Procedure SendExpr (expr: TExpr); forward;

Procedure SendComment (comment: string);
Begin
     if comment <> '' then begin
        if not StartOfLine then Send (' ');
        Send ('{ ');
        Send (comment);
        Send (' }');
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendString (txt: string);
Const quo = '''';
Var   i: integer;
      c: char;
      inside: boolean;
      t: string; { bylo string [255] - delsi konstanty se orezaly }
Begin
     if txt = '' then t := quo + quo
     else begin
        t := '';
        inside := false;

        for i := 1 to length (txt) do begin
           c := txt[i];
           if ord (c) < 32 then begin
              if inside then begin
                 t := t + quo;
                 inside := false;
              end;
              t := t + '^' + chr (ord ('@') + ord (c));
           end
           else begin
              if not inside then begin
                 t := t + quo;
                 inside := true;
              end;
              if c = quo then t := t + quo + quo
                         else t := t + c;
           end;
        end; {for}

        if inside then t := t + quo;
     end; {if}

     Send (t);
End;

{--------------------------------------------------------------------------}

Procedure SendArgSect (sect: TArgSect);
Var  item: TArgItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     if item <> nil then begin


        if sect.long_params then begin
           SendEol;
           IncIndent;
           Send ('(');
           IncrIndent (1);
        end
        else Send (' (');

        while item <> nil do begin

           SendExpr (item.value);

           if item.width <> nil then begin
              Send (': ');
              SendExpr (item.width);
           end;

           if item.digits <> nil then begin
              Send (': ');
              SendExpr (item.digits);
           end;

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
     end;
End;

Procedure SendInxSect (sect: TInxSect);
Var  item: TInxItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        SendExpr (item.value);
        if item.next <> nil then Send (', ');
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
           Send (' .. ');
           SendExpr (item.high);
        end;
        if item.next <> nil then Send (', ');
        item := item.next;
     end;
End;

Procedure SendStructSect (sect: TStructSect);
Var  item: TStructItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     Send ('(');
     while item <> nil do begin

        if item.name <> '' then begin
           Send (item.name);
           Send (': ');
        end;

        SendExpr (item.value);

        if item.next <> nil then
           if sect.arr then Send (', ')
                       else Send ('; ');

        item := item.next;
     end;
     Send (')');
End;

{--------------------------------------------------------------------------}

Procedure SendBinaryExpr (expr: TBinaryExpr);
Var  txt: string;
     space: boolean;
Begin
     with expr do begin

        case kind of
           MulExp:  txt := '*';
           RDivExp: txt := '/';
           DivExp:  txt := 'div';
           ModExp:  txt := 'mod';
           AndExp:  txt := 'and';
           ShlExp:  txt := 'shl';
           ShrExp:  txt := 'shr';
           AsExp:   txt := 'as';

           AddExp:  txt := '+';
           SubExp:  txt := '-';
           OrExp:   txt := 'or';
           XorExp:  txt := 'xor';

           EqExp:   txt := '=';
           NeExp:   txt := '<>';
           LtExp:   txt := '<';
           GtExp:   txt := '>';
           LeExp:   txt := '<=';
           GeExp:   txt := '>=';
           InExp:   txt := 'in';
           IsExp:   txt := 'is';

           FieldExp:     txt := '.';
           PtrFieldExp:  txt := '->';

           MemberExp:    txt := '.*';
           PtrMemberExp: txt := '->*';

           BitAndExp:  txt := 'and';
           BitOrExp:   txt := 'or';
           BitXorExp:  txt := 'xor';

           LogAndExp:  txt := 'and';
           LogOrExp:   txt := ' or ';

           else     Bug;
        end;

        space := not (kind in [FieldExp, PtrFieldExp, MemberExp, PtrMemberExp]);

        SendExpr (left);
        if space then Send (' ');
        Send (txt);
        if space then Send (' ');
        SendExpr (right);
     end;
End;

Procedure SendUnaryExpr (expr: TUnaryExpr);
Var  txt: string;
Begin
     with expr do begin
        case kind of
           NotExp:   txt := 'not';
           PlusExp:  txt := '+';
           MinusExp: txt := '-';
           AdrExp:   txt := '@';
           DerefExp: txt := '';

           ParExp:    txt := '(';
           LogNotExp: txt := 'not';
           BitNotExp: txt := 'not';
           else Bug;
        end;
        if txt <> '' then begin
           Send (txt);
           Send (' ');
        end;

        if param <> nil then SendExpr (param);

        case kind of
           ParExp:   txt := ')';
           DerefExp: txt := '^';
           else      txt := '';
        end;
        if txt <> '' then begin
           Send (' ');
           Send (txt);
        end;
     end;
End;

Procedure SendExpr (expr: TExpr);
Begin
     Assert (expr <> nil);

     case expr.tag of
        BinaryExp:   SendBinaryExpr (expr as TBinaryExpr);
        UnaryExp:    SendUnaryExpr (expr as TUnaryExpr);

        ValueExp:    with expr as TValueExpr do
                        if kind = StrValueExp then SendString (value) { lex0 uklada text bez apostrofu }
                                              else Send (value);

        IdentExp:    with expr as TIdentExpr do
                        Send (ident);

        IndexExp:    with expr as TIndexExpr do begin
                        SendExpr (left);
                        Send ('[');
                        SendInxSect (list);
                        Send (']');
                     end;

        CallExp:     with expr as TCallExpr do begin
                        SendExpr (func);
                        SendArgSect (list);
                     end;

        SetExp:      with expr as TSetExpr do begin
                        Send ('[');
                        SendElemSect (list);
                        Send (']');
                     end;

        StructExp:   with expr as TStructExpr do
                        SendStructSect (list);

        NilExp:      Send ('nil');

        StringExp:   with expr as TStringExpr do begin
                        Send ('string');
                        if param <> nil then begin
                           Send (' (');
                           SendExpr (param);
                           Send (')');
                        end;
                     end;

        SuperExp:    with expr as TSuperExpr do begin
                        Send ('inherited ');
                        if ident <> '' then Send (ident);
                     end;

        ThisExp:     Send ('self');

        TextExp:     with expr as TTextExpr do
                        Send (text);

        else         Bug;
     end;
End;

(******************************* STATEMENT ********************************)

Procedure SendStat (stat: TStat); forward;
Procedure SendType (typ: TType); forward;
Procedure SendTypeName (typ: TType); forward;

{--------------------------------------------------------------------------}

Procedure SendCaseSect (sect: TCaseSect);
Var  item: TCaseItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        SendElemSect (item.sel_list);
        Send (': ');
        SendEol;

        IncIndent;
        SendStat (item.sel_stat);
        Send (';');
        SendEol;
        DecIndent;

        item := item.next;
     end;
End;

Procedure SendWithSect (sect: TWithSect);
Var  item: TWithItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        SendExpr (item.expr);
        if item.next <> nil then Send (', ');
        item := item.next;
     end;
End;

Procedure SendOnSect (sect: TOnSect);
Var  item: TOnItem;
Begin
     Assert (sect <> nil);
     item := sect.first;

     while item <> nil do begin
        Send ('on ');

        if item.on_ident <> '' then begin
           Send (item.on_ident);
           Send (': ');
        end;

        SendTypeName (item.on_type);
        Send (' do');   { chybela mezera }
        SendEol;

        IncIndent;
        SendStat (item.body_stat);
        Send (';');     { strednik za polozkou on }
        SendEol;
        DecIndent;

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
           if (stat.next <> nil) or not (stat as TTextStat).optional then begin
              SendStat (stat);
              SendEol;
           end;
        end
        else if stat.tag <> EmptySt then begin
           SendStat (stat);
           if stat.tag <> GroupSt then Send (';');
           if stat.tag <> GroupSt then SendEol;
        end;
        stat := stat.next;
     end;
End;

Procedure SendInnerStat (stat: TStat);
Begin
     if stat.tag = CompoundSt then begin
        Send (' '); { pokracovani radku }
        SendStat (stat);
     end
     else begin
        SendEol;
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
                       Send (' := ');
                       SendExpr (right_expr);
                    end;

        CallSt:     with stat as TCallStat do
                       SendExpr (call_expr);

        CompoundSt: with stat as TCompoundStat do begin
                       Send ('begin');
                       SendEol;
                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;
                       Send ('end');
                    end;

        GotoSt:     with stat as TGotoStat do begin
                       Send ('goto ');
                       Send (goto_lab);
                    end;

        IfSt:       with stat as TIfStat do begin
                       Send ('if ');
                       SendExpr (cond_expr);
                       Send (' then');
                       SendInnerStat (then_stat);

                       if else_stat <> nil then begin
                          SendEol;
                          Send ('else');
                          SendInnerStat (else_stat);
                       end;
                    end;

        CaseSt:     with stat as TCaseStat do begin
                       Send ('case ');
                       SendExpr (case_expr);
                       Send (' of');   { bylo ' do' }
                       SendEol;

                       IncIndent;
                       SendCaseSect (case_list);
                       DecIndent;

                       if else_seq <> nil then begin
                          SendEol;
                          Send ('else');
                          SendEol;

                          IncIndent;
                          SendStatSeq (else_seq);
                          DecIndent;
                       end;
                       Send ('end');
                    end;

        WhileSt:    with stat as TWhileStat do begin
                       Send ('while ');
                       SendExpr (cond_expr);
                       Send (' do');
                       SendInnerStat (body_stat);
                    end;

        RepeatSt:   with stat as TRepeatStat do begin
                       Send ('repeat');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('until ');   { chybela mezera }
                       SendExpr (until_expr);
                    end;

        ForSt:      with stat as TForStat do begin
                       Send ('for ');
                       SendExpr (var_expr);
                       Send (' := ');
                       SendExpr (from_expr);
                       if incr then Send (' to ')
                               else Send (' downto ');
                       SendExpr (to_expr);
                       Send (' do');
                       SendInnerStat (body_stat);
                    end;

        WithSt:     with stat as TWithStat do begin
                       Send ('with ');
                       SendWithSect (with_list);
                       Send (' do');
                       SendEol;

                       IncIndent;
                       SendStat (body_stat);
                       DecIndent;
                    end;

        RaiseSt:    with stat as TRaiseStat do begin
                       Send ('raise');
                       if raise_expr <> nil then begin
                          Send (' ');
                          SendExpr (raise_expr);
                       end;
                    end;

        FinallySt:  with stat as TFinallyStat do begin
                       Send ('try');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('finally');
                       SendEol;

                       IncIndent;
                       SendStatSeq (finally_seq);
                       DecIndent;
                       Send ('end');
                    end;

        ExceptSt:   with stat as TExceptStat do begin
                       Send ('try');
                       SendEol;

                       IncIndent;
                       SendStatSeq (body_seq);
                       DecIndent;

                       Send ('except');
                       SendEol;

                       IncIndent;
                       SendOnSect (on_list);
                       DecIndent;

                       if else_seq <> nil then begin
                          if on_list.first <> nil then begin
                             Send ('else');
                             SendEol;
                          end;

                          IncIndent;
                          SendStatSeq (else_seq);
                          DecIndent;
                       end;

                       Send ('end');
                    end;

        TextSt:     with stat as TTextStat do
                       Send (text);

        GroupSt:    with stat as TGroupStat do
                       SendStatSeq (body_seq);

        LabeledSt:  with stat as TLabeledStat do begin
                       SendExpr (label_expr);
                       Send (': ');
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
     Send ('(');

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

     Send (')');
     DecIndent;
End;

Procedure SendParameters (sect: TParamSect);
Var  item: TParamItem;
Begin
     if (sect <> nil) and (sect.first <> nil) then begin

        (*
        lim := 0;
        item := sect.first;
        while item <> nil do begin
           i := length (item.name);

           case item.mode of
              ValueParam: { nothing } ;
              VarParam:   inc (i, 4);
              ConstParam: inc (i, 6);
              OutParam:   inc (i, 4);
           end;

           if i > lim then i := lim;
           item := item.next
        end;
        *)

        if sect.long_params then begin
           SendEol;
           IncrIndent (10);
           Send ('(');
           IncrIndent (1);
        end
        else Send (' (');

        item := sect.first;
        while item <> nil do begin

           case item.mode of
              ValueParam: { nothing } ;
              VarParam:   Send ('var ');
              ConstParam: Send ('const ');
              OutParam:   Send ('out ');
              else        Bug;
           end;

           Send (item.name);

           while (item.next <> nil) and
                 (item.mode = item.next.mode) and
                 (item.typ = item.next.typ) do
           begin
              item := item.next;
              Send (', ');
              Send (item.name);
           end;

           if item.typ <> nil then begin
              Send (': ');
              SendTypeName (item.typ);
           end;

           if item.ini <> nil then begin
              Send (' = ');
              SendExpr (item.ini);
           end;

           if item.next <> nil then begin
              Send (';');
              if sect.long_params then SendEol
                                  else Send (' ');
           end;
           item := item.next;
        end;

        Send (')');
        if sect.long_params then DecrIndent (11);
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
           Send (' (');
           if parent <> nil then begin
              SendTypeName (parent);
              if any_ifc then Send (', ');
           end;
           if any_ifc then SendInterfaceSect (ifc_list);
           Send (')');
        end;

        SendComment (comment); { !? komentar typu }

        if not forw then begin
           SendEol;
           if members <> nil then
              SendDeclSect_ClassMembers (members);
           Send ('end');
        end;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendCall (call: TCall);
Begin
     case call of
        RegisterCall: Send (' register');
        PascalCall:   Send (' pascal');
        CdeclCall:    Send (' cdecl');
        StdcallCall:  Send (' stdcall');
        SafecallCall: Send (' safecall');
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
                          SendExpr (low);
                          Send ('..');
                          SendExpr (high);
                       end;

        EnumTyp:       with typ as TEnumType do begin
                          SendComment (comment); { !? komentar typu }
                          SendEnumSect (elements);
                       end;

        StringTyp:     with typ as TStringType do begin
                          Send ('string');
                          if lim <> nil then begin
                             Send (' [');
                             SendExpr (lim);
                             Send (']');
                          end;
                       end;

        ArrayTyp:      with typ as TArrayType do begin
                          Send ('array ');
                          if not dynamic_array and not open_array then begin
                             Send ('[');
                             SendTypeName (index);
                             Send ('] ');
                          end;
                          Send ('of ');
                          SendTypeName (elem);
                       end;

        RecordTyp:     with typ as TRecordType do begin
                          Send ('record');
                          SendEol;
                          IncIndent;
                          SendDeclSect (fields, member_mode);
                          DecIndent;
                          Send ('end');
                       end;

        PointerTyp:    with typ as TPointerType do begin
                          Send ('^ ');
                          SendTypeName (elem);
                       end;

        SetTyp:        with typ as TSetType do begin
                          Send ('set of ');
                          if elem <> nil then SendTypeName (elem);
                       end;

        FileTyp:       with typ as TFileType do begin
                          Send ('file');
                          if not untyped_file then begin
                             Send (' of ');
                             SendTypeName (elem);
                          end;
                       end;


        ObjectTyp,
        ClassTyp,
        InterfaceTyp:  SendClsType (typ as TClsType);

        ClassOfTyp:    with typ as TClassOfType do begin
                          Send ('class of ');
                          SendTypeName (elem);
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
     Send ('label ');
     Send (decl.name);
     SendComment (decl.comment);
     Send (';');
     SendEol;
End;

Procedure SendConstDecl (decl: TConstDecl);
Begin
     Send (decl.name);
     if decl.typ <> nil then begin
        Send (': ');
        SendTypeName (decl.typ);
     end;
     Send (' = ');
     SendExpr (decl.val);
     Send (';');
     SendComment (decl.comment);
     SendEol;
End;

Procedure SendTypeDecl (decl: TTypeDecl);
Begin
     Send (decl.name);
     Send (' = ');
     SendType (decl.typ);
     Send (';');
     SendComment (decl.comment); { !? u tridy a vyctoveho typu by se mohl opakovat }
     SendEol;
End;

Procedure SendVarDecl (decl: TVarDecl);
Begin
     Send (decl.name);

     Send (': ');
     SendTypeName (decl.typ);

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
Var  txt: string;
     p_uppercase: boolean;
Begin
     with decl do begin
        // writeln ('SendProcDecl ', context, '.', name); { !? debug }

        p_uppercase := mode in [intf_mode, global_mode];

        if (style = ProcedureStyle) and (answer <> nil) then
           style := FunctionStyle;

        if static_proc then begin
           txt := 'class ';
           if p_uppercase then txt[1] := UpCase (txt[1]);
           p_uppercase := false;
           Send (txt);
        end;

        case style of
           ProcedureStyle:   txt := 'procedure ';
           FunctionStyle:    txt := 'function ';
           ConstructorStyle: txt := 'constructor ';
           DestructorStyle:  txt := 'destructor ';
           else              Bug;
        end;
        if p_uppercase then txt[1] := UpCase (txt[1]);
        Send (txt);

        if mode = global_mode then
           if context <> '' then
              p_context := context;

        if p_context <> '' then begin
           Send (p_context);
           Send ('.');
        end;

        Send (name);

        SendParameters (param_list);

        if answer <> nil then begin
           Send (': ');
           SendTypeName (answer);
        end;

        Send (';');

        { directives }
        if call <> NoCall then begin
           SendCall (call);
           Send (';');
        end;

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

        if mode = member_mode then begin
           if a_virtual then Send (' virtual;');
           if a_dynamic then Send (' dynamic;');
           if a_override then Send (' override;');
           if a_abstract then Send (' abstract;');
           // if a_inline then Send (' inline;'); { !? not supported by FPC }
        end;

        SendComment (comment);
        SendEol;

        { procedure body - forward a external nemaji telo
          (konstruktor TProcDecl vytvari prazdne Body, vypsalo by se Begin End;) }
        if (mode in [global_mode, local_mode]) and
           not a_forward and not a_external then begin

           if local <> nil then
              SendDeclSect (local, local_mode);

           if body <> nil then begin
              Send ('Begin');
              SendEol;
              IncrIndent (5);
              SendStatSeq (body);
              DecrIndent (5);
              Send ('End');
              Send (';');
              SendEol;
           end;

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
Var  delta: integer;
     start: boolean;
     stop:  boolean;
Begin
     delta := 0;
     if mode <> member_mode then begin

        start := (decl.prev = nil) or
                 (decl.prev.tag <> decl.tag);

        if start then begin
           if false and (mode = local_mode) then
              case decl.tag of
                 ConstDcl: Send ('const ');
                 TypeDcl:  Send ('type ');
                 VarDcl:   Send ('var ');
              end
           else
              case decl.tag of
                 ConstDcl: Send ('Const ');
                 TypeDcl:  Send ('Type ');
                 VarDcl:   Send ('Var ');
              end;
        end;

        case decl.tag of
           ConstDcl: delta := 6;
           TypeDcl:  delta := 5;
           VarDcl:   delta := 4;
        end;
     end;

     if (mode = local_mode) and (decl.tag = ProcDcl) then
        delta := 3;

     IncrIndent (delta);
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
     DecrIndent (delta);

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

Function HasForwardClass (sect: TDeclSect; const p_name: string): boolean;
{ sekce uz obsahuje doprednou deklaraci tridy (napr. z parsovaneho zdrojaku) }
Var  decl: TDecl;
     typ:  TType;
Begin
     result := false;
     decl := sect.first;
     while (decl <> nil) and not result do begin
        if (decl.tag = TypeDcl) and (decl.name = p_name) then begin
           typ := (decl as TTypeDecl).typ;
           result := (typ <> nil) and (typ.tag = ClassTyp) and (typ as TClsType).forw;
        end;
        decl := decl.next;
     end;
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
              if not HasForwardClass (sect, tmp.name) then
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
        PrivateAccess:   Send ('private');
        ProtectedAccess: Send ('protected');
        PublicAccess:    Send ('public');
        PublishedAccess: Send ('published');
        AutomatedAccess: Send ('automated');
        else             Bug;
     end;
     SendEol;
End;

Procedure SendDeclSect_ClassMembers (sect: TDeclSect);
Var  item: TDecl;
     prev: TAccess;
     any:  boolean;
     after_methods: boolean; { v aktualni sekci uz byla metoda nebo property }
Begin
     sect.Sort;

     any := false;
     after_methods := false;
     item := sect.first;

     while item <> nil do begin

        { promenna za metodou/property vyzaduje novou specifikaci pristupu }
        if not any or (item.access <> prev) or
           (item.tag = VarDcl) and after_methods then
           if item.tag <> TextDcl then begin
              SendAccess (item.access);
              any := true;
              prev := item.access;
              after_methods := false;
           end;

        if item.tag in [ProcDcl, PropertyDcl] then
           after_methods := true;

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
// Var  line: TLine;
//      lines: TOutputLines;
Begin
     if not proc.skip_impl then begin
        if proc.comment_impl then SendLn ('(*');

        (*
        if proc.sect <> nil then begin
           lines := TOutputLines.Create;
           Translate (proc.sect, lines, proc.dict);

           line := lines.first;
           while line <> nil do begin
              SendLn (line.Value);
              line := line.next;
           end;

           lines.Free;
        end
        else begin
           SendProcDecl (proc, p_context, global_mode);
        end;
        *)

        SendProcDecl (proc, p_context, global_mode);

        if proc.comment_impl then SendLn ('*)');
        SendLn ('');
     end;
End;

Procedure SendClassImpl (decl: TTypeDecl);
Var  cls:    TClsType;
     member: TDecl;
     proc:   TProcDecl;
     any:    boolean;
Begin
     // writeln ('SendClassImpl ', decl.name); { !? debug }
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
                    Send ('{ ');
                    Send (decl.name);
                    Send (' }');
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

{--------------------------------------------------------------------------}

(*
Procedure SortDecl (sect: TDeclSect);
Const min = -1;
      max =  4;
Var   decl, nxt, start, stop: TDecl;
      inx: integer;
      first, last: array [min..max] of TDecl;
Begin
     if sect.first <> nil then begin

        { inicializace tabulek }
        for inx := min to max do begin
           first[inx] := nil;
           last[inx] := nil;
        end;

        { rozdeleni posloupnosti }
        decl := sect.first;
        while decl <> nil do begin
           inx := decl.level;

           { uloz zacatek }
           if first[inx] = nil then begin
              Assert (last[inx] = nil);
              first[inx] := decl;
              decl.prev := nil;
           end
           else begin
              Assert (last[inx] <> nil);
              last[inx].next := decl;
              decl.prev := last[inx];
           end;

           { nalezni posledni se stejnou prioritou }
           nxt := decl.next;
           while (nxt <> nil) and (nxt.level = inx) do
              decl := nxt;
              nxt := nxt.next;
           end;

           Assert (decl <> nil);
           Assert (decl.level = inx);

           { uloz konec }
           last[inx] := decl;
           decl.next := nil;
           if nxt <> nil then nxt.prev := nil;

           decl := nxt;
        end;

        { sestav vyslednou posloupnost }
        start := nil;
        stop := nil;

        for inx := min to max do begin
           if first[inx] <> nil then begin
              Assert (last[inx] <> nil);
              if start = nil then begin
                 Assert (stop = nil);
                 start := first[inx];
              end
              else begin
                 Assert (stop <> nil);
                 stop.next := first[inx];
                 first[inx].prev := stop
              end;
              stop := last [inx];
           end;
        end;

        Assert (start <> nil);
        Assert (start.prev = nil);
        Assert (stop <> nil);
        Assert (stop.next = nil);

        sect.first := start;
        sect.last := stop;
     end;
End;
*)

{--------------------------------------------------------------------------}

Procedure SendExportsSect (sect: TExportsSect);
Var  item: TExportsItem;
Begin
     Send ('exports');
     SendEol;
     IncIndent;

     item := sect.first;
     while item <> nil do begin
        Send (item.name);
        Send (' ');

        if item.e_index <> nil then begin
           Send (' index ');
           SendExpr (item.e_index);
        end;

        if item.e_name <> nil then begin
           Send (' name ');
           SendExpr (item.e_name);
        end;

        if item.next <> nil then Send (',')
                            else Send (';');
        SendEol;
        item := item.next;
     end;

     DecIndent;
End;

(********************************* MODULE *********************************)

Procedure SendImports (sect: TImportSect);
Var  p: TImportItem;
Begin
     if (sect <> nil) and (sect.first <> nil) then begin
        Send ('Uses ');
        IncrIndent (5);

        p := sect.first;
        while p <> nil do begin
           Send (p.name);
           SendComment (p.comment);
           if p.next <> nil then begin
              Send (', ');
              SendEol;
           end;
           p := p.next;
        end;

        Send (';');
        SendEol;

        DecrIndent (5);
        SendLn ('');
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
Begin
     with module do begin
        Send ('UNIT ');
        Send (name);
        Send (';');
        SendComment (module.comment);
        SendEol;
        SendLn ('');

        Send ('INTERFACE');
        SendEol;
        SendLn ('');
        SendImports (intf_imports);
        SendDeclSect (intf_decl, intf_mode);

        Send ('IMPLEMENTATION');
        SendEol;
        SendLn ('');
        SendImports (impl_imports);

        SendImpl (module);

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

        Send ('END.');
        SendEol;
     end;
End;

Procedure SendBlock (module: TModule);
Begin
     with module do begin
        SendImports (intf_imports);
        SendDeclSect (intf_decl, global_mode);
        SendMethods (intf_decl);
        SendSubroutines (intf_decl);

        Send ('BEGIN');
        SendEol;
        IncIndent;
        SendStatSeq (init);
        DecIndent;
        Send ('END.');
        SendEol;
     end;
End;

Procedure SendProgram (module: TModule);
Begin
     with module do begin
        Send ('PROGRAM ');
        Send (name);
        Send (';');
        SendComment (comment);
        SendEol;
        SendLn ('');

        SendBlock (module);
     end;
End;

Procedure SendLibrary (module: TModule);
Begin
     with module do begin
        Send ('LIBRARY ');
        Send (name);
        Send (';');
        SendComment (comment);
        SendEol;
        SendLn ('');

        SendBlock (module);
     end;
End;

Procedure SendPascalModule (module: TModule);
Begin
     OpenOut;

     case module.kind of
        UnitMod:    SendUnit (module);
        ProgramMod: SendProgram (module);
        LibraryMod: SendLibrary (module);
        else        Bug;
     end;

     CloseOut;
End;

(***************************************************************************)

Procedure SendPascalCls (cls: TClsType);
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

Procedure SendPascalImpl (module: TModule);
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
