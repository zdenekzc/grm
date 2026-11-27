
(**************************************************************************)
(*                                                                        *)
(*                              Declarations                              *)
(*                                                                        *)
(**************************************************************************)

UNIT Decl0;

INTERFACE

Uses SysUtils {func SameText},
     Fil0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     Expr0, Stat0, Type0;

Function ModuleDecl: TModule;

IMPLEMENTATION

(**************************************************************************)

Type TMode = (intf, global, local);
Function DeclPart (mode: TMode): TDeclSect; forward;

(********************************* LABELS *********************************)

Function LabelIdent: TIdent;
Begin
     case sy of
        IdentSy: result := IdentVal;
        NumSy:   result := NumberVal;
        else     Error ('Label expected');
     end;
     GetSymbol ();
End;

Procedure LabelDecl (sect: TDeclSect);
Var  decl: TLabelDecl;
Begin
     decl := TLabelDecl.Create;
     decl.name := LabelIdent ();
     sect.Add (decl);
End;

Procedure LabelSection (sect: TDeclSect);
Begin
     CheckSymbol (LabelSy);

     LabelDecl (sect);
     while sy = CommaSy do begin
        GetSymbol;
        LabelDecl (sect);
     end;

     CheckSymbol (SemicolonSy);
End;

(******************************* CONSTANTS ********************************)

Procedure ConstDecl (sect: TDeclSect);
Var  decl: TConstDecl;
Begin
     decl := TConstDecl.Create;
     decl.name := Identifier ();
     sect.Add (decl);

     if sy = ColonSy then begin
        GetSymbol;
        decl.typ := TypeDef ();
     end;

     CheckSymbol (EqualSy);

     if decl.typ <> nil then decl.val := StructConst ()
                        else decl.val := Expression ();

     CheckSymbol (SemicolonSy);
End;

Procedure ConstSection (sect: TDeclSect);
Begin
     CheckSymbol (ConstSy);
     repeat
        ConstDecl (sect);
     until sy <> IdentSy;
End;

(********************************* TYPES **********************************)

Procedure TypeDecl (sect: TDeclSect);
Var  decl: TTypeDecl;
Begin
     decl := TTypeDecl.Create;
     decl.name := Identifier ();
     sect.Add (decl);

     CheckSymbol (EqualSy);
     decl.typ := TypeDef ();

     CheckSymbol (SemicolonSy);
End;

Procedure TypeSection (sect: TDeclSect);
Begin
     CheckSymbol (TypeSy);
     repeat
        TypeDecl (sect);
     until sy <> IdentSy;
End;

(******************************* VARIABLES ********************************)

Procedure VarIdent (sect: TDeclSect);
Var  item: TVarDecl;
Begin
     item := TVarDecl.Create;
     item.name := Identifier ();
     sect.Add (item);
End;

Procedure VarDecl (sect: TDeclSect);
Var  start: TDecl;
     typ: TType;
     ini: TExpr;
     item: TVarDecl;
Begin
     VarIdent (sect);
     start := sect.last;

     while sy = CommaSy do begin
        GetSymbol;
        VarIdent (sect);
     end;

     CheckSymbol (ColonSy);
     typ := TypeDef ();

     ini := nil;
     if sy = EqualSy then begin
        GetSymbol;
        ini := StructConst ();
     end;

     CheckSymbol (SemicolonSy);

     { store type and initialization }
     item := start as TVarDecl;
     while item <> nil do begin
        item.typ := typ;
        item.ini := ini;
        item := item.next as TVarDecl;
     end;
End;

Procedure VarSection (sect: TDeclSect);
Begin
     CheckSymbol (VarSy);
     repeat
        VarDecl (sect);
     until sy <> IdentSy;
End;

(******************************* PROCEDURES *******************************)

{ procedures from unit Types:
  SubroutineHead,
  GetCall }

Procedure SubrExternal (decl: TProcDecl);
Begin
     CheckSymbol (ExternalSy);
     decl.a_external := true;

     if sy <> SemicolonSy then begin
        decl.a_lib := Expression ();
        ConvDirective;
        if sy = NameSy then begin
           GetSymbol;
           decl.a_name := Expression ();
           ConvDirective;
        end
        else if sy = IndexSy then begin
           GetSymbol;
           decl.a_index := Expression ();
        end;
     end;

     CheckSymbol (SemicolonSy);
End;

Procedure SubroutineIntf (sect: TDeclSect);
Var  decl: TProcDecl;
Begin
     decl := SubroutineHead ();

     ConvDirective;
     if sy = ExternalSy then
        SubrExternal (decl);

     sect.Add (decl);
End;

Procedure SubroutineDecl (sect: TDeclSect);
Var  decl: TProcDecl;
Begin
     decl := SubroutineHead ();

     { forward }
     ConvDirective;
     if sy = ForwardSy then begin
        decl.a_forward := true;
        GetSymbol;
        CheckSymbol (SemicolonSy);
        ConvDirective;
     end

     { external }
     else if sy = ExternalSy then
        SubrExternal (decl)

     { block }
     else begin
        decl.local := DeclPart (local);
        CheckSymbol (BeginSy);
        decl.body := StatementSeq ();
        CheckSymbol (EndSy);
        CheckSymbol (SemicolonSy);
     end;

     sect.Add (decl);
End;

(****************************** DECLARATIONS ******************************)

Const DclSet = [LabelSy, ConstSy, TypeSy, VarSy,
                ProcedureSy, FunctionSy, ClassSy, ConstructorSy, DestructorSy];

Function DeclPart (mode: TMode): TDeclSect;
Begin
     result := TDeclSect.Create ();

     while sy in DclSet do
        case sy of
           LabelSy:          LabelSection (result);
           ConstSy:          ConstSection (result);
           TypeSy:           TypeSection (result);
           VarSy:            VarSection (result);

           ProcedureSy,
           FunctionSy,
           ClassSy,
           ConstructorSy,
           DestructorSy:     if mode = intf then SubroutineIntf (result)
                                            else SubroutineDecl (result);

           else              Bug;
        end;
End;

(********************************** USES **********************************)

Procedure ImportEntry (sect: TImportSect);
Var  item: TImportItem;
Begin
     item := TImportItem.Create;
     item.name := Identifier ();
     sect.Add (item);
End;

Function ImportSect: TImportSect;
Begin
     result := TImportSect.Create;
     if sy = UsesSy then begin
        GetSymbol;

        ImportEntry (result);
        while sy = CommaSy do begin
           GetSymbol;
           ImportEntry (result);
        end;
        CheckSymbol (SemicolonSy);
    end;
End;

(********************************** UNIT **********************************)

Procedure PeriodExp;
Begin
     if sy <> PeriodSy then Error ('"." expected');
End;

{ Podprogram z interface a metoda tridy, ktere maji telo v implementacni casti,
  dostanou skip_impl - jinak by je vypis (plist0, clist0) zopakoval
  s prazdnym telem (procedura z interface v SendSubroutines,
  metoda v SendClassImpl). }
Function HasImpl (impl_sect: TDeclSect; const p_context, p_name: string): boolean;
Var  i: TDecl;
     p: TProcDecl;
Begin
     result := false;
     i := impl_sect.first;
     while (i <> nil) and not result do begin
        if i.tag = ProcDcl then begin
           p := i as TProcDecl;
           result := SameText (p.context, p_context) and SameText (p.name, p_name);
        end;
        i := i.next;
     end;
End;

Procedure MarkMethods (sect, impl_sect: TDeclSect);
Var  d, m: TDecl;
     typ:  TType;
Begin
     d := sect.first;
     while d <> nil do begin
        if d.tag = TypeDcl then begin
           typ := (d as TTypeDecl).typ;
           if (typ <> nil) and (typ.tag in [ClassTyp, ObjectTyp]) and
              ((typ as TClsType).members <> nil) then begin
              m := (typ as TClsType).members.first;
              while m <> nil do begin
                 if (m.tag = ProcDcl) and HasImpl (impl_sect, d.name, m.name) then
                    (m as TProcDecl).skip_impl := true;
                 m := m.next;
              end;
           end;
        end;
        d := d.next;
     end;
End;

Procedure MarkImplemented (intf_sect, impl_sect: TDeclSect);
Var  d: TDecl;
Begin
     d := intf_sect.first;
     while d <> nil do begin
        if (d.tag = ProcDcl) and HasImpl (impl_sect, '', d.name) then
           (d as TProcDecl).skip_impl := true;
        d := d.next;
     end;

     MarkMethods (intf_sect, impl_sect);
     MarkMethods (impl_sect, impl_sect);
End;

Function UnitDecl: TModule;
Begin
     result := TModule.Create;
     result.kind := UnitMod;

     CheckSymbol (UnitSy);
     result.name := Identifier ();
     CheckSymbol (SemicolonSy);

     { interface part }
     CheckSymbol (InterfaceSy);
     result.intf_imports := ImportSect ();
     result.intf_decl := DeclPart (intf);

     { implementation part }
     CheckSymbol (ImplementationSy);
     result.impl_imports  := ImportSect ();
     result.impl_decl := DeclPart (global);
     MarkImplemented (result.intf_decl, result.impl_decl);

     { body }
     if sy = InitializationSy then begin
        GetSymbol;
        result.init := StatementSeq ();

        if sy = FinalizationSy then begin
           GetSymbol;
           result.finish := StatementSeq ();
        end;
     end
     else if sy = BeginSy then begin
        GetSymbol;
        result.init := StatementSeq ();
     end;

     CheckSymbol (EndSy);
     PeriodExp;
End;

(******************************** PROGRAM *********************************)

Function ProgramDecl: TModule;
Begin
     result := TModule.Create;
     result.kind := ProgramMod;

     CheckSymbol (ProgramSy);
     result.name := Identifier ();
     CheckSymbol (SemicolonSy);

     { uses }
     result.intf_imports := ImportSect ();

     { declarations }
     result.intf_decl := DeclPart (global);
     MarkMethods (result.intf_decl, result.intf_decl);

     { body }
     CheckSymbol (BeginSy);
     result.init := StatementSeq ();
     CheckSymbol (EndSy);
     PeriodExp;
End;

(******************************** LIBRARY *********************************)

Function LibraryDecl: TModule;
Begin
     result := TModule.Create;
     result.kind := LibraryMod;

     CheckSymbol (LibrarySy);
     result.name := Identifier ();
     CheckSymbol (SemicolonSy);

     { uses }
     result.intf_imports := ImportSect ();

     { declaration }
     result.intf_decl := DeclPart (global);
     MarkMethods (result.intf_decl, result.intf_decl);

     { body }
     CheckSymbol (BeginSy);
     result.init := StatementSeq ();
     CheckSymbol (EndSy);
     PeriodExp;
End;

(********************************* MODULE *********************************)

Function ModuleDecl: TModule;
Begin
     case sy of
        UnitSy:    result := UnitDecl ();
        ProgramSy: result := ProgramDecl ();
        LibrarySy: result := LibraryDecl ();
        else       Error ('"UNIT", "PROGRAM" or "LIBRARY" expected');
     end;
End;

END.
