UNIT Tab0;

INTERFACE

Uses SysUtils,
     Fil0, Lex0;

Type  TType = class;
      TDeclSect = class;

      TPlace = class (TAlloc)
         loc:  TLocation; { umisteni ve zdrojovem textu }
         constructor Create;
      end;

      (*************************** EXPRESSIONS ****************************)

      TExpr       = class; { vyraz }
      TQualIdent  = TExpr; { kvalifikovany identifikator }

      TArgSect    = class; { argumenty funkce }
      TInxSect    = class; { indexy pole }
      TElemSect   = class; { prvky mnoziny }
      TStructSect = class; { prvky konstantni struktury }

      {--------------------------------------------------------------------}

      TExprTag = (BinaryExp,
                  UnaryExp,
                  ValueExp,

                  IdentExp,
                  IndexExp,

                  CallExp,
                  SetExp,
                  StructExp,

                  NilExp,
                  StringExp,
                  SuperExp,

                  { plist }
                  TextExp,

                  { cpp }
                  ThisExp,
                  CondExp);

      TBinaryKind = (MulExp, RDivExp, DivExp, ModExp,
                     AndExp, ShlExp, ShrExp, AsExp,
                     AddExp, SubExp, OrExp, XorExp,
                     EqExp, NeExp, LtExp, GtExp, LeExp, GeExp, InExp, IsExp,
                     FieldExp,

                     { cpp }
                     ScopeExp,
                     PtrFieldExp,
                     MemberExp, PtrMemberExp,
                     BitAndExp,  BitXorExp, BitOrExp,
                     LogAndExp, LogOrExp,
                     AssignExp,
                     MulAssignExp, DivAssignExp, ModAssignExp,
                     AddAssignExp, SubAssignExp,
                     ShlAssignExp, ShrAssignExp,
                     AndAssignExp, OrAssignExp, XorAssignExp,
                     CommaExp);

      TUnaryKind  = (NotExp, PlusExp, MinusExp, AdrExp, DerefExp,
                     { cpp }
                     GlobalExp, DestructorExp,
                     ParExp, SizeofExp,
                     BitNotExp, LogNotExp,
                     PreIncExp, PreDecExp, PostIncExp, PostDecExp);

      TValueKind  = (IntValueExp, FltValueExp, StrValueExp,
                     { cpp }
                     ChrValueExp);

      {--------------------------------------------------------------------}

      TExpr = class (TPlace)
         tag:    TExprTag; { druh vyrazu }
         { without constructor }
      end;

      {--------------------------------------------------------------------}

      TBinaryExpr = class (TExpr)
         kind:   TBinaryKind;
         left:   TExpr;   { levy podvyraz }
         right:  TExpr;   { pravy podvyraz }
         constructor Create;
      end;

      TUnaryExpr = class (TExpr)
         kind:   TUnaryKind;
         param:  TExpr;   { parameter }
         constructor Create;
      end;

      TValueExpr = class (TExpr)
         kind:   TValueKind;
         value:  string;  { konstanta }
         constructor Create;
      end;

      TIdentExpr = class (TExpr)
         ident:  TIdent;  { identifikator }
         constructor Create;
      end;

      TIndexExpr = class (TExpr)
         left:   TExpr;    { pole }
         list:   TInxSect; { indexy }
         constructor Create;
      end;

      TCallExpr = class (TExpr)
         func:   TExpr;      { funkce }
         list:   TArgSect;   { seznam argumentu }
         constructor Create;
      end;

      TSetExpr = class (TExpr)
         list:   TElemSect;  { seznam hodnot }
         constructor Create;
      end;

      TStructExpr = class (TExpr)
         list:   TStructSect;  { seznam hodnot }
         constructor Create;
      end;

      TNilExpr = class (TExpr)
         { nothing }
         constructor Create;
      end;

      TStringExpr = class (TExpr)
         param: TExpr; { pretypovavany parametr - opt }
         constructor Create;
      end;

      TSuperExpr = class (TExpr)
         ident:  TIdent;  { identifikator }
         constructor Create;
      end;

      TTextExpr = class (TExpr)
         text:  string;
         constructor Create;
      end;

      TThisExpr = class (TExpr)
         constructor Create;
      end;

      TCondExpr = class (TExpr)
         cond:       TExpr;
         true_expr:  TExpr;
         false_expr: TExpr;
         constructor Create;
      end;

      { TBinaryExpr:
           MulExp         left * right
           RDivExp        left / right
           DivExp         left div right
           ModExp         left mod right
           AndExp         left and right
           ShlExp         left shl right
           ShrExp         left shr right
           AsExp          left as right

           AddExp         left + right
           SubExp         left - right
           OrExp          left or right
           XorExp         left xor right

           EqExp          left = right
           NeExp          left <> right
           LtExp          left < right
           GtExp          left > right
           LeExp          left <= right
           GeExp          left >= right
           InExp          left in right
           IsExp          left is right

           FieldExp       param . ident

           ScopeExp       left :: right
           FieldExp       param -> ident
           MemberExp      left .* right
           PtrMemberExp   left ->* right

           BitAndExp      left & right
           BitXorExp      left ^ right
           BitOrExp       left | right
           LogAndExp      left && right
           LogOrExp       left || right

           AssignExp      left = right
           MulAssignExp   left *= right
           DivAssignExp   left /= right
           ModAssignExp   left %= right
           AddAssignExp   left += right
           SubAssignExp   left -= right
           ShlAssignExp   left <<= right
           ShrAssignExp   left >>= right
           AndAssignExp   left &= right
           OrAssignExp    left |= right
           XorAssignExp   left ^= right

           CommaExp       left, right

        TUnaryExpr:
           NotExp         not param
           PlusExp        + param
           MinusExp       - param
           AdrExp         @ param
           DerefExp       param ^

           GlobalExp      :: param
           DestructorExp  ~ param
           ParExp         ( param )
           SizeofExp      sizeof ( param )
           BitNotExp      ~ param
           LogNotExp      ! param
           PreIncExp      ++ param
           PreDecExp      -- param
           PostIncExp     param ++
           PostDecExp     param --

        TValueExpr:
           IntValueExp    value
           FltValueExp    value
           StrValueExp    value
           ChrValueExp    value

        TIdentExpr:
           IdentExp       ident

        TIndexExpr:
           IndexExp       left [right]

        TCallExpr:
           CallExp        param (list)

        TSetExpr:
           SetExp         [ list ]

        TStructExpr:
           StructExp      ( list )

        TNilExpr:
           NilExp         nil

        TStringExpr:
           StringExp      string (param)

        TSuperExpr:
           SuperExp       inherited ident

        TTextExpr:
           TextExp        text

        TThisExpr:
           ThisExp        this

        TCondExpr
           CondExp        cond ? true_expr : false_expr

        TArgItem:         name := value : width : digits
        TInxItem:         value
        TElemItem:        low .. high
        TStructItem:      name : value
      }

      {---------------------------- arguments -----------------------------}

      TArgItem = class (TPlace)
         value:  TExpr;  { hodnota parametru }
         width:  TExpr;  { hodnota za dvojteckou - opt }
         digits: TExpr;  { hodnota za druhou dvojteckou - opt }
         next:   TArgItem;   { nasledujici prvek seznamu }
      end;

      TArgSect = class (TPlace)
         first: TArgItem;
         last:  TArgItem;
         long_params: boolean;  { each parameter on separate line }
         procedure Add (item: TArgItem);
      end;

      {----------------------------- indexes ------------------------------}

      TInxItem = class (TPlace)
         value:  TExpr;      { hodnota parametru }
         next:   TInxItem;   { nasledujici prvek seznamu }
      end;

      TInxSect = class (TPlace)
         first: TInxItem;
         last:  TInxItem;
         procedure Add (item: TInxItem);
      end;

      {--------------------------- set elements ---------------------------}

      TElemItem = class (TPlace)
         low:    TExpr;      { hodnota parametru }
         high:   TExpr;      { hodnota za dvema teckami - opt }
         next:   TElemItem;  { nasledujici prvek seznamu }
      end;

      TElemSect = class (TPlace)
         first: TElemItem;
         last:  TElemItem;
         procedure Add (item: TElemItem);
      end;

      {----------------------- structured constants -----------------------}

      TStructItem = class (TPlace)
         name:  TIdent;      { jmeno parametru - opt }
         value: TExpr;       { hodnota parametru }
         next:  TStructItem; { nasledujici prvek seznamu }
      end;

      TStructSect = class (TPlace)
         arr:   boolean; { pole }
         rec:   boolean; { zaznam }

         first: TStructItem;
         last:  TStructItem;
         procedure Add (item: TStructItem);
      end;

      (**************************** STATEMENTS ****************************)

      TStat      = class; { prikaz }
      TStatSeq   = class; { posloupnost prikazu }

      TCaseSect  = class; { seznam variant prikazu case }
      TWithSect  = class; { seznam vyrazu v prikazy with}
      TOnSect    = class; { seznam variant on ... }

      {--------------------------------------------------------------------}

      TStatTag = (EmptySt, AssignSt, CallSt,
                  CompoundSt, GotoSt,
                  IfSt, CaseSt,
                  WhileSt, RepeatSt, ForSt,
                  WithSt,
                  RaiseSt, FinallySt, ExceptSt,

                  { cpp }
                  BreakSt, ContinueSt, ReturnSt,
                  SwitchSt, DoSt, CppForSt,
                  LabeledSt, CaseLabeledSt, DefaultLabeledSt,
                  ExpressionSt);

      {--------------------------------------------------------------------}

      TStat = class (TPlace)
         next:  TStat;    { dalsi prikaz }
         tag:   TStatTag; { druh prikazu }
         level: integer; { plist }
      end;

      TEmptyStat = class (TStat)
         { nothing }
         constructor Create;
      end;

      TAssignStat = class (TStat)
         left_expr:   TExpr;
         right_expr:  TExpr;
         constructor Create;
      end;

      TCallStat = class (TStat)
         call_expr:  TExpr;
         constructor Create;
      end;

      TCompoundStat = class (TStat)
         body_seq:   TStatSeq;
         constructor Create;
      end;

      TGotoStat = class (TStat)
         goto_lab:   TIdent;
         constructor Create;
      end;

      TIfStat = class (TStat)
         cond_expr:  TExpr;
         then_stat:  TStat;
         else_stat:  TStat; { opt }
         constructor Create;
      end;

      TCaseStat = class (TStat)
         case_expr:  TExpr;
         case_list:  TCaseSect;
         else_seq:   TStatSeq; { opt }
         constructor Create;
      end;

      TWhileStat = class (TStat)
         cond_expr:  TExpr;
         body_stat:  TStat;
         constructor Create;
      end;

      TRepeatStat = class (TStat)
         body_seq:   TStatSeq;
         until_expr: TExpr;
         constructor Create;
      end;

      TForStat = class (TStat)
         var_expr:   TExpr;
         from_expr:  TExpr;
         to_expr:    TExpr;
         incr:       boolean;  { true -> to, false -> downto }
         body_stat:  TStat;
         constructor Create;
      end;

      TWithStat = class (TStat)
         with_list:  TWithSect;
         body_stat:  TStat;
         constructor Create;
      end;

      TRaiseStat = class (TStat)
         raise_expr: TExpr; { opt }
         constructor Create;
      end;

      TFinallyStat = class (TStat)
         body_seq:    TStatSeq;
         finally_seq: TStatSeq;
         constructor  Create;
      end;

      TExceptStat = class (TStat)
         body_seq:    TStatSeq;
         on_list:     TOnSect;
         else_seq:    TStatSeq; { opt }
         constructor  Create;
      end;

      TBreakStat = class (TStat)
         constructor Create;
      end;

      TContinueStat = class (TStat)
         constructor Create;
      end;

      TReturnStat = class (TStat)
         return_expr: TExpr;
         constructor Create;
      end;

      TSwitchStat = class (TStat)
         switch_expr: TExpr;
         body_stat:   TStat;
         constructor Create;
      end;

      TDoStat = class (TStat)
         while_expr: TExpr;
         body_stat:  TStat;
         constructor Create;
      end;

      TCppForStat = class (TStat)
         init_stat: TStat;
         cond_expr: TExpr;
         step_expr: TExpr;
         body_stat: TStat;
         constructor Create;
      end;

      TLabeledStat = class (TStat)
         label_expr: TExpr;
         body_stat:  TStat;
         constructor Create;
      end;

      TCaseLabeledStat = class (TStat)
         case_expr: TExpr;
         body_stat: TStat;
         constructor  Create;
      end;

      TDefaultLabeledStat = class (TStat)
         body_stat: TStat;
         constructor  Create;
      end;

      TExpressionStat = class (TStat)
         expr: TExpr;
         constructor  Create;
      end;

      { EmptySt
        AssignSt    left_expr := right_expr
        CallSt      call_expr
        CompoundSt  begin body_seq end
        GotoSt      goto goto_expr
        IfSt        if cond_expr then then_stat else else_stat
        CaseSt      case case_expr of case_list else else_stat end
        WhileSt     while cond_expr do body_stat
        RepeatSt    repeat body_seq until until_expr
        ForSt       for var_expr := from_expr to/downto to_expr do body_stat
        WithSt      with with_list do body_stat
        RaiseSt     raise raise_expr at at_expr
        FinallySt   try body_seq finally finally_seq end
        ExceptSt    try body_seq except on_list else else_seq end

        BreakSt     break
        ContinueSt  continue
        ReturnSt    return return_expr
        SwitchSt    switch (switch_expr) body_stat
        DoSt        do body_stat while (while_expr)
        CppForSt    for (init_expr; cond_expr; step_expr) body_stat

        LabeledSt         label_expr : body_stat
        CaseLabeledSt     case case_expr : body_stat
        DefaultLabeledSt  default : body_stat
        ExpressionSt      expr;

        TCaseItem   sel_list : sel_stat
        TWithItem   expr
        TOnItem     on on_expr : type_expr do body_stat }

      {------------------------ statement sequence ------------------------}

      TStatSeq = class (TPlace)
         first: TStat;
         last:  TStat;
         procedure Add (item: TStat);
      end;

      {-------------------------- case variants ---------------------------}

      TCaseItem = class (TPlace)
         sel_list: TElemSect; { list of expressions }
         sel_stat: TStat;     { statement }
         next:     TCaseItem;
      end;

      TCaseSect = class (TPlace)
         first: TCaseItem;
         last:  TCaseItem;
         procedure Add (item: TCaseItem);
      end;

      {------------------------- with expressions -------------------------}

      TWithItem = class (TPlace)
         expr:   TExpr;     { vyraz }
         next:   TWithItem; { nasledujici prvek seznamu }
      end;

      TWithSect = class (TPlace)
         first: TWithItem;
         last:  TWithItem;
         procedure Add (item: TWithItem);
      end;

      {--------------------------- on exception ---------------------------}

      TOnItem = class (TPlace)
         on_ident:     TIdent;  { opt }
         on_type:      TType;
         body_stat:    TStat;
         next:         TOnItem;
      end;

      TOnSect = class (TPlace)
         first: TOnItem;
         last:  TOnItem;
         procedure Add (item: TOnItem);

      end;

      (****************************** TYPES *******************************)

      TEnumSect      = class;
      TParamSect     = class;
      TInterfaceSect = class;
      TFriendSect    = class;

      {--------------------------------------------------------------------}

      TTypeTag = (AliasTyp,      { type t = ident }

                  SubrangeTyp,
                  EnumTyp,
                  StringTyp,
                  ArrayTyp,
                  RecordTyp,
                  PointerTyp,
                  SetTyp,
                  FileTyp,
                  ObjectTyp,
                  ClassTyp,
                  ClassOfTyp,
                  InterfaceTyp,
                  ProcTyp);

      {--------------------------------------------------------------------}

      TType = class (TPlace)
         tag:      TTypeTag;
         info:     string;   { !debug }
         { without constructor }
      end;

      { -- alias -- }

      TAliasType = class (TType)
         qual_ident: TExpr;
         constructor Create;
      end;

      { -- subrange -- }

      TSubrangeType = class (TType)
         low:  TExpr;
         high: TExpr;
         constructor Create;
      end;

      { -- enumerated -- }

      TEnumType = class (TType)
         elements: TEnumSect;
         constructor Create;
      end;

      { -- string -- }

      TStringType = class (TType)
         lim:        TExpr;       { limit - opt }
         constructor Create;
      end;

      { -- array -- }

      TArrayType = class (TType)
         index:         TType;   { opt }
         elem:          TType;

         dynamic_array: boolean;
         open_array:    boolean;

         constructor    Create;
      end;

      { -- record -- }

      TRecordType = class (TType)
         fields: TDeclSect;
         constructor Create;
      end;

      { -- pointer -- }

      TPointerType = class (TType)
         elem: TType;
         constructor Create;
      end;

      { -- set -- }

      TSetType = class (TType)
         elem: TType;
         constructor Create;
      end;

      { -- file -- }

      TFileType = class (TType)
         elem:         TType;    { opt }
         untyped_file: boolean;  { file }
         constructor Create;
      end;

      { -- class -- }

      TClsType = class (TType)
         parent:      TType;           { parent class - opt }
         ifc_list:    TInterfaceSect;  { interfaces - opt }

         members:     TDeclSect;       { members - opt }
         friends:     TFriendSect;     { friends - opt }

         forw:        boolean;         { forward class declaration }

         { without constructor }
      end;

      TObjectType = class (TClsType)
         constructor Create;
      end;

      TClassType = class (TClsType)
         constructor Create;
      end;

      TInterfaceType = class (TClsType)
         constructor Create;
      end;

      TClassOfType = class (TType)
         elem:      TType;
         constructor Create;
      end;

      { -- subroutine -- }

      TStyle = (ProcedureStyle,
                FunctionStyle,
                ConstructorStyle,
                DestructorStyle);

      TCall  = (NoCall,
                RegisterCall,
                CdeclCall,
                PascalCall,
                StdcallCall,
                SafecallCall);

      TProcType = class (TType)
         static_proc: boolean;    { class procedure / function }
         style:       TStyle;     { procedura, funkce, ... }
         param_list:  TParamSect; { seznam parametru }
         answer:      TType;      { vysledek - opt }
         of_object:   boolean;    { 'of object' }
         call:        TCall;      { zpusob volani }

         constructor Create;
      end;

      { ------------------------------------------------------------ }

      { TAliasType     ident

        TSubrangeType  low .. high
        TEnumType      (items)
        TStringType    string [expr1]
        TArrayType     array [indexes] of elem
        TRecordType    record field_list end
        TPointerType   ^ elem
        TSetType       set of elem
        TFileType      file of elem
        TTextType      text

        TObjectType    object (parent) member_list end
        TClassType     class (parent, ifc_list) member_list end
        TClassOfType   class of elem;
        TInterfaceType interface (parent, ifc) member_list end

        TProcType      procedure params
                       function params: answer }

      {------------------------- enum identifiers -------------------------}

      TEnumItem = class (TPlace)
         name: TIdent;
         next: TEnumItem;
      end;

      TEnumSect = class (TPlace)
         first: TEnumItem; { prvni polozka }
         last:  TEnumItem; { posledni polozka }
         procedure Add (item: TEnumItem);
      end;

      {---------------------------- parameters ----------------------------}

      TParamMode = (ValueParam,
                    ConstParam,
                    VarParam,
                    OutParam);

      TParamItem = class (TPlace)
         mode:  TParamMode;
         name:  TIdent;
         typ:   TType;      { opt }
         ini:   TExpr;      { opt }
         next:  TParamItem;
      end;

      TParamSect = class (TPlace)
         first: TParamItem;
         last:  TParamItem;
         procedure Add (item: TParamItem);
      end;

      {---------------------------- interfaces ----------------------------}

      TInterfaceItem = class (TPlace)
         ifc:  TType;
         next: TInterfaceItem;
      end;

      TInterfaceSect = class (TPlace)
         first: TInterfaceItem;
         last:  TInterfaceItem;
         procedure Add (item: TInterfaceItem);
      end;

      {-------------------------- CLASS FRIENDS ---------------------------}

      TFriendItem = class (TPlace)
         cls:      boolean; { friend class }
         name:     TIdent;
         next:     TFriendItem;
      end;

      TFriendSect = class (TPlace)
         first: TFriendItem;
         last:  TFriendItem;
         procedure Add (item: TFriendItem);
      end;

      (*************************** DECLARATIONS ***************************)

      TAccess  = (PrivateAccess,
                  ProtectedAccess,
                  PublicAccess,
                  PublishedAccess,
                  AutomatedAccess);

      TDeclTag = (LabelDcl,
                  ConstDcl,
                  TypeDcl,
                  VarDcl,
                  ProcDcl,
                  PropertyDcl);

      TDecl = class (TPlace)
         tag:    TDeclTag; { druh deklarace }
         access: TAccess;  { pristupova prava }
         name:   TIdent;   { identifikator }
         next:   TDecl;

         constructor Create;
      end;

      TDeclSect = class (TPlace)
         first: TDecl;
         last:  TDecl;
         procedure Add (item: TDecl);
      end;

      { -- label -- }

      TLabelDecl = class (TDecl)
         constructor Create;
      end;

      { -- const -- }

      TConstDecl = class (TDecl)
         typ: TType;  { typ - opt }
         val: TExpr;  { hodnota }
         constructor Create;
      end;

      { -- type -- }

      TTypeDecl = class (TDecl)
         typ: TType;    { prave definovany typ }
         constructor Create;
      end;

      { -- var -- }

      TVarDecl = class (TDecl)
         typ:      TType;    { type }
         ini:      TExpr;    { inicializace - opt }

         a_external: boolean; { external }
         a_lib:      TExpr;   { library - opt }
         a_name:     TExpr;   { name - opt }
         a_index:    TExpr;   { index - opt }

         constructor Create;
      end;

      { -- procedure -- }

      TProcDecl = class (TDecl)
         static_proc:   boolean;    { class procedure / function }
         style:         TStyle;     { procedura, funkce, ... }
         context:       TIdent;     { identifikator tridy - opt }
         param_list:    TParamSect; { seznam parametru }
         answer:        TType;      { vysledek - opt }
         call:          TCall;      { zpusob volani }

         local:         TDeclSect;  { local declarations - opt }
         body:          TStatSeq;   { body - opt }

         a_reintroduce: boolean;    { reintroduce }
         a_overload:    boolean;    { overload }
         a_inline:      boolean;    { inline }

         a_virtual:     boolean;    { virtual }
         a_dynamic:     boolean;    { dynamic }
         a_message:     TExpr;      { message - opt }
         a_override:    boolean;    { override }
         a_abstract:    boolean;    { abstract }

         a_forward:     boolean;    { forward }

         a_external:    boolean;    { external }
         a_lib:         TExpr;      { library - opt }
         a_name:        TExpr;      { name - opt }
         a_index:       TExpr;      { index - opt }

         constructor Create;
      end;

      { -- property -- }

      TPropertyDecl = class (TDecl)
         param_list:   TParamSect;     { opt }
         typ:          TType;          { opt }
         index:        TExpr;          { opt }

         a_read:       TQualIdent;     { opt }
         a_write:      TQualIdent;     { opt }
         a_stored:     TExpr;          { opt }

         a_default:    TExpr;          { opt }
         a_nodefault:  boolean;        { opt }

         a_implements: TInterfaceSect; { opt }
         a_def_array:  boolean;        { opt - default array property }

         constructor Create;
      end;

      { TLabelDecl    name
        TConstDecl    name : typ = val
        TTypeDecl     name = typ
        TVarDecl      name : typ = ini
        TProcDecl     procedure ...
        TPropertyDecl property name ...  }

      (***************************** MODULES ******************************)

      TImportSect = class;

      TModuleKind = (UnitMod,
                     ProgramMod,
                     LibraryMod);

      TModule = class
         name:         TIdent;
         kind:         TModuleKind; { unit / program / library }

         intf_imports: TImportSect; { interface }
         impl_imports: TImportSect; { implementation }

         intf_decl:    TDeclSect;   { interface declarations }
         impl_decl:    TDeclSect;   { implementation declarations }

         init:   TStatSeq; { initialization - opt }
         finish: TStatSeq; { finalization  - opt }
      end;

      {------------------------------- uses -------------------------------}

      TImportItem = class (TPlace)
         name:  TIdent;
         next:  TImportItem;
      end;

      TImportSect = class (TPlace)
         first: TImportItem;
         last:  TImportItem;

         procedure Add (item: TImportItem);
      end;

      {----------------------------- exports ------------------------------}

      TExportsItem = class (TPlace)
         name:    TIdent;       { subroutine identifier }
         e_index: TExpr;        { export by number - opt }
         e_name:  TExpr;        { export by name - opt }
         next:    TExportsItem; { next item }
      end;

      TExportsSect = class (TPlace)
         first: TExportsItem;
         last:  TExportsItem;
         procedure Add (item: TExportsItem);
      end;

IMPLEMENTATION

(********************************** ADD ***********************************)

Procedure TArgSect.Add (item: TArgItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TInxSect.Add (item: TInxItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TElemSect.Add (item: TElemItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TStructSect.Add (item: TStructItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

{--------------------------------------------------------------------------}

Procedure TStatSeq.Add (item: TStat);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TWithSect.Add (item: TWithItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TCaseSect.Add (item: TCaseItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TOnSect.Add (item: TOnItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

{--------------------------------------------------------------------------}

Procedure TEnumSect.Add (item: TEnumItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TParamSect.Add (item: TParamItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TInterfaceSect.Add (item: TInterfaceItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TFriendSect.Add (item: TFriendItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

{--------------------------------------------------------------------------}

Procedure TDeclSect.Add (item: TDecl);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TImportSect.Add (item: TImportItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

Procedure TExportsSect.Add (item: TExportsItem);
Begin
     if first = nil then begin
        first := item;
        last := item;
     end
     else begin
        last.next := item;
        last := item;
     end;
End;

(********************************* CREATE *********************************)

Constructor TPlace.Create;
Begin
     inherited Create;
     loc := SymLoc;
End;

{--------------------------------------------------------------------------}

Constructor TBinaryExpr.Create;
Begin
     inherited Create;
     tag := BinaryExp;
End;

Constructor TUnaryExpr.Create;
Begin
     inherited Create;
     tag := UnaryExp;
End;

Constructor TValueExpr.Create;
Begin
     inherited Create;
     tag := ValueExp;
End;

{--------------------------------------------------------------------------}

Constructor TIdentExpr.Create;
Begin
     inherited Create;
     tag := IdentExp;
End;

Constructor TIndexExpr.Create;
Begin
     inherited Create;
     tag := IndexExp;
End;

Constructor TCallExpr.Create;
Begin
     inherited Create;
     tag := CallExp;
End;

Constructor TSetExpr.Create;
Begin
     inherited Create;
     tag := SetExp;
End;

Constructor TStructExpr.Create;
Begin
     inherited Create;
     tag := StructExp;
End;

Constructor TNilExpr.Create;
Begin
     inherited Create;
     tag := NilExp;
End;

Constructor TStringExpr.Create;
Begin
     inherited Create;
     tag := StringExp;
End;

Constructor TSuperExpr.Create;
Begin
     inherited Create;
     tag := SuperExp;
End;

Constructor TTextExpr.Create;
Begin
     inherited Create;
     tag := TextExp;
End;

Constructor TThisExpr.Create;
Begin
     inherited Create;
     tag := ThisExp;
End;

Constructor TCondExpr.Create;
Begin
     inherited Create;
     tag := CondExp;
End;

{--------------------------------------------------------------------------}

Constructor TEmptyStat.Create;
Begin
     inherited Create;
     tag := EmptySt;
End;

Constructor TAssignStat.Create;
Begin
     inherited Create;
     tag := AssignSt;
End;

Constructor TCallStat.Create;
Begin
     inherited Create;

     tag := CallSt;
End;

Constructor TCompoundStat.Create;
Begin
     inherited Create;
     tag := CompoundSt;
End;

Constructor TGotoStat.Create;
Begin
     inherited Create;
     tag := GotoSt;
End;

Constructor TIfStat.Create;
Begin
     inherited Create;
     tag := IfSt;
End;

Constructor TCaseStat.Create;
Begin
     inherited Create;
     tag := CaseSt;
End;

Constructor TWhileStat.Create;
Begin
     inherited Create;
     tag := WhileSt;
End;

Constructor TRepeatStat.Create;
Begin
     inherited Create;
     tag := RepeatSt;
End;

Constructor TForStat.Create;
Begin
     inherited Create;
     tag := ForSt;
End;

Constructor TWithStat.Create;
Begin
     inherited Create;
     tag := WithSt;
End;

Constructor TRaiseStat.Create;
Begin
     inherited Create;
     tag := RaiseSt;
End;

Constructor TFinallyStat.Create;
Begin
     inherited Create;
     tag := FinallySt;
End;

Constructor TExceptStat.Create;
Begin
     inherited Create;
     tag := ExceptSt;
End;

Constructor TBreakStat.Create;
Begin
     inherited Create;
     tag := BreakSt;
End;

Constructor TContinueStat.Create;
Begin
     inherited Create;
     tag := ContinueSt;
End;

Constructor TReturnStat.Create;
Begin
     inherited Create;
     tag := ReturnSt;
End;

Constructor TSwitchStat.Create;
Begin
     inherited Create;
     tag := SwitchSt;
End;

Constructor TDoStat.Create;
Begin
     inherited Create;
     tag := DoSt;
End;

Constructor TCppForStat.Create;
Begin
     inherited Create;
     tag := CppForSt;
End;

Constructor TLabeledStat.Create;
Begin
     inherited Create;
     tag := LabeledSt;
End;

Constructor TCaseLabeledStat.Create;
Begin
     inherited Create;
     tag := CaseLabeledSt;
End;

Constructor TDefaultLabeledStat.Create;
Begin
     inherited Create;
     tag := DefaultLabeledSt;
End;

Constructor TExpressionStat.Create;
Begin
     inherited Create;
     tag := ExpressionSt;
End;

{--------------------------------------------------------------------------}

Constructor TAliasType.Create;
Begin
     inherited Create;
     tag := AliasTyp;
End;

Constructor TSubrangeType.Create;
Begin
     inherited Create;
     tag := SubrangeTyp;
End;

Constructor TEnumType.Create;
Begin
     inherited Create;
     tag := EnumTyp;
End;

Constructor TStringType.Create;
Begin
     inherited Create;
     tag := StringTyp;
End;

Constructor TArrayType.Create;
Begin
     inherited Create;
     tag := ArrayTyp;
End;

Constructor TPointerType.Create;
Begin
     inherited Create;
     tag := PointerTyp;
End;

Constructor TSetType.Create;
Begin
     inherited Create;
     tag := SetTyp;
End;

Constructor TFileType.Create;
Begin
     inherited Create;
     tag := FileTyp;
End;

Constructor TRecordType.Create;
Begin
     inherited Create;
     tag := RecordTyp;
End;

Constructor TObjectType.Create;
Begin
     inherited Create;
     tag := ObjectTyp;
End;

Constructor TClassType.Create;
Begin
     inherited Create;
     tag := ClassTyp;
End;

Constructor TClassOfType.Create;
Begin
     inherited Create;
     tag := ClassOfTyp;
End;

Constructor TInterfaceType.Create;
Begin
     inherited Create;
     tag := InterfaceTyp;
End;

Constructor TProcType.Create;
Begin
     inherited Create;
     tag := ProcTyp;
End;

{--------------------------------------------------------------------------}

Constructor TDecl.Create;
Begin
     inherited Create;
     access := PublicAccess;
End;

Constructor TLabelDecl.Create;
Begin
     inherited Create;
     tag := LabelDcl;
End;

Constructor TConstDecl.Create;
Begin
     inherited Create;
     tag := ConstDcl;
End;

Constructor TTypeDecl.Create;
Begin
     inherited Create;
     tag := TypeDcl;
End;

Constructor TVarDecl.Create;
Begin
     inherited Create;
     tag := VarDcl;
End;

Constructor TProcDecl.Create;
Begin
     inherited Create;
     tag := ProcDcl;
End;

Constructor TPropertyDecl.Create;
Begin
     inherited Create;
     tag := PropertyDcl;
End;

END.
