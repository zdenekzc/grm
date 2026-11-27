
(**************************************************************************)
(*                                                                        *)
(*                                Types                                   *)
(*                                                                        *)
(**************************************************************************)

UNIT Type0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     Expr0, Stat0;

Function SubroutineHead: TProcDecl;
Function TypeDef: TType;

IMPLEMENTATION

(**************************** TYPE IDENTIFIER *****************************)

Function TypeIdent: TAliasType;
Var  tmp: TExpr;
Begin
     tmp := SimpleExpr (); { <- problem s '=' }
     result := ExprToAlias (tmp);
End;

(******************************* PARAMETERS *******************************)

Function DefaultStringType: TStringType;
Begin
     result := TStringType.Create;
     result.lim := nil; { % long string }
End;

Function UntypedFileType: TFileType;
Begin
     result := TFileType.Create;
     result.elem := nil; { % untyped file element }
     result.untyped_file := true;
End;

Function ParamType: TType;
Begin
     if sy = StringSy then begin
        GetSymbol;
        result := DefaultStringType ();
     end
     else if sy = FileSy then begin
        GetSymbol;
        result := UntypedFileType;
     end
     else result := TypeIdent ();
End;

Procedure ParamIdent (sect: TParamSect);
Var  item: TParamItem;
Begin
     item := TParamItem.Create;
     item.name := Identifier ();
     sect.Add (item);
End;

Procedure ParameterDeclaration (sect: TParamSect);
Var mode:  TParamMode;
    start: TParamItem;
    typ:   TType;
    tmp:   TArrayType;
    ini:   TExpr;
    item:  TParamItem;
Begin
     { druh parametru }
     mode := ValueParam;
     if sy = VarSy then begin
        GetSymbol; { skip var }
        mode := VarParam;
     end
     else if sy = ConstSy then begin
        GetSymbol;
        mode := ConstParam;
     end
     else if sy = OutSy then begin
        GetSymbol;
        mode := OutParam;
     end;

     { posloupnost identifikatoru }
     ParamIdent (sect);
     start := sect.last; { prvni identifikator teto skupiny (ne cele sekce) }
     while sy = CommaSy do begin
        GetSymbol;
        ParamIdent (sect);
     end;

     typ := nil;
     ini := nil;

     { typ }
     if sy = ColonSy then begin
        GetSymbol; { dvojtecka }
        if sy = ArraySy then begin
           { open array }
           GetSymbol;
           CheckSymbol (OfSy);

           tmp := TArrayType.Create;
           tmp.open_array := true;
           tmp.index := nil; { % open array index }
           tmp.elem := ParamType ();

           typ := tmp;
        end
        else begin
           { normal type }
           typ := ParamType ();
        end;

        { initialization }
        if sy = EqualSy then begin
           GetSymbol;
           ini := Expression ();
        end;
     end
     else begin
        { untyped parameter }
        if mode = ValueParam then Error ('Missing parameter type');
        typ := nil; { % untyped parameter }
     end;

     { store mode, type, initialization }
     item := start;
     while item <> nil do begin
        item.mode := mode;
        item.typ := typ;
        item.ini := ini;
        item := item.next;
     end;
End;

Function FormalParameterList: TParamSect;
Begin
     result := TParamSect.Create;
     if sy = LParSy then begin
        GetSymbol; { leva zavorka }

        if sy <> RParSy then begin
           ParameterDeclaration (result);
           while sy = SemicolonSy do begin
              GetSymbol; { strednik }
              ParameterDeclaration (result);
           end;
        end;

        CheckSymbol (RParSy); { prava zavorka }
     end;
End;

Function PropertyParameterList: TParamSect;
Begin
     CheckSymbol (LBrackSy);

     result := TParamSect.Create;
     ParameterDeclaration (result);
     while sy = SemicolonSy do begin
        GetSymbol; { strednik }
        ParameterDeclaration (result);
     end;

     CheckSymbol (RBrackSy);
End;

(*************************** CALLING CONVETIONS ***************************)

Function GetCall: TCall;
Begin
     ConvDirective;
     case sy of
        RegisterSy: result := RegisterCall;
        PascalSy:   result := PascalCall;
        CdeclSy:    result := CdeclCall;
        StdcallSy:  result := StdcallCall;
        SafecallSy: result := SafecallCall;
        else        result := NoCall;
     end;
     if result <> NoCall then GetSymbol;
End;

(****************************** SUBROUTINES *******************************)

Const DirSet = [RegisterSy, PascalSy, CdeclSy, StdcallSy, SafecallSy,
                InlineSy, ReintroduceSy, OverloadSy,
                VirtualSy, DynamicSy, MessageSy, OverrideSy, AbstractSy];

Procedure SubrDirectives (decl: TProcDecl);
Var  old: TSymbol;
Begin
     ConvDirective;
     while sy in DirSet do begin
        old := sy;
        GetSymbol;

        case old of
           RegisterSy:    decl.call := RegisterCall;
           PascalSy:      decl.call := PascalCall;
           CdeclSy:       decl.call := CdeclCall;
           StdcallSy:     decl.call := StdcallCall;
           SafecallSy:    decl.call := SafecallCall;

           InlineSy:      decl.a_inline := true;
           ReintroduceSy: decl.a_reintroduce := true;
           OverloadSy:    decl.a_overload := true;

           VirtualSy:     decl.a_virtual := true;
           DynamicSy:     decl.a_dynamic := true;
           MessageSy:     decl.a_message := Expression ();
           OverrideSy:    decl.a_override := true;
           AbstractSy:    decl.a_abstract := true;
           else           Bug;
        end;

        CheckSymbol (SemicolonSy);
        ConvDirective;
     end;
End;

Function SubroutineHead: TProcDecl;
Var  decl: TProcDecl;
     id:   TIdent;
Begin
     decl := TProcDecl.Create;

     { subroutine heading }
     if sy = ClassSy then begin
        GetSymbol;
        decl.static_proc := true;
        case sy of
           ProcedureSy: decl.style := ProcedureStyle;
           FunctionSy:  decl.style := FunctionStyle;
           else         Error ('Procedure or function expected');
        end;
        GetSymbol;
     end
     else begin
        decl.static_proc := false;
        case sy of
           ProcedureSy:   decl.style := ProcedureStyle;
           FunctionSy:    decl.style := FunctionStyle;
           ConstructorSy: decl.style := ConstructorStyle;
           DestructorSy:  decl.style := DestructorStyle;
           else           Bug;
        end;
        GetSymbol;
     end;

     { identifier }
     id := Identifier ();
     if sy = PeriodSy then begin
        GetSymbol ();
        decl.context := id;
        decl.name := Identifier ();
     end
     else begin
        decl.name := id;
     end;

     { parameters }
     decl.param_list := FormalParameterList ();

     { result }
     if decl.style = FunctionStyle then begin
        CheckSymbol (ColonSy);
        decl.answer := ParamType ();
     end;

     CheckSymbol (SemicolonSy);
     SubrDirectives (decl);

     result := decl;
End;

(********************************* FIELDS *********************************)

Procedure FieldIdent (sect: TDeclSect);
Var  item: TVarDecl;
Begin
     item := TVarDecl.Create;
     item.name := Identifier ();
     sect.Add (item);
End;

Procedure FieldList (sect: TDeclSect; acs: TAccess);
Var  start: TDecl;
     item:  TVarDecl;
     typ:   TType;
Begin
     FieldIdent (sect);
     start := sect.last;

     while sy = CommaSy do begin
        GetSymbol;
        FieldIdent (sect);
     end;

     CheckSymbol (ColonSy);
     typ := TypeDef ();

     { store type }
     item := start as TVarDecl;
     while item <> nil do begin
        item.access := acs;
        item.typ := typ;
        item := item.next as TVarDecl;
     end;
End;

Procedure FieldDefinition (sect: TDeclSect; acs: TAccess);
Begin
     FieldList (sect, acs);
     CheckSymbol (SemicolonSy);
End;

(******************************** METHODS *********************************)

Procedure MethodDefinition (sect: TDeclSect; acs: TAccess);
Var  decl: TProcDecl;
Begin
     decl := SubroutineHead ();
     decl.access := acs;
     sect.Add (decl);
End;

(******************************* PROPERTIES *******************************)

Procedure InterfaceEntry (top: TInterfaceSect);
Var  item: TInterfaceItem;
Begin
     item := TInterfaceItem.Create;
     item.ifc := TypeIdent ();
     top.Add (item);
End;

Procedure PropertyDefinition (sect: TDeclSect; acs: TAccess);
Var  decl: TPropertyDecl;
Begin
     CheckSymbol (PropertySy);

     decl := TPropertyDecl.Create;
     sect.Add (decl);

     decl.access := acs;
     decl.name := Identifier ();

     if sy in [LBrackSy, ColonSy] then begin
        if sy = LBrackSy then
           decl.param_list := PropertyParameterList ();

        CheckSymbol (ColonSy);
        decl.typ := ParamType ();

        ConvDirective;
        if sy = IndexSy then begin
           GetSymbol;
           decl.index := Expression ();
        end;
     end;

     ConvDirective;
     if sy = ReadSy then begin
        GetSymbol;
        decl.a_read := QualIdent ();
     end;

     ConvDirective;
     if sy = WriteSy then begin
        GetSymbol;
        decl.a_write := QualIdent ();
     end;

     ConvDirective;
     if sy = StoredSy then begin
        GetSymbol;
        decl.a_stored := Expression ();
     end;

     ConvDirective;
     if sy = DefaultSy then begin
        GetSymbol;
        decl.a_default := Expression ();
     end
     else if sy = NodefaultSy then begin
        GetSymbol;
        decl.a_nodefault := true;
     end;

     ConvDirective;
     if sy = ImplementsSy then begin
        GetSymbol;

        decl.a_implements := TInterfaceSect.Create;
        InterfaceEntry (decl.a_implements);
        while sy = CommaSy do begin
           GetSymbol;
           InterfaceEntry (decl.a_implements);
        end;
     end;

     CheckSymbol (SemicolonSy);

     ConvDirective;
     if sy = DefaultSy then begin
        GetSymbol;
        decl.a_def_array := true;
        CheckSymbol (SemicolonSy);
     end;
End;

(******************************** FRIENDS *********************************)

Procedure FriendDefinition (sect: TFriendSect);
Var  item: TFriendItem;
Begin
     CheckSymbol (FriendSy);

     item := TFriendItem.Create;
     sect.Add (item);

     if sy = ClassSy then begin
        GetSymbol;
        item.cls := true;
     end;

     item.name := Identifier ();
     CheckSymbol (SemicolonSy);
End;

(********************************* CLASS **********************************)

Const MethodSet = [ProcedureSy, FunctionSy, ClassSy, ConstructorSy, DestructorSy];

Procedure ComponentList (cls: TClsType; acs: TAccess);
Var   stop: boolean;
Begin
     stop := false;
     repeat
        ConvClassDirective;  { nezbytne }
        if sy = IdentSy then FieldDefinition (cls.members, acs)
        else if sy in MethodSet then MethodDefinition (cls.members, acs)
        else if sy = PropertySy then PropertyDefinition (cls.members, acs)
        else if sy = FriendSy then FriendDefinition (cls.friends)
        else stop := true;
     until stop;

     ConvClassDirective; { nezbytne }
End;

Const AccessSet = [PrivateSy, ProtectedSy, PublicSy, PublishedSy, AutomatedSy];

Procedure ClassComponents (cls: TClsType);
Var   acs: TAccess;
Begin
     if not (sy in AccessSet) then
        ComponentList (cls, PublicAccess);

     while sy in AccessSet do begin
        case sy of
           PrivateSy:   acs := PrivateAccess;
           ProtectedSy: acs := ProtectedAccess;
           PublicSy:    acs := PublicAccess;
           PublishedSy: acs := PublishedAccess;
           AutomatedSy: acs := AutomatedAccess;
           else         Bug;
        end;
        GetSymbol;
        ComponentList (cls, acs);
     end;
End;

Procedure ClassBody (item: TClsType);
Begin
     item.ifc_list := TInterfaceSect.Create;

     { parent, interfaces }
     if sy = LParSy then begin
        GetSymbol;
        item.parent := TypeIdent ();

        while sy = CommaSy do begin
           GetSymbol;
           InterfaceEntry (item.ifc_list);
        end;

        CheckSymbol (RParSy);
     end;

     item.members := TDeclSect.Create;
     item.friends := TFriendSect.Create;

     if sy <> SemicolonSy then begin
        ClassComponents (item);
        CheckSymbol (EndSy);
     end;
End;

Function ClassType: TClassType;
Begin
     result := TClassType.Create;
     if sy = SemicolonSy then result.forw := true
                         else ClassBody (result);
End;

Function ClassOfType: TClassOfType;
Begin
     CheckSymbol (OfSy);
     result := TClassOfType.Create;
     result.elem := TypeIdent ();
End;

Function ClassDef: TType;
Begin
     CheckSymbol (ClassSy);
     if sy = OfSy then result := ClassOfType ()
                  else result := ClassType ();
End;

(********************************* OBJECT *********************************)

Function ObjectDef: TObjectType;
Begin
     CheckSymbol (ObjectSy);
     result := TObjectType.Create;
     if sy = SemicolonSy then result.forw := true
                         else ClassBody (result);
End;

(******************************* INTERFACE ********************************)

Function InterfaceDef: TInterfaceType;
Begin
     CheckSymbol (InterfaceSy);
     result := TInterfaceType.Create;
     if sy = SemicolonSy then result.forw := true
                         else ClassBody (result);
End;

(********************************* RECORD *********************************)

Function RecordDef: TRecordType;
Begin
     CheckSymbol (RecordSy);
     result := TRecordType.Create;
     result.fields := TDeclSect.Create;

     if sy = IdentSy then
        FieldList (result.fields, PublicAccess);

     while sy = SemicolonSy do begin
        GetSymbol;
        if sy = IdentSy then
           FieldList (result.fields, PublicAccess);
     end;

     CheckSymbol (EndSy);
End;

(********************************* ARRAY **********************************)

Function ArrayDef: TArrayType;
Var  last, tmp: TArrayType;
Begin
     CheckSymbol (ArraySy);
     result := TArrayType.Create;
     last := result;
     last := last; { compiler }

     if sy = LBrackSy then begin
        GetSymbol ();
        result.index := TypeDef ();

        while sy = CommaSy do begin
           GetSymbol;

           { new array type }
           tmp := TArrayType.Create;
           tmp.index := TypeDef ();

           { add new type }
           last.elem := tmp;
           last := tmp;
        end;

        CheckSymbol (RBrackSy);
     end
     else begin
        result.dynamic_array := true;
        result.index := nil; { % dynamic array index }
     end;

     CheckSymbol (OfSy);
     last.elem := TypeDef ();
End;

(******************************** POINTER *********************************)

Function PointerDef: TPointerType;
Begin
     CheckSymbol (ArrowSy);
     result := TPointerType.Create;
     result.elem := ParamType ();
End;

(********************************* STRING *********************************)

Function StringDef: TStringType;
Begin
     CheckSymbol (StringSy);

     if sy = LBrackSy then begin
        GetSymbol;

        result := TStringType.Create;
        result.name := ''; { konstruktor nastavi 'string' - vypis by vynechal [lim] }
        result.lim := Expression ();

        CheckSymbol (RBrackSy);
     end
     else result := DefaultStringType ();
End;

(********************************** SET ***********************************)

Function SetDef: TSetType;
Begin
     CheckSymbol (SetSy);
     CheckSymbol (OfSy);

     result := TSetType.Create;
     result.elem := TypeDef ();
End;

(********************************** FILE **********************************)

Function FileDef: TFileType;
Begin
     CheckSymbol (FileSy);

     if sy = OfSy then begin
        GetSymbol;
        result := TFileType.Create;
        result.elem := TypeDef ();
     end
     else begin
        result := UntypedFileType;
     end;
End;

(************************** PROCEDURE / FUNCTION **************************)

Procedure SubrOptions (item: TProcType);
Begin
     if sy = OfSy then begin
        GetSymbol;
        CheckSymbol (ObjectSy);
        item.of_object := true;
     end;

     item.call := GetCall ();
End;

Function ProcDef: TProcType;
Begin
     CheckSymbol (ProcedureSy);
     result := TProcType.Create;
     result.style := ProcedureStyle;
     result.param_list := FormalParameterList ();
     SubrOptions (result);
End;

Function FuncDef: TProcType;
Begin
     CheckSymbol (FunctionSy);
     result := TProcType.Create;
     result.style := FunctionStyle;
     result.param_list := FormalParameterList ();
     CheckSymbol (ColonSy);
     result.answer := ParamType ();
     SubrOptions (result);
End;

(**************************** ENUMERATED TYPE *****************************)

Procedure EnumIdent (sect: TEnumSect);
Var  item: TEnumItem;
Begin
     item := TEnumItem.Create;
     item.name := Identifier ();
     sect.Add (item);
End;

Function EnumDef: TEnumType;
Begin
     result := TEnumType.Create;
     CheckSymbol (LParSy);

     result.elements := TEnumSect.Create;
     EnumIdent (result.elements);

     while sy = CommaSy do begin
        GetSymbol ();
        EnumIdent (result.elements);
     end;

     CheckSymbol (RParSy);
End;

(******************************** SUBRANGE ********************************)

Function SubrangeDef (expr1, expr2: TExpr): TSubrangeType;
Begin
     result := TSubrangeType.Create;
     result.low := expr1;
     result.high := expr2;
End;

(****************************** SIMPLE TYPE *******************************)

Function OtherDef: TType;
Var  expr1, expr2: TExpr;
Begin
     if not (sy in ExprSet) then Error ('Type expected');
     expr1 := SimpleExpr (); { !? problem s inicializovanymi promennymi }

     if sy <> RangeSy then begin
         result := ExprToAlias (expr1);
     end
     else begin
        GetSymbol;
        expr2 := SimpleExpr (); { !? problem s inicializovanymi promennymi }
        result := SubrangeDef (expr1, expr2);
     end;
End;

(**************************** TYPE DEFINITIONS ****************************)

Function TypeDef: TType;
Begin
     { packed }
     if sy = PackedSy then GetSymbol;

     case sy of
        StringSy:        result := StringDef ();
        ArraySy:         result := ArrayDef ();
        SetSy:           result := SetDef ();
        FileSy:          result := FileDef ();
        RecordSy:        result := RecordDef ();
        ObjectSy:        result := ObjectDef ();
        ClassSy:         result := ClassDef ();
        InterfaceSy:     result := InterfaceDef ();
        ProcedureSy:     result := ProcDef ();
        FunctionSy:      result := FuncDef ();
        ArrowSy:         result := PointerDef ();
        LParSy:          result := EnumDef ();
        else             result := OtherDef ();
     end;
End;

END.
