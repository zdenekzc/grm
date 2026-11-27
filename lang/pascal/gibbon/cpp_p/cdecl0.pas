
(**************************************************************************)
(*                                                                        *)
(*                                Types                                   *)
(*                                                                        *)
(**************************************************************************)

UNIT CDecl0;

INTERFACE

Uses Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     Expr0, Stat0;

Function TypeDef: TType;

IMPLEMENTATION

(****************************** DECLARATIONS ******************************)

Const DeclSpecSet =
      [ FriendSy, TypedefSy,
        AutoSy, RegisterSy, StaticSy, ExternSy,
        InlineSy, VirtualSy,
        ConstSy, VolatileSy,
        ClassSy, StructSy, UnionSy,
        EnumSy,
        CharSy, ShortSy, IntSy, LongSy,
        SignedSy, UnsignedSy,
        FloatSy, DoubleSy,
        VoidSy ];

Function DeclSpecifier: TType;
Begin
     if sy = FriendSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = TypedefSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = AutoSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = RegisterSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = StaticSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = ExternSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = InlineSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = VirtualSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = ConstSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = VolatileSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = ClassSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = StructSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = UnionSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = EnumSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = CharSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = ShortSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = IntSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = LongSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = SignedSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = UnsignedSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = FloatSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = DoubleSy then begin
        GetSymbol;
        { !? }
     end

     else if sy = VoidSy then begin
        GetSymbol;
        { !? }
     end

     else Bug {!?}
End;

Function Declaration: TDecl;
Begin
     if sy = AsmSy then
     else if sy = ExternSy then
     else if sy = TemplateSy then
     else begin

        while sy in DeclSpecSet do
           DeclSpecifier ();

        while sy <> SemicolonSy do
           Declarator ();

        CheckSymbol (SemicolonSy); { !? }
     end;
End;

(****************************** DECLARATORS *******************************)

Function PtrDeclarator: TPtrType;
Var  tmp: TPtrType;
Begin
     result := nil; {!?}
     while sy in [AsteriskSy, AndSy] do begin

        tmp := result;
        if sy = AsteriskSy
           then result := TPointerType.Create;
           else result := TReferenceType.Create;
        GetSymbol;
        result.elem := tmp;

        while sy in [ConstSy, VolatileSy] do begin
           if sy = ConstSy then result.const_spec := true
                           else result.volatile.spec := true;
           GetSymbol;
        end;
     end;
End;

Function FunctionDeclarator: TFunctionType;
Begin
     CheckSymbol (LParSy);

     result := TFunctionType.Create;

     while sy <> RParSy do begin
        { !? }
     end;

     CheckSymbol (RParSy);

     while sy in [ConstSy, VolatileSy] do begin
        if sy = ConstSy then result.const_spec := true
                        else result.volatile.spec := true;
        GetSymbol;
     end;
End;

Function ArrayDeclarator: TArrayType;
Begin
     CheckSymbol (LBrackSy);

     result := TArrayType.Create;
     result.limit := ConstExpr ();

     CheckSymbol (RBrackSy);
End;

Function Declarator;
Begin
     if sy in [AsteriskSy, AndSy] then
        PtrDeclarator ();

     if sy = IdentSy then begin
        name := Identifier (); {!?}
        while sy in [LParSy, LBrackSy] do begin
           if sy = LParSy then
              result := FunctionDeclarator ();
           else
              result := ArrayDeclarator ();
        end;
     end

     else if sy = LPar then begin

     end

     else Error ('Invalid declarator');
End;

(******************************* PARAMETERS *******************************)

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
     typ := nil;
     ini := nil;

     { initialization }
     if sy = EqualSy then begin
        GetSymbol;
        ini := Expression ();
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
     CheckSymbol (LParSym); { leva zavorka }

        if sy <> RParSy then begin
           ParameterDeclaration (result);

           while sy = CommaSy do begin
              GetSymbol; { carka }
              ParameterDeclaration (result);
           end;
        end;

     CheckSymbol (RParSy); { prava zavorka }
End;

(********************************* CLASS **********************************)

Const AccessSet = [PrivateSy, ProtectedSy, PublicSy];

Procedure MemberDeclarator (cls: TClsType; acs: TAccess; spec: TDeclSpec);
Begin
     Declarator (); {!?}

     if sy = EqualSy then begin
        GetSymbol;
        init := ConstExpr (); {!?}
     end
     else if sy = ColonSy then begin
        GetSymbol;
        offset := ConstExpr (); {!?}
     end;
End;

Procedure ClassComponents (cls: TClsType);
Var  acs: TAccess;
Begin
     acs :=  PublicAccess; { !? }

     while sy <> RBraceSy do begin

        if sy in AccessSet do begin
           case sy of
              PrivateSy:   acs := PrivateAccess;
              ProtectedSy: acs := ProtectedAccess;
              PublicSy:    acs := PublicAccess;
              else         Bug;
           end;
           GetSymbol;
           CheckSymbol (ColonSy);
        end
        else begin
           spec := DeclSpecifiers ();
           if sy <> SemicolonSy then begin
              MemberDeclarator (cls, acs, spec);
              while sy = CommaSy do begin
                 GetSymbol ();
                 MemberDeclarator (cls, acs, spec);
              end;
           end;
           CheckSymbol (SemicolonSy);
        end;

     end;
End;

Procedure BaseSpecifier (cls: TClsType);
Var  item: TParentItem;
Begin
     item := TParentItem.Create;

     if sy = VirtualSy then begin
        GetSymbol;
        item.is_virtual := true;
     end;

     if sy in AccessSet do begin
        case sy of
           PrivateSy:   item.access := PrivateAccess;
           ProtectedSy: item.access := ProtectedAccess;
           PublicSy:    item.access := PublicAccess;
           else         Bug;
        end;
        GetSymbol;
     end;

     if sy = VirtualSy then begin
        GetSymbol;
        item.is_virtual := true;
     end;

     item.ifc := QualifiedIdent (); {!?}
     Assert (cls.parents <> nil);
     cls.parents.Add (item);
End;

Function ClassDef: TClsType;
Begin
     case sy of
        ClassSy:  result := TClassType.Create;
        StructSy: result := TRecordType.Create; { !? }
        UnionSy:  result := TUnionSy.Create; { !? }
        else      Bug;
     end;

     if sy = IdentSy then
        result.name := Identifier (); {!?}

     item.parents := TParentSect.Create;
     item.members := TDeclSect.Create;
     item.friends := TFriendSect.Create;

     if sy = ColonSy then begin
        GetSymbol;
        BaseSpecifier (result);
        while sy = CommaSy do begin
           GetSymbol;
           BaseSpecifier (result);
        end;
     end;

     CheckSymbol (LBraceSy);
     ClassComponents (result);
     CheckSymbol (RBraceSy);
End;

(**************************** ENUMERATED TYPE *****************************)

Procedure EnumIdent (sect: TEnumSect);
Var  item: TEnumItem;
Begin
     item := TEnumItem.Create;
     item.name := Identifier ();

     if sy = AssignSy then begin
        GetSymbol ();
        item.value := ConstExpr ();
     end;

     sect.Add (item);
End;

Function EnumDef: TEnumType;
Begin
     result := TEnumType.Create;
     CheckSymbol (EnumSy);

     if sy = IdentSy then
        result.name := Identifier (); {!?}

     result.elements := TEnumSect.Create;

     CheckSymbol (LBraceSy);

     if sy <> LBraceSy then begin
        EnumIdent (result.elements);

        while sy = CommaSy do begin
           GetSymbol ();
           EnumIdent (result.elements);
        end;
     end;

     CheckSymbol (RBraceSy);
End;

END.
