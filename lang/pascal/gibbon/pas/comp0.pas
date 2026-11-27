
(**************************************************************************)
(*                                                                        *)
(*                               Compilation                              *)
(*                                                                        *)
(**************************************************************************)

UNIT Comp0;

INTERFACE

Uses SysUtils,
     Fil0, Dir0, Lex0,
     {$IFDEF TAB} Tab0 {$ELSE} ProgCls {$ENDIF},
     Expr0, Stat0, Type0, Decl0;

{------------------------------- DICTIONARY -------------------------------}

Type  TDictNode = class (TAlloc)
         name:   TIdent;
         src:    TModule; { popis modulu }

         left:   TDictNode;   { strom prvku }
         right:  TDictNode;
      end;

      TDictTree = class (TAlloc)
         root:  TDictNode;

         procedure Add (module: TModule);
         function  Search (id: TIdent): TModule;
      end;

Var DictTree: TDictTree;

{---------------------------- COMPILE PROJECT -----------------------------}

Function CompileModule (p_file_name:   string;
                        p_search_path: string;
                        p_defines:     string): TModule;

Procedure CompileProject (p_file_name:   string;  { source file }
                          p_search_path: string;  { unit directories }
                          p_defines:     string;  { defined symbols }
                          var p_err:     boolean);

IMPLEMENTATION

(*************************** MODULE DICTIONARY ****************************)

Procedure TDictTree.Add (module: TModule);
Var  item: TDictNode;
     ptr:  ^ TDictNode;
     done: boolean;
     id:   TIdent;
Begin
     Assert (module <> nil);

     id := UpperCase (module.name);

     item := TDictNode.Create;
     item.name := id;
     item.src := module;

     item.left := nil;
     item.right := nil;

     ptr := @ root;
     done := false;

     while not done do
        if ptr^ = nil then begin
           done := true;
           ptr^ := item;
        end
        else if id < ptr^.name then ptr := addr (ptr^.left)
        else if id > ptr^.name then ptr := addr (ptr^.right)
        else Error ('Duplicate identifier ('+ id +')' );
End;

Function TDictTree.Search (id: TIdent): TModule;
Var  item: TDictNode;
     cmp:  integer;
     done: boolean;
Begin
     id := UpperCase (id);

     item := root;
     done := false;
     result := nil;

     while not done do
        if item = nil then begin
           result := nil;
           done   := true;
        end
        else begin
           cmp := CompareStr (id, item.name);
           if cmp < 0 then item := item.left
           else if cmp > 0 then item := item.right
           else begin
              Assert (item.src <> nil);
              result := item.src;
              done   := true;
           end;
        end;
End;

(******************************** PROJECT *********************************)

Procedure OpenProject (p_search_path: string);
Begin
     { create module dictionary }
     DictTree := TDictTree.Create;

     { initialize unit Fil }
     InitFil (p_search_path);
End;

Procedure CloseProject;
Begin
     Assert (Inp = nil);
End;

(******************************** COMPILE *********************************)

Procedure CompileModules (p_name, p_defines: string); forward;

Procedure CompileUses (sect: TImportSect; p_defines: string);
Var  item: TImportItem;
Begin
     if sect <> nil then begin
        item := sect.first;
        while item <> nil do begin
           if FileNameExist (item.name) then
              CompileModules (item.name, p_defines);
           item := item.next;
        end;
     end;
End;

Procedure CompileModules (p_name, p_defines: string);
Var  decl: TModule;
Begin
     decl := DictTree.Search (p_name);
     if decl = nil then begin
        { new module }
        writeln (p_name);

        { read source }
        OpenUnit (p_name, p_defines);
        GetSymbol;
        decl := ModuleDecl ();
        CloseUnit;

        { insert into DictTree - register module name }
        DictTree.Add (decl);

        { compile units used in interface }
        CompileUses (decl.intf_imports, p_defines);
        CompileUses (decl.impl_imports, p_defines);
     end
End;

{--------------------------------------------------------------------------}

Function CompileModule (p_file_name:   string;
                        p_search_path: string;
                        p_defines:     string): TModule;

Begin
     result := nil;

     try
        try

           OpenProject (p_search_path);
           OpenUnit (p_file_name, p_defines);
           GetSymbol;
           result := ModuleDecl ();
           CloseUnit;
           CloseProject;

        except
           on E: ECompile do
              result := nil;
        end;

     finally
        CloseAll;
     end;
End;

{--------------------------------------------------------------------------}

Procedure CompileProject (p_file_name:   string;
                          p_search_path: string;
                          p_defines:     string;
                          var p_err:     boolean);
Begin
     p_err := false;

     try
        try

           OpenProject (p_search_path);
           CompileModules (p_file_name, p_defines);
           CloseProject;

        except
           on E: ECompile do
              p_err := true;
        end;

     finally
        CloseAll;
     end;
End;

END.

