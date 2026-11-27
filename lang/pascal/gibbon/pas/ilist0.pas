UNIT IList0;

INTERFACE

Uses SysUtils {func UpperCase},
     Fil0, Dir0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     List0;

Procedure SendInfoModule (module: TModule);

IMPLEMENTATION

Var class_id: string;
    max_len: integer;
    global_decl: TDeclSect;

(****************************** IDENTIFIERS *******************************)

Function ShortName (name: string): string;
Begin
     result := name;
     if result [1] = 'T' then
        result := copy (result, 2, length (result) - 1);
End;

Function ClassVar (name: string): string;
Begin
     result := ShortName (name) + 'Model';
End;

Function EnumVar (name: string): string;
Begin
     result := ShortName (name) + 'Enum';
End;

(******************************* EXPRESSION *******************************)

Function ExprToText (expr: TExpr): string;
Begin
     case expr.tag of
        IdentExp:    with expr as TIdentExpr do
                        result := ident;

        BinaryExp:   with expr as TBinaryExpr do
                        if kind = FieldExp then
                           result := ExprToText (left) + '.' + ExprToText (right)
                        else
                           result := '???';

        else         result := '???';
     end;
End;

Procedure SendExpr (expr: TExpr);
Begin
     Send (ExprToText (expr));
End;

(********************************** TYPE **********************************)

Function TypeName (typ: TType): string;
Begin
     case typ.tag of
        AliasTyp:  with typ as TAliasType do
                      result := ExprToText (qual_ident);

        StringTyp: result := 'string';

        else       result := typ.info;
     end;
End;

Procedure SendTypeName (typ: TType);
Begin
     Send (TypeName (typ));
End;

(********************************** LIST **********************************)

Var any: boolean;

    first_field,
    last_field,
    prev_field,
    next_field,
    up_field,

    first_prop,
    last_prop,
    prev_prop,
    next_prop,
    up_prop,

    link_method,
    insert_first_method,
    insert_last_method,
    insert_prev_method,
    insert_next_method,
    remove_method,
    remove_all_method: string;

    elem_type: TType;

Procedure Clear;
Begin
     first_field := '?';
     last_field := '?';
     prev_field := '?';
     next_field := '?';
     up_field := '?';

     first_prop := '?';
     last_prop := '?';
     prev_prop := '?';
     next_prop := '?';
     up_prop := '?';

     link_method := '?';
     insert_first_method := '?';
     insert_last_method := '?';
     insert_prev_method := '?';
     insert_next_method := '?';
     remove_method := '?';
     remove_all_method := '?';

     elem_type := nil;
End;

Function Prefix (const name, pref: string): boolean;
Begin
     result :=  UpperCase (copy (name, 1, length (pref))) = UpperCase (pref);
End;

Procedure Check (const name, prefix: string; var answer: string);
Begin
     if UpperCase (copy (name, 1, length (prefix))) = UpperCase (prefix)
        then begin
           answer := copy (name, length (prefix) + 1,
                                 length (name) - length (prefix));
           any := true;
        end;
End;

Procedure CheckField (name: string; typ: TType);
Begin
     any := false;

     Check (name, 'FFirst', first_field);
     Check (name, 'First', first_prop);

     if any then elem_type := typ;

     Check (name, 'FLast',  last_field);
     Check (name, 'FPrev',  prev_field);
     Check (name, 'FNext',  next_field);
     Check (name, 'FUp',    up_field);
     Check (name, 'FAbove', up_field);

     Check (name, 'Last',  last_prop);
     Check (name, 'Prev',  prev_prop);
     Check (name, 'Next',  next_prop);
     Check (name, 'Up',    up_prop);
     Check (name, 'Above', up_prop);
End;

Procedure CheckProperty (name: string);
Begin
     any := false;
     Check (name, 'First', first_prop);
     Check (name, 'Last',  last_prop);
     Check (name, 'Prev',  prev_prop);
     Check (name, 'Next',  next_prop);
     Check (name, 'Up',    up_prop);
     Check (name, 'Above', up_prop);
End;

Procedure CheckMethod (name: string);
Begin
     any := false;
     Check (name, 'Link',         link_method);
     Check (name, 'InsertFirst',  insert_first_method);
     Check (name, 'InsertLast',   insert_last_method);
     Check (name, 'InsertBefore', insert_prev_method);
     Check (name, 'InsertAfter',  insert_next_method);
     Check (name, 'InsertPrev',   insert_prev_method);
     Check (name, 'InsertNext',   insert_next_method);
     Check (name, 'RemoveAll',    remove_all_method);
     if not any then Check (name, 'Remove', remove_method);
End;

Procedure Sequence;
Begin
     if first_prop <> '?' then begin
        Send ('NewRel (');

        Send (class_id);
        Send(', ');

        Send(QuotedStr (''));
        Send(', ');

        Send(QuotedStr (''));
        Send(', ');

        (*
        Send (QuotedStr (up_prop));
        Send(', ');
        Send (QuotedStr (first_prop));
        Send(', ');
        Send (QuotedStr (remove_all_method));
        *)

        if elem_type <> nil then
           Send (ClassVar (TypeName (elem_type)))
        else
           Send ('???');

        Send (');');
        SendEol;
     end;
     Clear;
End;

(********************************** ENUM **********************************)

Procedure SendComment (txt: string);
Begin
     Send ('{ ');
     Send (txt);
     Send (' }');
     SendEol;
     SendLn ('');
End;

Procedure SendEnumSect (name: TIdent; sect: TEnumSect);
Var  item: TEnumItem;
Begin
     SendComment (name);

     Send (EnumVar (name));
     Send (' := NewEnum (');
     Send (QuotedStr (name));
     Send (');');
     SendEol;

     item := sect.first;
     while item <> nil do begin
        Send ('NewItem (');
        Send (QuotedStr (item.name));
        Send (', ');
        Send (QuotedStr (''));
        Send (');');
        SendEol;
        item := item.next;
     end;

     SendLn ('');
End;

Procedure SendEnumType (decl: TTypeDecl);
Begin
     if decl.typ.tag = EnumTyp then
        SendEnumSect (decl.name, (decl.typ as TEnumType).elements);
End;

Procedure SendEnums (sect: TDeclSect);
Var  item: TDecl;
Begin
     item := sect.first;
     while item <> nil do begin
        case item.tag of
           TypeDcl: SendEnumType (item as TTypeDecl);
        end;
        item := item.next;
     end;
End;

(********************************* CLASS **********************************)

Function IsForw (typ: TType): boolean;
Begin
     Assert (typ <> nil);
     result := (typ.tag = ClassTyp) and
               (typ as TClassType).forw;
End;

Function SearchType (id: TIdent): TTypeDecl;
Var  item: TDecl;
     decl: TTypeDecl;
Begin
     id := UpperCase (id);
     result := nil;

     Assert (global_decl <> nil);
     item := global_decl.first;

     while (result = nil) and (item <> nil) do begin
        if item.tag = TypeDcl then begin
           decl := item as TTypeDecl;

           if not IsForw (decl.typ) then
              if UpperCase (decl.name) = id then
                 result := decl;

        end;
        item := item.next;
     end;
End;

Procedure SendField (item: TVarDecl);
Var  txt: string;
     dcl: TTypeDecl;
Begin
     if Prefix (item.name, 'FFirst') then Sequence;

     CheckField (item.name, item.typ);

     if not any then begin
        Send ('NewFeature (');
        Send (class_id);
        Send (', ');
        Send (QuotedStr (item.name));
        Send (', ');

        if item.typ.tag = StringTyp then
           Send ('Str')
        else begin
           txt := TypeName (item.typ);
           dcl := SearchType (txt);
           if dcl = nil then begin
              txt := UpperCase (txt);
              if txt = 'BOOLEAN' then Send ('Bool')
              else if txt = 'INTEGER' then Send ('Int')
              else if txt = 'REAL' then Send ('Real')
              else if txt = 'TIDENT' then Send ('Str')
              else Send (QuotedStr (txt))
           end
           else if dcl.typ.tag = EnumTyp then
              Send (EnumVar (dcl.name))
           else if dcl.typ.tag = ClassTyp then begin
              Send ('Ref_Empty, ');
              Send (ClassVar (dcl.name))
           end
           else Send (QuotedStr (txt));
        end;

        Send (');');
        SendEol;
     end;
End;

Procedure PutProc (name: string);
Begin
     Send (name);
     Send (' (');
     Send (class_id);
     Send (');');
     SendEol;
End;

Procedure SendMethod (item: TProcDecl);
Begin
     CheckMethod (item.name);

     if UpperCase (item.name) = 'ADD' then
        PutProc ('NewAdd');
     if item.style = ConstructorStyle then
        PutProc ('NewCreate');
End;

Procedure SendProperty (item: TPropertyDecl);
Begin
     CheckProperty (item.name);
End;

Procedure SendMemberSect (sect: TDeclSect);
Var  item: TDecl;
Begin
     item := sect.first;
     while item <> nil do begin
        case item.tag of
           VarDcl:      SendField (item as TVarDecl);
           ProcDcl:     SendMethod (item as TProcDecl);
           PropertyDcl: SendProperty (item as TPropertyDecl);
        end;
        item := item.next;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SendClassType (name: TIdent; cls: TClassType);
Begin
     if not cls.forw then begin
        class_id := ClassVar (name);

        SendComment (ShortName (name));

        if cls.parent <> nil then begin
           Send ('SetSuper (');
           Send (class_id);
           Send (', ');
           Send (ClassVar (TypeName (cls.parent)));
           Send (');');
           SendEol;
        end;

        Clear;
        if cls.members <> nil then
           SendMemberSect (cls.members);
        Sequence;

        SendEol;
     end;
End;

(**************************** CALCULATE LENGTH ****************************)

Procedure CalcLength (sect: TDeclSect);
Var  item: TDecl;
     decl: TTypeDecl;
     len: integer;
Begin
     max_len := 0;

     item := sect.first;
     while item <> nil do begin
        if item.tag = TypeDcl then begin
           decl := item as TTypeDecl;
           if decl.typ.tag = ClassTyp then
              len := length (ClassVar (decl.name));
              if max_len < len then
                 max_len := len;
        end;
        item := item.next;
     end;
End;

Function Expand (txt: string; len: integer): string;
Begin
     while length (txt) < len do
        txt := txt + ' ';
     result := txt;
End;

(**************************** INITIALIZATIONS *****************************)

Procedure SendInitialization (decl: TTypeDecl);
Begin
     if decl.typ.tag = ClassTyp then
        if not IsForw (decl.typ) then begin
           Send (Expand (ClassVar (decl.name), max_len));
           Send (' := NewProgModel (');
           Send (QuotedStr (ShortName (decl.name)));
           Send (');');
           SendEol;
        end;
End;

Procedure SendInitializations (sect: TDeclSect);
Var  item: TDecl;
Begin
     CalcLength (sect);

     item := sect.first;
     while item <> nil do begin
        if item.tag = TypeDcl then
           SendInitialization (item as TTypeDecl);
        item := item.next;
     end;
End;

(****************************** DESCRIPTIONS ******************************)

Procedure SendDescription (decl: TTypeDecl);
Begin
     case decl.typ.tag of
        ClassTyp: SendClassType (decl.name, decl.typ as TClassType);
     end;
End;

Procedure SendDecriptions (sect: TDeclSect);
Var  item: TDecl;
Begin
     item := sect.first;
     while item <> nil do begin
        case item.tag of
           TypeDcl: SendDescription (item as TTypeDecl);
        end;
        item := item.next;
     end;
End;

(******************************* VARIABLES ********************************)

Procedure SendEnumVariables (sect: TDeclSect);
Var  item: TDecl;
     decl: TTypeDecl;
     any:  boolean;
Begin
     any := false;

     item := sect.first;
     while item <> nil do begin
        if item.tag = TypeDcl then begin
           decl := item as TTypeDecl;
           if decl.typ.tag = EnumTyp then begin

              if any then begin
                 Send (',');
                 SendEol;
              end;
              any := true;
              Send (EnumVar (decl.name));

           end;
        end;
        item := item.next;
     end;

     if any then begin
        Send (': TEnumType;');
        SendEol;
        SendLn ('');
     end;
End;

Procedure SendModelVariables (sect: TDeclSect);
Var  item: TDecl;
     decl: TTypeDecl;
     any:  boolean;
Begin
     any := false;

     item := sect.first;
     while item <> nil do begin
        if item.tag = TypeDcl then begin
           decl := item as TTypeDecl;
           if decl.typ.tag = ClassTyp then
              if not IsForw (decl.typ) then begin

                 if any then begin
                    Send (',');
                    SendEol;
                 end;
                 any := true;
                 Send (ClassVar (decl.name));

              end;
        end;
        item := item.next;
     end;

     if any then begin
        Send (': TModel;');
        SendEol;
        SendLn ('');
     end;
End;

(********************************* MODULE *********************************)

Procedure SendInfoModule (module: TModule);
Begin
     if module <> nil then begin
        OpenOut;
        global_decl := module.intf_decl;

        // SendLn ('Procedure TabCls;');
        SendLn ('Var');
        SetIndent (4);
        SendEnumVariables (module.intf_decl);
        SendModelVariables (module.intf_decl);
        SetIndent (0);

        SendLn ('Begin');
        SetIndent (5);
        SendLn ('');
        SendEnums (module.intf_decl);
        SendComment ('models');
        SendInitializations (module.intf_decl);
        SendLn ('');
        SendDecriptions (module.intf_decl);
        SetIndent (0);
        SendLn ('End;');

        CloseOut;
     end;
End;

END.
