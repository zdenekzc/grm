unit pas_parser;

interface

uses textio;

type
   Symbol = (
      eos,
      identifier,
      number,
      real_number,
      character_literal,
      string_literal,
      separator,
      end_of_line,
      LPAREN,
      RPAREN,
      STAR,
      PLUS,
      COMMA,
      MINUS,
      DOT,
      RANGE,
      SLASH,
      COLON,
      ASSIGN,
      SEMICOLON,
      LESS,
      LESS_OR_EQUAL,
      UNEQUAL,
      EQUAL,
      GREATER,
      GREATER_OR_EQUAL,
      ADDRESS,
      LBRACKET,
      RBRACKET,
      ARROW,
      keyword_abstract,
      keyword_and,
      keyword_array,
      keyword_as,
      keyword_automated,
      keyword_begin,
      keyword_case,
      keyword_cdecl,
      keyword_class,
      keyword_const,
      keyword_constructor,
      keyword_default,
      keyword_destructor,
      keyword_div,
      keyword_do,
      keyword_downto,
      keyword_dynamic,
      keyword_else,
      keyword_end,
      keyword_except,
      keyword_external,
      keyword_file,
      keyword_finalization,
      keyword_finally,
      keyword_for,
      keyword_forward,
      keyword_function,
      keyword_goto,
      keyword_if,
      keyword_implementation,
      keyword_implements,
      keyword_in,
      keyword_inherited,
      keyword_initialization,
      keyword_inline,
      keyword_interface,
      keyword_is,
      keyword_label,
      keyword_library,
      keyword_mod,
      keyword_nil,
      keyword_nodefault,
      keyword_not,
      keyword_object,
      keyword_of,
      keyword_on,
      keyword_or,
      keyword_out,
      keyword_override,
      keyword_packed,
      keyword_pascal,
      keyword_private,
      keyword_procedure,
      keyword_program,
      keyword_property,
      keyword_protected,
      keyword_public,
      keyword_published,
      keyword_raise,
      keyword_read,
      keyword_record,
      keyword_register,
      keyword_repeat,
      keyword_safecall,
      keyword_set,
      keyword_shl,
      keyword_shr,
      keyword_stdcall,
      keyword_stored,
      keyword_string,
      keyword_then,
      keyword_to,
      keyword_try,
      keyword_type,
      keyword_unit,
      keyword_until,
      keyword_uses,
      keyword_var,
      keyword_virtual,
      keyword_while,
      keyword_with,
      keyword_write,
      keyword_xor
   );

   TItem = class;
   TBasic = class;
   TExpr = class;
   TBinaryExpr = class;
   TComponentsItem = class;
   TParamItem = class;
   TModule = class;
   TLabelIdent = class;
   TQualName = class;
   TContName = class;
   TType = class;
   TAliasType = class;
   TStringType = class;
   TFileType = class;
   TInxItem = class;
   TInxList = class;
   TArgItem = class;
   TArgSect = class;
   TElemSect = class;
   TElemItem = class;
   TStructSect = class;
   TIdentExpr = class;
   TIntValueExpr = class;
   TFltValueExpr = class;
   TStrValueExpr = class;
   TNilExpr = class;
   TStructExpr = class;
   TNotExpr = class;
   TPlusExpr = class;
   TMinusExpr = class;
   TAdrExpr = class;
   TSetExpr = class;
   TSuperExpr = class;
   TStringExpr = class;
   TIndexExpr = class;
   TCallExpr = class;
   TDerefExpr = class;
   TFieldExpr = class;
   TStat = class;
   TGotoStat = class;
   TBlockStat = class;
   TStatSeq = class;
   TIfStat = class;
   TCaseStat = class;
   TCaseSect = class;
   TCaseItem = class;
   TWhileStat = class;
   TRepeatStat = class;
   TForStat = class;
   TWithStat = class;
   TWithSect = class;
   TWithItem = class;
   TRaiseStat = class;
   TTryStat = class;
   TFinallyPart = class;
   TExceptPart = class;
   TOnSect = class;
   TOnItem = class;
   TEmptyStat = class;
   TAssignStat = class;
   TCallStat = class;
   TLabeledTStat = class;
   TParamIdent = class;
   TParamSect = class;
   TClassType = class;
   TInterfaceType = class;
   TInterfaceSect = class;
   TIntefaceItem = class;
   TComponetsSect = class;
   TDeclGroup = class;
   TDeclSect = class;
   TFieldItem = class;
   TFieldDecl = class;
   TPropertyDecl = class;
   TEnumType = class;
   TEnumSect = class;
   TEnumItem = class;
   TArrayType = class;
   TIndexTypeSect = class;
   TIndexTypeItem = class;
   TRecordType = class;
   TFieldDeclGroup = class;
   TPointerType = class;
   TSetType = class;
   TClassOfType = class;
   TProcType = class;
   TSubrangeType = class;
   TLabelDecl = class;
   TLabelSect = class;
   TConstDecl = class;
   TConstSect = class;
   TTypeDecl = class;
   TTypeSect = class;
   TVarItem = class;
   TVarDecl = class;
   TVarSect = class;
   TProcDecl = class;
   TImportItem = class;
   TImportSect = class;
   TUnitModule = class;
   TProgramModule = class;
   TLibraryModule = class;
   TTermExpr = class;
   TSimpleExpr = class;
   TCompleteExpr = class;

   Parser = class (TTextInput)
   public
      constructor create;

      function parse_label_ident : TLabelIdent;
      function parse_qualified_name : TQualName;
      function parse_cont_name : TContName;
      function parse_ifc_type : TType;
      function parse_param_type : TType;
      function parse_result_type : TType;
      function parse_simple_alias_type : TAliasType;
      function parse_simple_string_type : TStringType;
      function parse_simple_file_type : TFileType;
      function parse_index_expr_item : TInxItem;
      function parse_index_expr_list : TInxList;
      function parse_arg_item : TArgItem;
      function parse_arg_list : TArgSect;
      function parse_elem_sect : TElemSect;
      function parse_elem_item : TElemItem;
      function parse_struct_item : TStructSect;
      function parse_struct_sect : TStructSect;
      function parse_ident_expr : TIdentExpr;
      function parse_int_value_expr : TIntValueExpr;
      function parse_float_value_expr : TFltValueExpr;
      function parse_string_value_expr : TStrValueExpr;
      function parse_nil_expr : TNilExpr;
      function parse_sub_expr : TStructExpr;
      function parse_not_expr : TNotExpr;
      function parse_plus_expr : TPlusExpr;
      function parse_minus_expr : TMinusExpr;
      function parse_adr_expr : TAdrExpr;
      function parse_set_expr : TSetExpr;
      function parse_super_expr : TSuperExpr;
      function parse_string_type_expr : TStringExpr;
      function parse_variable : TExpr;
      function parse_reference : TExpr;
      function parse_index_expr (store : TExpr) : TIndexExpr;
      function parse_call_expr (store : TExpr) : TCallExpr;
      function parse_deref_expr (store : TExpr) : TDerefExpr;
      function parse_field_expr (store : TExpr) : TFieldExpr;
      function parse_factor : TExpr;
      function parse_term : TExpr;
      function parse_simple_expr : TExpr;
      function parse_expr : TExpr;
      function parse_goto_stat : TGotoStat;
      function parse_begin_stat : TBlockStat;
      function parse_stat_list : TStatSeq;
      function parse_inner_stat : TStat;
      function parse_if_stat : TIfStat;
      function parse_case_stat : TCaseStat;
      function parse_case_sect : TCaseSect;
      function parse_case_item : TCaseItem;
      function parse_while_stat : TWhileStat;
      function parse_repeat_stat : TRepeatStat;
      function parse_for_stat : TForStat;
      function parse_with_stat : TWithStat;
      function parse_with_sect : TWithSect;
      function parse_with_item : TWithItem;
      function parse_raise_stat : TRaiseStat;
      function parse_try_stat : TTryStat;
      function parse_finally_part : TFinallyPart;
      function parse_except_part : TExceptPart;
      function parse_on_sect : TOnSect;
      function parse_on_item : TOnItem;
      function parse_empty_stat : TEmptyStat;
      function parse_simple_stat : TStat;
      function parse_assign_stat (store : TExpr) : TAssignStat;
      function parse_call_stat (store : TExpr) : TCallStat;
      function parse_labeled_stat : TLabeledTStat;
      function parse_stat : TStat;
      function parse_param_ident : TParamIdent;
      function parse_param_item : TParamItem;
      function parse_formal_param_list : TParamSect;
      function parse_property_param_list : TParamSect;
      function parse_class_type : TClassType;
      function parse_interface_type : TInterfaceType;
      function parse_interface_sect : TInterfaceSect;
      function parse_interface_item : TIntefaceItem;
      function parse_components_sect : TComponetsSect;
      function parse_components_item : TComponentsItem;
      function parse_components_first_item : TComponentsItem;
      function parse_member_sect : TDeclGroup;
      function parse_member_decl : TDeclSect;
      function parse_field_ident : TFieldItem;
      function parse_field_decl : TFieldDecl;
      function parse_method_decl : TProcDecl;
      function parse_property_decl : TPropertyDecl;
      function parse_enum_type : TEnumType;
      function parse_enum_sect : TEnumSect;
      function parse_enum_item : TEnumItem;
      function parse_string_type : TStringType;
      function parse_array_type : TArrayType;
      function parse_index_type_sect : TIndexTypeSect;
      function parse_index_type_item : TIndexTypeItem;
      function parse_record_type : TRecordType;
      function parse_field_sect : TFieldDeclGroup;
      function parse_pointer_type : TPointerType;
      function parse_set_type : TSetType;
      function parse_file_type : TFileType;
      function parse_class_of_type : TClassOfType;
      function parse_proc_type : TProcType;
      function parse_range_type : TSubrangeType;
      function parse_alias_type : TAliasType;
      function parse_type : TType;
      function parse_label_decl : TLabelDecl;
      function parse_label_sect : TLabelSect;
      function parse_const_decl : TConstDecl;
      function parse_const_sect : TConstSect;
      function parse_type_decl : TTypeDecl;
      function parse_type_sect : TTypeSect;
      function parse_var_item : TVarItem;
      function parse_var_decl : TVarDecl;
      function parse_var_sect : TVarSect;
      function parse_proc_head (param : TProcDecl) : TProcDecl;
      function parse_proc_decl : TProcDecl;
      function parse_proc_external (param : TProcDecl) : TProcDecl;
      function parse_proc_intf_decl : TProcDecl;
      function parse_intf_decl : TDeclSect;
      function parse_intf_decl_part : TDeclGroup;
      function parse_decl : TDeclSect;
      function parse_decl_part : TDeclGroup;
      function parse_import_item : TImportItem;
      function parse_import_sect : TImportSect;
      function parse_unit_decl : TUnitModule;
      function parse_program_decl : TProgramModule;
      function parse_library_decl : TLibraryModule;
      function parse_module_decl : TModule;

   public
      token: Symbol;

      procedure lookupKeyword;
      procedure processSeparator;
      function tokenToString (value :Symbol) : string;

      function isSymbol (sym : Symbol) : boolean; inline;
      procedure checkSymbol (sym : Symbol); inline;
      function testSymbols (table : array of byte) : boolean; inline;
      procedure stop;

      procedure translate;
      procedure storeLocation (item : TItem);
      procedure on_ident_expr (item: TIdentExpr); virtual;
      procedure on_field_expr (item: TFieldExpr); virtual;
      procedure on_param (item: TParamIdent); virtual;
      procedure add_param (item: TParamItem); virtual;
      procedure open_class (item: TClassType); virtual;
      procedure close_class (item: TClassType); virtual;
      procedure open_interface (item: TInterfaceType); virtual;
      procedure close_interface (item: TInterfaceType); virtual;
      procedure on_field (item: TFieldItem); virtual;
      procedure add_field (item: TFieldDecl); virtual;
      procedure open_proc (item: TProcDecl); virtual;
      procedure close_proc (item: TProcDecl); virtual;
      procedure simple_type (item: TItem); virtual;
      procedure on_const (item: TConstDecl); virtual;
      procedure add_const (item: TConstDecl); virtual;
      procedure on_type (item: TTypeDecl); virtual;
      procedure add_type (item: TTypeDecl); virtual;
      procedure on_var (item: TVarItem); virtual;
      procedure add_var (item: TVarDecl); virtual;
      procedure on_proc (item: TProcDecl); virtual;
      procedure on_begin_proc (item: TProcDecl); virtual;
      procedure on_end_proc (item: TProcDecl); virtual;
      procedure on_tail_proc (item: TProcDecl); virtual;
      procedure on_import (item: TImportItem); virtual;
      procedure open_module (item: TItem); virtual;
      procedure on_module (item: TItem); virtual;
      procedure close_module (item: TItem); virtual;
      function test_1 : boolean;
      function test_2 : boolean;
      function test_3 : boolean;
      function test_4 : boolean;
      function test_label_ident : boolean;
      function test_range_type : boolean;
      function test_simple_expr : boolean;
      function test_term : boolean;
      function test_factor : boolean;
      function test_int_value_expr : boolean;
      function test_float_value_expr : boolean;
      function test_string_value_expr : boolean;
      function test_not_expr : boolean;
      function test_plus_expr : boolean;
      function test_minus_expr : boolean;
      function test_adr_expr : boolean;
      function test_nil_expr : boolean;
      function test_set_expr : boolean;
      function test_elem_sect : boolean;
      function test_elem_item : boolean;
      function test_expr : boolean;
      function test_string_type_expr : boolean;
      function test_reference : boolean;
      function test_variable : boolean;
      function test_ident_expr : boolean;
      function test_sub_expr : boolean;
      function test_super_expr : boolean;
      function test_index_expr : boolean;
      function test_index_expr_list : boolean;
      function test_index_expr_item : boolean;
      function test_call_expr : boolean;
      function test_arg_list : boolean;
      function test_arg_item : boolean;
      function test_deref_expr : boolean;
      function test_field_expr : boolean;
      function test_enum_type : boolean;
      function test_enum_sect : boolean;
      function test_enum_item : boolean;
   end;

   TItem = class
   public
      src_line : integer;
      src_col : integer;
   end;

   TBasic = class (TItem)
   public
      src_file: integer;
      src_line: integer;
      src_column: integer;

      constructor create;

      function conv_TBasic : TBasic; virtual;
   end;

   TExpr = class (TItem)
   public
      fce: TFce;

      constructor create;

      function conv_TExpr : TExpr; virtual;
   end;

   TBinaryExpr = class (TExpr)
   public
      left: TExpr;
      right: TExpr;

      constructor create;

      function conv_TBinaryExpr : TBinaryExpr; virtual;
   end;

   TComponentsItem = class (TItem)
   public
      acs: TAccess;
      members: TDeclGroup;

      constructor create;

      function conv_TComponentsItem : TComponentsItem; virtual;
   end;

   TParamItem = class (TItem)
   public
      mode: TParamMode;
      items: array of TParamIdent;
      typ: TType;
      ini: TExpr;

      constructor create;

      function conv_TParamItem : TParamItem; virtual;
   end;

   TModule = class (TItem)
   public
      intf_imports: TImportSect;
      impl_imports: TImportSect;
      intf_decl: TDeclGroup;
      impl_decl: TDeclGroup;
      init: TStatSeq;
      finish: TStatSeq;

      constructor create;

      function conv_TModule : TModule; virtual;
   end;

   TLabelIdent = class (TItem)
   public
      id: string;

      constructor create;

      function conv_TLabelIdent : TLabelIdent; virtual;
   end;

   TQualName = class (TItem)
   public
      id: string;
      items: array of TContName;

      constructor create;

      function conv_TQualName : TQualName; virtual;
   end;

   TContName = class (TItem)
   public
      id: string;

      constructor create;

      function conv_TContName : TContName; virtual;
   end;

   TType = class (TItem)
   public

      constructor create;

      function conv_TType : TType; virtual;
   end;

   TAliasType = class (TType)
   public
      alias_name: TQualName;

      constructor create;

      function conv_TAliasType : TAliasType; virtual;
   end;

   TStringType = class (TType)
   public
      lim: TExpr;

      constructor create;

      function conv_TStringType : TStringType; virtual;
   end;

   TFileType = class (TType)
   public
      elem: TType;

      constructor create;

      function conv_TFileType : TFileType; virtual;
   end;

   TInxItem = class (TItem)
   public
      ref: TExpr;

      constructor create;

      function conv_TInxItem : TInxItem; virtual;
   end;

   TInxList = class (TItem)
   public
      items: array of TInxItem;

      constructor create;

      function conv_TInxList : TInxList; virtual;
   end;

   TArgItem = class (TItem)
   public
      value: TExpr;
      width: TExpr;
      digits: TExpr;

      constructor create;

      function conv_TArgItem : TArgItem; virtual;
   end;

   TArgSect = class (TItem)
   public
      items: array of TArgItem;

      constructor create;

      function conv_TArgSect : TArgSect; virtual;
   end;

   TElemSect = class (TItem)
   public
      items: array of TElemItem;

      constructor create;

      function conv_TElemSect : TElemSect; virtual;
   end;

   TElemItem = class (TItem)
   public
      low: TExpr;
      high: TExpr;

      constructor create;

      function conv_TElemItem : TElemItem; virtual;
   end;

   TStructSect = class (TItem)
   public
      name: string;
      value: TExpr;
      items: array of TStructSect;

      constructor create;

      function conv_TStructSect : TStructSect; virtual;
   end;

   TIdentExpr = class (TExpr)
   public
      name: string;

      constructor create;

      function conv_TIdentExpr : TIdentExpr; virtual;
   end;

   TIntValueExpr = class (TExpr)
   public
      value: string;

      constructor create;

      function conv_TIntValueExpr : TIntValueExpr; virtual;
   end;

   TFltValueExpr = class (TExpr)
   public
      value: string;

      constructor create;

      function conv_TFltValueExpr : TFltValueExpr; virtual;
   end;

   TStrValueExpr = class (TExpr)
   public
      value: string;

      constructor create;

      function conv_TStrValueExpr : TStrValueExpr; virtual;
   end;

   TNilExpr = class (TExpr)
   public

      constructor create;

      function conv_TNilExpr : TNilExpr; virtual;
   end;

   TStructExpr = class (TExpr)
   public
      value: TExpr;

      constructor create;

      function conv_TStructExpr : TStructExpr; virtual;
   end;

   TNotExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TNotExpr : TNotExpr; virtual;
   end;

   TPlusExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TPlusExpr : TPlusExpr; virtual;
   end;

   TMinusExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TMinusExpr : TMinusExpr; virtual;
   end;

   TAdrExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TAdrExpr : TAdrExpr; virtual;
   end;

   TSetExpr = class (TExpr)
   public
      list: TElemSect;

      constructor create;

      function conv_TSetExpr : TSetExpr; virtual;
   end;

   TSuperExpr = class (TExpr)
   public
      name: string;

      constructor create;

      function conv_TSuperExpr : TSuperExpr; virtual;
   end;

   TStringExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TStringExpr : TStringExpr; virtual;
   end;

   TIndexExpr = class (TExpr)
   public
      left: TExpr;
      list: TInxList;

      constructor create;

      function conv_TIndexExpr : TIndexExpr; virtual;
   end;

   TCallExpr = class (TExpr)
   public
      func: TExpr;
      list: TArgSect;

      constructor create;

      function conv_TCallExpr : TCallExpr; virtual;
   end;

   TDerefExpr = class (TExpr)
   public
      param: TExpr;

      constructor create;

      function conv_TDerefExpr : TDerefExpr; virtual;
   end;

   TFieldExpr = class (TExpr)
   public
      param: TExpr;
      name: string;

      constructor create;

      function conv_TFieldExpr : TFieldExpr; virtual;
   end;

   TStat = class (TItem)
   public

      constructor create;

      function conv_TStat : TStat; virtual;
   end;

   TGotoStat = class (TStat)
   public
      goto_lab: TLabelIdent;

      constructor create;

      function conv_TGotoStat : TGotoStat; virtual;
   end;

   TBlockStat = class (TStat)
   public
      body_seq: TStatSeq;

      constructor create;

      function conv_TBlockStat : TBlockStat; virtual;
   end;

   TStatSeq = class (TItem)
   public
      items: array of TStat;

      constructor create;

      function conv_TStatSeq : TStatSeq; virtual;
   end;

   TIfStat = class (TStat)
   public
      cond_expr: TExpr;
      then_stat: TStat;
      else_stat: TStat;

      constructor create;

      function conv_TIfStat : TIfStat; virtual;
   end;

   TCaseStat = class (TStat)
   public
      case_expr: TExpr;
      case_list: TCaseSect;
      else_seq: TStatSeq;

      constructor create;

      function conv_TCaseStat : TCaseStat; virtual;
   end;

   TCaseSect = class (TItem)
   public
      items: array of TCaseItem;

      constructor create;

      function conv_TCaseSect : TCaseSect; virtual;
   end;

   TCaseItem = class (TItem)
   public
      sel_list: TElemSect;
      sel_stat: TStat;

      constructor create;

      function conv_TCaseItem : TCaseItem; virtual;
   end;

   TWhileStat = class (TStat)
   public
      cond_expr: TExpr;
      body_stat: TStat;

      constructor create;

      function conv_TWhileStat : TWhileStat; virtual;
   end;

   TRepeatStat = class (TStat)
   public
      body_seq: TStatSeq;
      until_expr: TExpr;

      constructor create;

      function conv_TRepeatStat : TRepeatStat; virtual;
   end;

   TForStat = class (TStat)
   public
      var_expr: TExpr;
      from_expr: TExpr;
      incr: boolean;
      to_expr: TExpr;
      body_stat: TStat;

      constructor create;

      function conv_TForStat : TForStat; virtual;
   end;

   TWithStat = class (TStat)
   public
      with_list: TWithSect;
      body_stat: TStat;

      constructor create;

      function conv_TWithStat : TWithStat; virtual;
   end;

   TWithSect = class (TItem)
   public
      items: array of TWithItem;

      constructor create;

      function conv_TWithSect : TWithSect; virtual;
   end;

   TWithItem = class (TItem)
   public
      expr: TExpr;

      constructor create;

      function conv_TWithItem : TWithItem; virtual;
   end;

   TRaiseStat = class (TStat)
   public
      raise_expr: TExpr;

      constructor create;

      function conv_TRaiseStat : TRaiseStat; virtual;
   end;

   TTryStat = class (TStat)
   public
      body_seq: TStatSeq;
      finally_branch: TFinallyPart;
      except_branch: TExceptPart;

      constructor create;

      function conv_TTryStat : TTryStat; virtual;
   end;

   TFinallyPart = class (TItem)
   public
      finally_seq: TStatSeq;

      constructor create;

      function conv_TFinallyPart : TFinallyPart; virtual;
   end;

   TExceptPart = class (TItem)
   public
      on_list: TOnSect;
      else_seq: TStatSeq;

      constructor create;

      function conv_TExceptPart : TExceptPart; virtual;
   end;

   TOnSect = class (TItem)
   public
      items: array of TOnItem;
      semicolon: boolean;

      constructor create;

      function conv_TOnSect : TOnSect; virtual;
   end;

   TOnItem = class (TItem)
   public
      on_ident: string;
      on_type: TType;
      body_stat: TStat;

      constructor create;

      function conv_TOnItem : TOnItem; virtual;
   end;

   TEmptyStat = class (TStat)
   public

      constructor create;

      function conv_TEmptyStat : TEmptyStat; virtual;
   end;

   TAssignStat = class (TStat)
   public
      left_expr: TExpr;
      right_expr: TExpr;

      constructor create;

      function conv_TAssignStat : TAssignStat; virtual;
   end;

   TCallStat = class (TStat)
   public
      call_expr: TExpr;

      constructor create;

      function conv_TCallStat : TCallStat; virtual;
   end;

   TLabeledTStat = class (TStat)
   public
      lab: TLabelIdent;
      body: TStat;

      constructor create;

      function conv_TLabeledTStat : TLabeledTStat; virtual;
   end;

   TParamIdent = class (TItem)
   public
      name: string;

      constructor create;

      function conv_TParamIdent : TParamIdent; virtual;
   end;

   TParamSect = class (TItem)
   public
      items: array of TParamItem;

      constructor create;

      function conv_TParamSect : TParamSect; virtual;
   end;

   TClassType = class (TType)
   public
      parent: TType;
      ifc_list: TInterfaceSect;
      components: TComponetsSect;

      constructor create;

      function conv_TClassType : TClassType; virtual;
   end;

   TInterfaceType = class (TType)
   public
      ifc_list: TInterfaceSect;
      components: TComponetsSect;

      constructor create;

      function conv_TInterfaceType : TInterfaceType; virtual;
   end;

   TInterfaceSect = class (TItem)
   public
      items: array of TIntefaceItem;

      constructor create;

      function conv_TInterfaceSect : TInterfaceSect; virtual;
   end;

   TIntefaceItem = class (TItem)
   public
      ifc: TType;

      constructor create;

      function conv_TIntefaceItem : TIntefaceItem; virtual;
   end;

   TComponetsSect = class (TItem)
   public
      items: array of TComponentsItem;

      constructor create;

      function conv_TComponetsSect : TComponetsSect; virtual;
   end;

   TDeclGroup = class (TItem)
   public
      items: array of TDeclSect;

      constructor create;

      function conv_TDeclGroup : TDeclGroup; virtual;
   end;

   TDeclSect = class (TItem)
   public

      constructor create;

      function conv_TDeclSect : TDeclSect; virtual;
   end;

   TFieldItem = class (TItem)
   public
      name: string;

      constructor create;

      function conv_TFieldItem : TFieldItem; virtual;
   end;

   TFieldDecl = class (TDeclSect)
   public
      items: array of TFieldItem;
      typ: TType;

      constructor create;

      function conv_TFieldDecl : TFieldDecl; virtual;
   end;

   TPropertyDecl = class (TDeclSect)
   public
      name: string;
      param_list: TParamSect;
      typ: TType;
      a_read: TExpr;
      a_write: TExpr;
      a_stored: boolean;
      a_default: boolean;
      a_nodefault: boolean;
      a_implements: TInterfaceSect;
      a_def_array: boolean;

      constructor create;

      function conv_TPropertyDecl : TPropertyDecl; virtual;
   end;

   TEnumType = class (TType)
   public
      elements: TEnumSect;

      constructor create;

      function conv_TEnumType : TEnumType; virtual;
   end;

   TEnumSect = class (TItem)
   public
      items: array of TEnumItem;

      constructor create;

      function conv_TEnumSect : TEnumSect; virtual;
   end;

   TEnumItem = class (TItem)
   public
      name: string;

      constructor create;

      function conv_TEnumItem : TEnumItem; virtual;
   end;

   TArrayType = class (TType)
   public
      index_list: TIndexTypeSect;
      elem: TType;

      constructor create;

      function conv_TArrayType : TArrayType; virtual;
   end;

   TIndexTypeSect = class (TItem)
   public
      items: array of TIndexTypeItem;

      constructor create;

      function conv_TIndexTypeSect : TIndexTypeSect; virtual;
   end;

   TIndexTypeItem = class (TItem)
   public
      index: TType;

      constructor create;

      function conv_TIndexTypeItem : TIndexTypeItem; virtual;
   end;

   TRecordType = class (TType)
   public
      a_packed: boolean;
      fields: TFieldDeclGroup;

      constructor create;

      function conv_TRecordType : TRecordType; virtual;
   end;

   TFieldDeclGroup = class (TItem)
   public
      items: array of TFieldDecl;

      constructor create;

      function conv_TFieldDeclGroup : TFieldDeclGroup; virtual;
   end;

   TPointerType = class (TType)
   public
      elem: TType;

      constructor create;

      function conv_TPointerType : TPointerType; virtual;
   end;

   TSetType = class (TType)
   public
      elem: TType;

      constructor create;

      function conv_TSetType : TSetType; virtual;
   end;

   TClassOfType = class (TType)
   public
      elem: TType;

      constructor create;

      function conv_TClassOfType : TClassOfType; virtual;
   end;

   TProcType = class (TType)
   public
      style: TStyle;
      call_conv: TCall;
      param_list: TParamSect;
      answer: TType;
      of_object: boolean;

      constructor create;

      function conv_TProcType : TProcType; virtual;
   end;

   TSubrangeType = class (TType)
   public
      low: TExpr;
      high: TExpr;

      constructor create;

      function conv_TSubrangeType : TSubrangeType; virtual;
   end;

   TLabelDecl = class (TItem)
   public
      name: TLabelIdent;

      constructor create;

      function conv_TLabelDecl : TLabelDecl; virtual;
   end;

   TLabelSect = class (TDeclSect)
   public
      items: array of TLabelDecl;

      constructor create;

      function conv_TLabelSect : TLabelSect; virtual;
   end;

   TConstDecl = class (TItem)
   public
      name: string;
      typ: TType;
      val: TExpr;

      constructor create;

      function conv_TConstDecl : TConstDecl; virtual;
   end;

   TConstSect = class (TDeclSect)
   public
      items: array of TConstDecl;

      constructor create;

      function conv_TConstSect : TConstSect; virtual;
   end;

   TTypeDecl = class (TItem)
   public
      name: string;
      typ: TType;

      constructor create;

      function conv_TTypeDecl : TTypeDecl; virtual;
   end;

   TTypeSect = class (TDeclSect)
   public
      items: array of TTypeDecl;

      constructor create;

      function conv_TTypeSect : TTypeSect; virtual;
   end;

   TVarItem = class (TItem)
   public
      name: string;

      constructor create;

      function conv_TVarItem : TVarItem; virtual;
   end;

   TVarDecl = class (TItem)
   public
      items: array of TVarItem;
      typ: TType;
      ini: TExpr;

      constructor create;

      function conv_TVarDecl : TVarDecl; virtual;
   end;

   TVarSect = class (TDeclSect)
   public
      items: array of TVarDecl;

      constructor create;

      function conv_TVarSect : TVarSect; virtual;
   end;

   TProcDecl = class (TDeclSect)
   public
      style: TStyle;
      call_conv: TCall;
      a_virtual: boolean;
      a_dynamic: boolean;
      a_override: boolean;
      a_abstract: boolean;
      a_static: boolean;
      proc_name: TQualName;
      param_list: TParamSect;
      answer: TType;
      a_forward: boolean;
      external_spec: boolean;
      a_inline: boolean;
      local: TDeclGroup;
      body: TStatSeq;
      a_external: boolean;
      a_lib: TExpr;

      constructor create;

      function conv_TProcDecl : TProcDecl; virtual;
   end;

   TImportItem = class (TItem)
   public
      name: string;
      path: string;

      constructor create;

      function conv_TImportItem : TImportItem; virtual;
   end;

   TImportSect = class (TItem)
   public
      items: array of TImportItem;

      constructor create;

      function conv_TImportSect : TImportSect; virtual;
   end;

   TUnitModule = class (TModule)
   public
      name: string;
      no_begin: boolean;

      constructor create;

      function conv_TUnitModule : TUnitModule; virtual;
   end;

   TProgramModule = class (TModule)
   public
      name: string;

      constructor create;

      function conv_TProgramModule : TProgramModule; virtual;
   end;

   TLibraryModule = class (TModule)
   public
      name: string;

      constructor create;

      function conv_TLibraryModule : TLibraryModule; virtual;
   end;

   TTermExpr = class (TBinaryExpr)
   public

      constructor create;

      function conv_TTermExpr : TTermExpr; virtual;
   end;

   TSimpleExpr = class (TBinaryExpr)
   public

      constructor create;

      function conv_TSimpleExpr : TSimpleExpr; virtual;
   end;

   TCompleteExpr = class (TBinaryExpr)
   public

      constructor create;

      function conv_TCompleteExpr : TCompleteExpr; virtual;
   end;


implementation

const set_0 : array [0..14] of byte = (0, 65, 0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
// set_0 :  ( . [ ^

const set_1 : array [0..14] of byte = (0, 4, 1, 128, 2, 8, 0, 0, 32, 0, 0, 128, 1, 0, 0);
// set_1 :  * / and as div mod shl shr

const set_2 : array [0..14] of byte = (0, 40, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 1);
// set_2 :  + - or xor

const set_3 : array [0..14] of byte = (0, 0, 240, 3, 0, 0, 0, 32, 4, 0, 0, 0, 0, 0, 0);
// set_3 :  < <= <> = > >= in is

const set_4 : array [0..14] of byte = (46, 41, 0, 12, 0, 0, 0, 64, 64, 1, 0, 0, 8, 0, 0);
// set_4 :  identifier number real_number string_literal ( + - @ [ inherited nil not string

const set_5 : array [0..14] of byte = (46, 41, 8, 12, 24, 0, 64, 70, 64, 1, 0, 17, 72, 96, 0);
// set_5 :  identifier number real_number string_literal ( + - ; @ [ begin case for goto if inherited nil not raise repeat string try while with

const set_6 : array [0..14] of byte = (0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 226, 0, 0, 0, 0);
// set_6 :  automated private protected public published

const set_7 : array [0..14] of byte = (2, 0, 0, 0, 64, 5, 0, 1, 0, 0, 20, 0, 0, 0, 0);
// set_7 :  identifier class constructor destructor function procedure property

const set_8 : array [0..14] of byte = (0, 0, 0, 0, 64, 5, 0, 1, 0, 0, 4, 0, 0, 0, 0);
// set_8 :  class constructor destructor function procedure

const set_9 : array [0..14] of byte = (0, 0, 0, 64, 0, 64, 0, 0, 0, 64, 0, 0, 0, 16, 0);
// set_9 :  abstract dynamic override virtual

const set_10 : array [0..14] of byte = (0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 1, 40, 2, 0, 0);
// set_10 :  cdecl pascal register safecall stdcall

const set_11 : array [0..14] of byte = (0, 0, 0, 0, 200, 5, 0, 1, 9, 0, 4, 0, 128, 8, 0);
// set_11 :  begin class const constructor destructor function inline label procedure type var

const set_12 : array [0..14] of byte = (0, 0, 0, 0, 192, 5, 0, 1, 0, 0, 4, 0, 128, 8, 0);
// set_12 :  class const constructor destructor function procedure type var

const set_13 : array [0..14] of byte = (0, 0, 0, 0, 192, 5, 0, 1, 8, 0, 4, 0, 128, 8, 0);
// set_13 :  class const constructor destructor function label procedure type var

function Parser.parse_label_ident : TLabelIdent;
begin
   result := TLabelIdent.create;
   storeLocation (result);
   result.id := readIdent;
   result := result;
end;

function Parser.parse_qualified_name : TQualName;
begin
   result := TQualName.create;
   storeLocation (result);
   result.id := readIdent;
   while isSymbol (DOT) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_cont_name ();
   end;
   result := result;
end;

function Parser.parse_cont_name : TContName;
begin
   result := TContName.create;
   storeLocation (result);
   checkSymbol (DOT);
   result.id := readIdent;
   result := result;
end;

function Parser.parse_ifc_type : TType;
begin
   result := nil;
   result := parse_simple_alias_type ();
   result := result;
end;

function Parser.parse_param_type : TType;
begin
   result := nil;
   if isSymbol (identifier) then begin
      result := parse_simple_alias_type ();
   end
   else if isSymbol (keyword_string) then begin
      result := parse_simple_string_type ();
   end
   else if isSymbol (keyword_file) then begin
      result := parse_simple_file_type ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_result_type : TType;
begin
   result := nil;
   if isSymbol (identifier) then begin
      result := parse_simple_alias_type ();
   end
   else if isSymbol (keyword_string) then begin
      result := parse_simple_string_type ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_simple_alias_type : TAliasType;
begin
   result := TAliasType.create;
   storeLocation (result);
   result.alias_name := parse_qualified_name ();
   result := result;
end;

function Parser.parse_simple_string_type : TStringType;
begin
   result := TStringType.create;
   storeLocation (result);
   checkSymbol (keyword_string);
   result := result;
end;

function Parser.parse_simple_file_type : TFileType;
begin
   result := TFileType.create;
   storeLocation (result);
   checkSymbol (keyword_file);
   result := result;
end;

function Parser.parse_index_expr_item : TInxItem;
begin
   result := TInxItem.create;
   storeLocation (result);
   result.ref := parse_expr ();
   result := result;
end;

function Parser.parse_index_expr_list : TInxList;
begin
   result := TInxList.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_index_expr_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_index_expr_item ();
   end;
   result := result;
end;

function Parser.parse_arg_item : TArgItem;
begin
   result := TArgItem.create;
   storeLocation (result);
   result.value := parse_expr ();
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.width := parse_expr ();
      if isSymbol (COLON) then begin
         checkSymbol (COLON);
         result.digits := parse_expr ();
      end;
   end;
   result := result;
end;

function Parser.parse_arg_list : TArgSect;
begin
   result := TArgSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_arg_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_arg_item ();
   end;
   result := result;
end;

function Parser.parse_elem_sect : TElemSect;
begin
   result := TElemSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_elem_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_elem_item ();
   end;
   result := result;
end;

function Parser.parse_elem_item : TElemItem;
begin
   result := TElemItem.create;
   storeLocation (result);
   result.low := parse_expr ();
   if isSymbol (RANGE) then begin
      checkSymbol (RANGE);
      result.high := parse_expr ();
   end;
   result := result;
end;

function Parser.parse_struct_item : TStructSect;
begin
   result := TStructSect.create;
   storeLocation (result);
   if isSymbol (identifier) then begin
      result.name := readIdent;
      checkSymbol (COLON);
   end;
   result.value := parse_expr ();
   result := result;
end;

function Parser.parse_struct_sect : TStructSect;
begin
   result := TStructSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_struct_item ();
   if isSymbol (COMMA) or isSymbol (SEMICOLON) then begin
      if isSymbol (COMMA) then begin
         checkSymbol (COMMA);
         setLength (result.items, length (result.items) + 1); 
         result.items [ high (result.items)] := parse_struct_item ();
         while isSymbol (COMMA) do begin
            checkSymbol (COMMA);
            setLength (result.items, length (result.items) + 1); 
            result.items [ high (result.items)] := parse_struct_item ();
         end;
      end
      else if isSymbol (SEMICOLON) then begin
         checkSymbol (SEMICOLON);
         setLength (result.items, length (result.items) + 1); 
         result.items [ high (result.items)] := parse_struct_item ();
         while isSymbol (SEMICOLON) do begin
            checkSymbol (SEMICOLON);
            setLength (result.items, length (result.items) + 1); 
            result.items [ high (result.items)] := parse_struct_item ();
         end;
      end
      else begin
         stop ();
      end;
   end;
   result := result;
end;

function Parser.parse_ident_expr : TIdentExpr;
begin
   result := TIdentExpr.create;
   storeLocation (result);
   result.name := readIdent;
   on_ident_expr (result);
   result := result;
end;

function Parser.parse_int_value_expr : TIntValueExpr;
begin
   result := TIntValueExpr.create;
   storeLocation (result);
   result.value := readNumber;
   result := result;
end;

function Parser.parse_float_value_expr : TFltValueExpr;
begin
   result := TFltValueExpr.create;
   storeLocation (result);
   result.value := readNumber;
   result := result;
end;

function Parser.parse_string_value_expr : TStrValueExpr;
begin
   result := TStrValueExpr.create;
   storeLocation (result);
   result.value := readString;
   result := result;
end;

function Parser.parse_nil_expr : TNilExpr;
begin
   result := TNilExpr.create;
   storeLocation (result);
   checkSymbol (keyword_nil);
   result := result;
end;

function Parser.parse_sub_expr : TStructExpr;
begin
   result := TStructExpr.create;
   storeLocation (result);
   checkSymbol (LPAREN);
   result.value := parse_expr ();
   checkSymbol (RPAREN);
   result := result;
end;

function Parser.parse_not_expr : TNotExpr;
begin
   result := TNotExpr.create;
   storeLocation (result);
   checkSymbol (keyword_not);
   result.param := parse_factor ();
   result := result;
end;

function Parser.parse_plus_expr : TPlusExpr;
begin
   result := TPlusExpr.create;
   storeLocation (result);
   checkSymbol (PLUS);
   result.param := parse_factor ();
   result := result;
end;

function Parser.parse_minus_expr : TMinusExpr;
begin
   result := TMinusExpr.create;
   storeLocation (result);
   checkSymbol (MINUS);
   result.param := parse_factor ();
   result := result;
end;

function Parser.parse_adr_expr : TAdrExpr;
begin
   result := TAdrExpr.create;
   storeLocation (result);
   checkSymbol (ADDRESS);
   result.param := parse_factor ();
   result := result;
end;

function Parser.parse_set_expr : TSetExpr;
begin
   result := TSetExpr.create;
   storeLocation (result);
   checkSymbol (LBRACKET);
   result.list := parse_elem_sect ();
   checkSymbol (RBRACKET);
   result := result;
end;

function Parser.parse_super_expr : TSuperExpr;
begin
   result := TSuperExpr.create;
   storeLocation (result);
   checkSymbol (keyword_inherited);
   result.name := readIdent;
   result := result;
end;

function Parser.parse_string_type_expr : TStringExpr;
begin
   result := TStringExpr.create;
   storeLocation (result);
   checkSymbol (keyword_string);
   checkSymbol (LPAREN);
   result.param := parse_expr ();
   checkSymbol (RPAREN);
   result := result;
end;

function Parser.parse_variable : TExpr;
begin
   result := nil;
   if isSymbol (identifier) then begin
      result := parse_ident_expr ();
   end
   else if isSymbol (LPAREN) then begin
      result := parse_sub_expr ();
   end
   else if isSymbol (keyword_inherited) then begin
      result := parse_super_expr ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_reference : TExpr;
begin
   result := nil;
   result := parse_variable ();
   while isSymbol (LBRACKET) or isSymbol (LPAREN) or isSymbol (ARROW) or isSymbol (DOT) do begin
      if isSymbol (LBRACKET) then begin
         result := parse_index_expr (result);
      end
      else if isSymbol (LPAREN) then begin
         result := parse_call_expr (result);
      end
      else if isSymbol (ARROW) then begin
         result := parse_deref_expr (result);
      end
      else if isSymbol (DOT) then begin
         result := parse_field_expr (result);
      end
      else begin
         stop ();
      end;
   end;
   result := result;
end;

function Parser.parse_index_expr (store : TExpr) : TIndexExpr;
begin
   result := TIndexExpr.create;
   storeLocation (result);
   result.left := store;
   checkSymbol (LBRACKET);
   result.list := parse_index_expr_list ();
   checkSymbol (RBRACKET);
   result := result;
end;

function Parser.parse_call_expr (store : TExpr) : TCallExpr;
begin
   result := TCallExpr.create;
   storeLocation (result);
   result.func := store;
   checkSymbol (LPAREN);
   result.list := parse_arg_list ();
   checkSymbol (RPAREN);
   result := result;
end;

function Parser.parse_deref_expr (store : TExpr) : TDerefExpr;
begin
   result := TDerefExpr.create;
   storeLocation (result);
   result.param := store;
   checkSymbol (ARROW);
   result := result;
end;

function Parser.parse_field_expr (store : TExpr) : TFieldExpr;
begin
   result := TFieldExpr.create;
   storeLocation (result);
   result.param := store;
   checkSymbol (DOT);
   result.name := readIdent;
   on_field_expr (result);
   result := result;
end;

function Parser.parse_factor : TExpr;
begin
   result := nil;
   if isSymbol (number) then begin
      result := parse_int_value_expr ();
   end
   else if isSymbol (real_number) then begin
      result := parse_float_value_expr ();
   end
   else if isSymbol (string_literal) then begin
      result := parse_string_value_expr ();
   end
   else if isSymbol (keyword_not) then begin
      result := parse_not_expr ();
   end
   else if isSymbol (PLUS) then begin
      result := parse_plus_expr ();
   end
   else if isSymbol (MINUS) then begin
      result := parse_minus_expr ();
   end
   else if isSymbol (ADDRESS) then begin
      result := parse_adr_expr ();
   end
   else if isSymbol (keyword_nil) then begin
      result := parse_nil_expr ();
   end
   else if isSymbol (LBRACKET) then begin
      result := parse_set_expr ();
   end
   else if isSymbol (keyword_string) and test_1 then begin
      result := parse_string_type_expr ();
   end
   else if isSymbol (identifier) or isSymbol (LPAREN) or isSymbol (keyword_inherited) then begin
      result := parse_reference ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_term : TExpr;
var store1: TExpr;
var result0: TTermExpr;
begin
   result := nil;
   result := parse_factor ();
   while isSymbol (STAR) or isSymbol (SLASH) or isSymbol (keyword_div) or isSymbol (keyword_mod) or isSymbol (keyword_shl) or isSymbol (keyword_shr) or isSymbol (keyword_and) or isSymbol (keyword_as) do begin
      store1 := result;
      result0 := TTermExpr.create;
      storeLocation (result0);
      result0.left := store1;
      result := result0;
      if isSymbol (STAR) then begin
         checkSymbol (STAR);
         result0.fce := MulExp;
      end
      else if isSymbol (SLASH) then begin
         checkSymbol (SLASH);
         result0.fce := RDivExp;
      end
      else if isSymbol (keyword_div) then begin
         checkSymbol (keyword_div);
         result0.fce := DivExp;
      end
      else if isSymbol (keyword_mod) then begin
         checkSymbol (keyword_mod);
         result0.fce := ModExp;
      end
      else if isSymbol (keyword_shl) then begin
         checkSymbol (keyword_shl);
         result0.fce := ShlExp;
      end
      else if isSymbol (keyword_shr) then begin
         checkSymbol (keyword_shr);
         result0.fce := ShrExp;
      end
      else if isSymbol (keyword_and) then begin
         checkSymbol (keyword_and);
         result0.fce := AndExp;
      end
      else if isSymbol (keyword_as) then begin
         checkSymbol (keyword_as);
         result0.fce := AsExp;
      end
      else begin
         stop ();
      end;
      result0.right := parse_factor ();
   end;
   result := result;
end;

function Parser.parse_simple_expr : TExpr;
var store1: TExpr;
var result0: TSimpleExpr;
begin
   result := nil;
   result := parse_term ();
   while isSymbol (PLUS) or isSymbol (MINUS) or isSymbol (keyword_or) or isSymbol (keyword_xor) do begin
      store1 := result;
      result0 := TSimpleExpr.create;
      storeLocation (result0);
      result0.left := store1;
      result := result0;
      if isSymbol (PLUS) then begin
         checkSymbol (PLUS);
         result0.fce := AddExp;
      end
      else if isSymbol (MINUS) then begin
         checkSymbol (MINUS);
         result0.fce := SubExp;
      end
      else if isSymbol (keyword_or) then begin
         checkSymbol (keyword_or);
         result0.fce := OrExp;
      end
      else if isSymbol (keyword_xor) then begin
         checkSymbol (keyword_xor);
         result0.fce := XorExp;
      end
      else begin
         stop ();
      end;
      result0.right := parse_term ();
   end;
   result := result;
end;

function Parser.parse_expr : TExpr;
var store1: TExpr;
var result0: TCompleteExpr;
begin
   result := nil;
   result := parse_simple_expr ();
   if isSymbol (EQUAL) or isSymbol (UNEQUAL) or isSymbol (LESS) or isSymbol (GREATER) or isSymbol (LESS_OR_EQUAL) or isSymbol (GREATER_OR_EQUAL) or isSymbol (keyword_in) or isSymbol (keyword_is) then begin
      store1 := result;
      result0 := TCompleteExpr.create;
      storeLocation (result0);
      result0.left := store1;
      result := result0;
      if isSymbol (EQUAL) then begin
         checkSymbol (EQUAL);
         result0.fce := EqExp;
      end
      else if isSymbol (UNEQUAL) then begin
         checkSymbol (UNEQUAL);
         result0.fce := NeExp;
      end
      else if isSymbol (LESS) then begin
         checkSymbol (LESS);
         result0.fce := LtExp;
      end
      else if isSymbol (GREATER) then begin
         checkSymbol (GREATER);
         result0.fce := GtExp;
      end
      else if isSymbol (LESS_OR_EQUAL) then begin
         checkSymbol (LESS_OR_EQUAL);
         result0.fce := LeExp;
      end
      else if isSymbol (GREATER_OR_EQUAL) then begin
         checkSymbol (GREATER_OR_EQUAL);
         result0.fce := GeExp;
      end
      else if isSymbol (keyword_in) then begin
         checkSymbol (keyword_in);
         result0.fce := InExp;
      end
      else if isSymbol (keyword_is) then begin
         checkSymbol (keyword_is);
         result0.fce := IsExp;
      end
      else begin
         stop ();
      end;
      result0.right := parse_simple_expr ();
   end;
   result := result;
end;

function Parser.parse_goto_stat : TGotoStat;
begin
   result := TGotoStat.create;
   storeLocation (result);
   checkSymbol (keyword_goto);
   result.goto_lab := parse_label_ident ();
   result := result;
end;

function Parser.parse_begin_stat : TBlockStat;
begin
   result := TBlockStat.create;
   storeLocation (result);
   checkSymbol (keyword_begin);
   result.body_seq := parse_stat_list ();
   checkSymbol (keyword_end);
   result := result;
end;

function Parser.parse_stat_list : TStatSeq;
begin
   result := TStatSeq.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_stat ();
   while isSymbol (SEMICOLON) do begin
      checkSymbol (SEMICOLON);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_stat ();
   end;
   result := result;
end;

function Parser.parse_inner_stat : TStat;
begin
   result := nil;
   result := parse_stat ();
   result := result;
end;

function Parser.parse_if_stat : TIfStat;
begin
   result := TIfStat.create;
   storeLocation (result);
   checkSymbol (keyword_if);
   result.cond_expr := parse_expr ();
   checkSymbol (keyword_then);
   result.then_stat := parse_inner_stat ();
   if isSymbol (keyword_else) then begin
      checkSymbol (keyword_else);
      result.else_stat := parse_inner_stat ();
   end;
   result := result;
end;

function Parser.parse_case_stat : TCaseStat;
begin
   result := TCaseStat.create;
   storeLocation (result);
   checkSymbol (keyword_case);
   result.case_expr := parse_expr ();
   checkSymbol (keyword_of);
   result.case_list := parse_case_sect ();
   if isSymbol (keyword_else) then begin
      checkSymbol (keyword_else);
      result.else_seq := parse_stat_list ();
   end;
   checkSymbol (keyword_end);
   result := result;
end;

function Parser.parse_case_sect : TCaseSect;
begin
   result := TCaseSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_case_item ();
   while isSymbol (SEMICOLON) do begin
      checkSymbol (SEMICOLON);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_case_item ();
   end;
   result := result;
end;

function Parser.parse_case_item : TCaseItem;
begin
   result := TCaseItem.create;
   storeLocation (result);
   result.sel_list := parse_elem_sect ();
   checkSymbol (COLON);
   result.sel_stat := parse_inner_stat ();
   result := result;
end;

function Parser.parse_while_stat : TWhileStat;
begin
   result := TWhileStat.create;
   storeLocation (result);
   checkSymbol (keyword_while);
   result.cond_expr := parse_expr ();
   checkSymbol (keyword_do);
   result.body_stat := parse_inner_stat ();
   result := result;
end;

function Parser.parse_repeat_stat : TRepeatStat;
begin
   result := TRepeatStat.create;
   storeLocation (result);
   checkSymbol (keyword_repeat);
   result.body_seq := parse_stat_list ();
   checkSymbol (keyword_until);
   result.until_expr := parse_expr ();
   result := result;
end;

function Parser.parse_for_stat : TForStat;
begin
   result := TForStat.create;
   storeLocation (result);
   checkSymbol (keyword_for);
   result.var_expr := parse_variable ();
   checkSymbol (ASSIGN);
   result.from_expr := parse_expr ();
   if isSymbol (keyword_to) then begin
      checkSymbol (keyword_to);
      result.incr := true;
   end
   else if isSymbol (keyword_downto) then begin
      checkSymbol (keyword_downto);
      result.incr := false;
   end
   else begin
      stop ();
   end;
   result.to_expr := parse_expr ();
   checkSymbol (keyword_do);
   result.body_stat := parse_inner_stat ();
   result := result;
end;

function Parser.parse_with_stat : TWithStat;
begin
   result := TWithStat.create;
   storeLocation (result);
   checkSymbol (keyword_with);
   result.with_list := parse_with_sect ();
   checkSymbol (keyword_do);
   result.body_stat := parse_inner_stat ();
   result := result;
end;

function Parser.parse_with_sect : TWithSect;
begin
   result := TWithSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_with_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_with_item ();
   end;
   result := result;
end;

function Parser.parse_with_item : TWithItem;
begin
   result := TWithItem.create;
   storeLocation (result);
   result.expr := parse_variable ();
   result := result;
end;

function Parser.parse_raise_stat : TRaiseStat;
begin
   result := TRaiseStat.create;
   storeLocation (result);
   checkSymbol (keyword_raise);
   if testSymbols (set_4) then begin
      result.raise_expr := parse_expr ();
   end;
   result := result;
end;

function Parser.parse_try_stat : TTryStat;
begin
   result := TTryStat.create;
   storeLocation (result);
   checkSymbol (keyword_try);
   result.body_seq := parse_stat_list ();
   if isSymbol (keyword_finally) then begin
      result.finally_branch := parse_finally_part ();
   end
   else if isSymbol (keyword_except) then begin
      result.except_branch := parse_except_part ();
   end
   else begin
      stop ();
   end;
   checkSymbol (keyword_end);
   result := result;
end;

function Parser.parse_finally_part : TFinallyPart;
begin
   result := TFinallyPart.create;
   storeLocation (result);
   checkSymbol (keyword_finally);
   result.finally_seq := parse_stat_list ();
   result := result;
end;

function Parser.parse_except_part : TExceptPart;
begin
   result := TExceptPart.create;
   storeLocation (result);
   checkSymbol (keyword_except);
   if isSymbol (keyword_on) then begin
      result.on_list := parse_on_sect ();
      if isSymbol (keyword_else) then begin
         checkSymbol (keyword_else);
         result.else_seq := parse_stat_list ();
      end;
   end
   else if testSymbols (set_5) then begin
      result.else_seq := parse_stat_list ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_on_sect : TOnSect;
begin
   result := TOnSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_on_item ();
   while isSymbol (SEMICOLON) do begin
      checkSymbol (SEMICOLON);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_on_item ();
   end;
   if isSymbol (SEMICOLON) then begin
      checkSymbol (SEMICOLON);
      result.semicolon := true;
   end;
   result := result;
end;

function Parser.parse_on_item : TOnItem;
begin
   result := TOnItem.create;
   storeLocation (result);
   checkSymbol (keyword_on);
   if isSymbol (identifier) then begin
      result.on_ident := readIdent;
      checkSymbol (COLON);
   end;
   result.on_type := parse_type ();
   checkSymbol (keyword_do);
   result.body_stat := parse_inner_stat ();
   result := result;
end;

function Parser.parse_empty_stat : TEmptyStat;
begin
   result := TEmptyStat.create;
   storeLocation (result);
   result := result;
end;

function Parser.parse_simple_stat : TStat;
var result1 : TExpr;
begin
   result := nil;
   result0 := parse_expr ();
   if isSymbol (ASSIGN) then begin
      result := parse_assign_stat (result0);
   end
   else begin
      result := parse_call_stat (result0);
   end;
   result := result;
end;

function Parser.parse_assign_stat (store : TExpr) : TAssignStat;
begin
   result := TAssignStat.create;
   storeLocation (result);
   result.left_expr := store;
   checkSymbol (ASSIGN);
   result.right_expr := parse_expr ();
   result := result;
end;

function Parser.parse_call_stat (store : TExpr) : TCallStat;
begin
   result := TCallStat.create;
   storeLocation (result);
   result.call_expr := store;
   result := result;
end;

function Parser.parse_labeled_stat : TLabeledTStat;
begin
   result := TLabeledTStat.create;
   storeLocation (result);
   result.lab := parse_label_ident ();
   checkSymbol (COLON);
   result.body := parse_stat ();
   result := result;
end;

function Parser.parse_stat : TStat;
begin
   result := nil;
   if isSymbol (identifier) and test_2 then begin
      result := parse_labeled_stat ();
   end
   else if testSymbols (set_4) then begin
      result := parse_simple_stat ();
   end
   else begin
      result := parse_empty_stat ();
   end
   else begin
      result := parse_goto_stat ();
   end
   else begin
      result := parse_begin_stat ();
   end
   else begin
      result := parse_if_stat ();
   end
   else begin
      result := parse_case_stat ();
   end
   else begin
      result := parse_while_stat ();
   end
   else begin
      result := parse_repeat_stat ();
   end
   else begin
      result := parse_for_stat ();
   end
   else begin
      result := parse_with_stat ();
   end
   else begin
      result := parse_raise_stat ();
   end
   else begin
      result := parse_try_stat ();
   end;
   result := result;
end;

function Parser.parse_param_ident : TParamIdent;
begin
   result := TParamIdent.create;
   storeLocation (result);
   result.name := readIdent;
   on_param (result);
   result := result;
end;

function Parser.parse_param_item : TParamItem;
begin
   result := TParamItem.create;
   storeLocation (result);
   if isSymbol (keyword_var) then begin
      checkSymbol (keyword_var);
      result.mode := VarParam;
   end
   else if isSymbol (keyword_const) then begin
      checkSymbol (keyword_const);
      result.mode := ConstParam;
   end
   else if isSymbol (keyword_out) then begin
      checkSymbol (keyword_out);
      result.mode := OutParam;
   end
   else begin
      result.mode := ValueParam;
   end;
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_param_ident ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_param_ident ();
   end;
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.typ := parse_param_type ();
      if isSymbol (EQUAL) then begin
         checkSymbol (EQUAL);
         result.ini := parse_expr ();
      end;
   end;
   add_param (result);
   result := result;
end;

function Parser.parse_formal_param_list : TParamSect;
begin
   result := TParamSect.create;
   storeLocation (result);
   if isSymbol (LPAREN) then begin
      checkSymbol (LPAREN);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_param_item ();
      while isSymbol (SEMICOLON) do begin
         checkSymbol (SEMICOLON);
         setLength (result.items, length (result.items) + 1); 
         result.items [ high (result.items)] := parse_param_item ();
      end;
      checkSymbol (RPAREN);
   end;
   result := result;
end;

function Parser.parse_property_param_list : TParamSect;
begin
   result := TParamSect.create;
   storeLocation (result);
   checkSymbol (LBRACKET);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_param_item ();
   while isSymbol (SEMICOLON) do begin
      checkSymbol (SEMICOLON);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_param_item ();
   end;
   checkSymbol (RBRACKET);
   result := result;
end;

function Parser.parse_class_type : TClassType;
begin
   result := TClassType.create;
   storeLocation (result);
   open_class (result);
   checkSymbol (keyword_class);
   if isSymbol (LPAREN) then begin
      checkSymbol (LPAREN);
      result.parent := parse_ifc_type ();
      if isSymbol (COMMA) then begin
         checkSymbol (COMMA);
         result.ifc_list := parse_interface_sect ();
      end;
      checkSymbol (RPAREN);
   end;
   result.components := parse_components_sect ();
   checkSymbol (keyword_end);
   close_class (result);
   result := result;
end;

function Parser.parse_interface_type : TInterfaceType;
begin
   result := TInterfaceType.create;
   storeLocation (result);
   open_interface (result);
   checkSymbol (keyword_interface);
   if isSymbol (LPAREN) then begin
      checkSymbol (LPAREN);
      result.ifc_list := parse_interface_sect ();
      checkSymbol (RPAREN);
   end;
   result.components := parse_components_sect ();
   checkSymbol (keyword_end);
   close_interface (result);
   result := result;
end;

function Parser.parse_interface_sect : TInterfaceSect;
begin
   result := TInterfaceSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_interface_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_interface_item ();
   end;
   result := result;
end;

function Parser.parse_interface_item : TIntefaceItem;
begin
   result := TIntefaceItem.create;
   storeLocation (result);
   result.ifc := parse_ifc_type ();
   result := result;
end;

function Parser.parse_components_sect : TComponetsSect;
begin
   result := TComponetsSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_components_first_item ();
   while testSymbols (set_6) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_components_item ();
   end;
   result := result;
end;

function Parser.parse_components_item : TComponentsItem;
begin
   result := TComponentsItem.create;
   storeLocation (result);
   if isSymbol (keyword_private) then begin
      checkSymbol (keyword_private);
      result.acs := PrivateAccess;
   end
   else if isSymbol (keyword_protected) then begin
      checkSymbol (keyword_protected);
      result.acs := ProtectedAccess;
   end
   else if isSymbol (keyword_public) then begin
      checkSymbol (keyword_public);
      result.acs := PublicAccess;
   end
   else if isSymbol (keyword_published) then begin
      checkSymbol (keyword_published);
      result.acs := PublishedAccess;
   end
   else if isSymbol (keyword_automated) then begin
      checkSymbol (keyword_automated);
      result.acs := AutomatedAccess;
   end
   else begin
      stop ();
   end;
   result.members := parse_member_sect ();
   result := result;
end;

function Parser.parse_components_first_item : TComponentsItem;
begin
   result := TComponentsItem.create;
   storeLocation (result);
   result.acs := PublicAccess;
   result.members := parse_member_sect ();
   result := result;
end;

function Parser.parse_member_sect : TDeclGroup;
begin
   result := TDeclGroup.create;
   storeLocation (result);
   while testSymbols (set_7) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_member_decl ();
   end;
   result := result;
end;

function Parser.parse_member_decl : TDeclSect;
begin
   result := nil;
   if isSymbol (identifier) then begin
      result := parse_field_decl ();
   end
   else if testSymbols (set_8) then begin
      result := parse_method_decl ();
   end
   else if isSymbol (keyword_property) then begin
      result := parse_property_decl ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_field_ident : TFieldItem;
begin
   result := TFieldItem.create;
   storeLocation (result);
   result.name := readIdent;
   on_field (result);
   result := result;
end;

function Parser.parse_field_decl : TFieldDecl;
begin
   result := TFieldDecl.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_field_ident ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_field_ident ();
   end;
   checkSymbol (COLON);
   result.typ := parse_type ();
   checkSymbol (SEMICOLON);
   add_field (result);
   result := result;
end;

function Parser.parse_method_decl : TProcDecl;
begin
   result := TProcDecl.create;
   storeLocation (result);
   open_proc (result);
   parse_proc_head (result);
   while isSymbol (keyword_virtual) or isSymbol (keyword_dynamic) or isSymbol (keyword_override) or isSymbol (keyword_abstract) do begin
      if isSymbol (keyword_virtual) then begin
         checkSymbol (keyword_virtual);
         result.a_virtual := true;
         checkSymbol (SEMICOLON);
      end
      else if isSymbol (keyword_dynamic) then begin
         checkSymbol (keyword_dynamic);
         result.a_dynamic := true;
         checkSymbol (SEMICOLON);
      end
      else if isSymbol (keyword_override) then begin
         checkSymbol (keyword_override);
         result.a_override := true;
         checkSymbol (SEMICOLON);
      end
      else if isSymbol (keyword_abstract) then begin
         checkSymbol (keyword_abstract);
         result.a_abstract := true;
         checkSymbol (SEMICOLON);
      end
      else begin
         stop ();
      end;
   end;
   close_proc (result);
   result := result;
end;

function Parser.parse_property_decl : TPropertyDecl;
begin
   result := TPropertyDecl.create;
   storeLocation (result);
   checkSymbol (keyword_property);
   result.name := readIdent;
   if isSymbol (LBRACKET) then begin
      result.param_list := parse_property_param_list ();
   end;
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.typ := parse_result_type ();
   end;
   if isSymbol (keyword_read) then begin
      checkSymbol (keyword_read);
      result.a_read := parse_expr ();
   end;
   if isSymbol (keyword_write) then begin
      checkSymbol (keyword_write);
      result.a_write := parse_expr ();
   end;
   if isSymbol (keyword_stored) then begin
      checkSymbol (keyword_stored);
      result.a_stored := true;
   end;
   if isSymbol (keyword_default) then begin
      checkSymbol (keyword_default);
      result.a_default := true;
   end;
   if isSymbol (keyword_nodefault) then begin
      checkSymbol (keyword_nodefault);
      result.a_nodefault := true;
   end;
   if isSymbol (keyword_implements) then begin
      checkSymbol (keyword_implements);
      result.a_implements := parse_interface_sect ();
   end;
   if isSymbol (SEMICOLON) then begin
      checkSymbol (SEMICOLON);
      checkSymbol (keyword_default);
      result.a_def_array := true;
   end;
   checkSymbol (SEMICOLON);
   result := result;
end;

function Parser.parse_enum_type : TEnumType;
begin
   result := TEnumType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (LPAREN);
   result.elements := parse_enum_sect ();
   checkSymbol (RPAREN);
   result := result;
end;

function Parser.parse_enum_sect : TEnumSect;
begin
   result := TEnumSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_enum_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_enum_item ();
   end;
   result := result;
end;

function Parser.parse_enum_item : TEnumItem;
begin
   result := TEnumItem.create;
   storeLocation (result);
   result.name := readIdent;
   result := result;
end;

function Parser.parse_string_type : TStringType;
begin
   result := TStringType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (keyword_string);
   if isSymbol (LBRACKET) then begin
      checkSymbol (LBRACKET);
      result.lim := parse_expr ();
      checkSymbol (RBRACKET);
   end;
   result := result;
end;

function Parser.parse_array_type : TArrayType;
begin
   result := TArrayType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (keyword_array);
   if isSymbol (LBRACKET) then begin
      checkSymbol (LBRACKET);
      result.index_list := parse_index_type_sect ();
      checkSymbol (RBRACKET);
   end;
   checkSymbol (keyword_of);
   result.elem := parse_type ();
   result := result;
end;

function Parser.parse_index_type_sect : TIndexTypeSect;
begin
   result := TIndexTypeSect.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_index_type_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_index_type_item ();
   end;
   result := result;
end;

function Parser.parse_index_type_item : TIndexTypeItem;
begin
   result := TIndexTypeItem.create;
   storeLocation (result);
   result.index := parse_type ();
   result := result;
end;

function Parser.parse_record_type : TRecordType;
begin
   result := TRecordType.create;
   storeLocation (result);
   simple_type (result);
   if isSymbol (keyword_packed) then begin
      checkSymbol (keyword_packed);
      result.a_packed := true;
   end;
   checkSymbol (keyword_record);
   result.fields := parse_field_sect ();
   checkSymbol (keyword_end);
   result := result;
end;

function Parser.parse_field_sect : TFieldDeclGroup;
begin
   result := TFieldDeclGroup.create;
   storeLocation (result);
   while isSymbol (identifier) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_field_decl ();
   end;
   result := result;
end;

function Parser.parse_pointer_type : TPointerType;
begin
   result := TPointerType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (ARROW);
   result.elem := parse_type ();
   result := result;
end;

function Parser.parse_set_type : TSetType;
begin
   result := TSetType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (keyword_set);
   checkSymbol (keyword_of);
   result.elem := parse_type ();
   result := result;
end;

function Parser.parse_file_type : TFileType;
begin
   result := TFileType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (keyword_file);
   if isSymbol (keyword_of) then begin
      checkSymbol (keyword_of);
      result.elem := parse_type ();
   end;
   result := result;
end;

function Parser.parse_class_of_type : TClassOfType;
begin
   result := TClassOfType.create;
   storeLocation (result);
   simple_type (result);
   checkSymbol (keyword_class);
   checkSymbol (keyword_of);
   result.elem := parse_type ();
   result := result;
end;

function Parser.parse_proc_type : TProcType;
begin
   result := TProcType.create;
   storeLocation (result);
   simple_type (result);
   if isSymbol (keyword_procedure) then begin
      checkSymbol (keyword_procedure);
      result.style := ProcedureStyle;
   end
   else if isSymbol (keyword_function) then begin
      checkSymbol (keyword_function);
      result.style := FunctionStyle;
   end
   else begin
      stop ();
   end;
   result.param_list := parse_formal_param_list ();
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.answer := parse_result_type ();
   end;
   if isSymbol (keyword_of) then begin
      checkSymbol (keyword_of);
      checkSymbol (keyword_object);
      result.of_object := true;
   end;
   if isSymbol (keyword_register) or isSymbol (keyword_pascal) or isSymbol (keyword_cdecl) or isSymbol (keyword_stdcall) or isSymbol (keyword_safecall) then begin
      if isSymbol (keyword_register) then begin
         checkSymbol (keyword_register);
         result.call_conv := RegisterCall;
      end
      else if isSymbol (keyword_pascal) then begin
         checkSymbol (keyword_pascal);
         result.call_conv := PascalCall;
      end
      else if isSymbol (keyword_cdecl) then begin
         checkSymbol (keyword_cdecl);
         result.call_conv := CdeclCall;
      end
      else if isSymbol (keyword_stdcall) then begin
         checkSymbol (keyword_stdcall);
         result.call_conv := StdcallCall;
      end
      else if isSymbol (keyword_safecall) then begin
         checkSymbol (keyword_safecall);
         result.call_conv := SafecallCall;
      end
      else begin
         stop ();
      end;
   end;
   result := result;
end;

function Parser.parse_range_type : TSubrangeType;
begin
   result := TSubrangeType.create;
   storeLocation (result);
   simple_type (result);
   result.low := parse_simple_expr ();
   checkSymbol (RANGE);
   result.high := parse_simple_expr ();
   result := result;
end;

function Parser.parse_alias_type : TAliasType;
begin
   result := TAliasType.create;
   storeLocation (result);
   simple_type (result);
   result.alias_name := parse_qualified_name ();
   result := result;
end;

function Parser.parse_type : TType;
begin
   result := nil;
   if isSymbol (keyword_string) then begin
      result := parse_string_type ();
   end
   else if isSymbol (keyword_array) then begin
      result := parse_array_type ();
   end
   else if isSymbol (keyword_set) then begin
      result := parse_set_type ();
   end
   else if isSymbol (keyword_file) then begin
      result := parse_file_type ();
   end
   else if isSymbol (keyword_packed) or isSymbol (keyword_record) then begin
      result := parse_record_type ();
   end
   else if isSymbol (keyword_class) then begin
      result := parse_class_type ();
   end
   else if isSymbol (keyword_class) then begin
      result := parse_class_of_type ();
   end
   else if isSymbol (keyword_interface) then begin
      result := parse_interface_type ();
   end
   else if isSymbol (keyword_function) or isSymbol (keyword_procedure) then begin
      result := parse_proc_type ();
   end
   else if isSymbol (ARROW) then begin
      result := parse_pointer_type ();
   end
   else if testSymbols (set_4) and test_3 then begin
      result := parse_range_type ();
   end
   else if isSymbol (LPAREN) and test_4 then begin
      result := parse_enum_type ();
   end
   else if isSymbol (identifier) then begin
      result := parse_alias_type ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_label_decl : TLabelDecl;
begin
   result := TLabelDecl.create;
   storeLocation (result);
   result.name := parse_label_ident ();
   result := result;
end;

function Parser.parse_label_sect : TLabelSect;
begin
   result := TLabelSect.create;
   storeLocation (result);
   checkSymbol (keyword_label);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_label_decl ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_label_decl ();
   end;
   checkSymbol (SEMICOLON);
   result := result;
end;

function Parser.parse_const_decl : TConstDecl;
begin
   result := TConstDecl.create;
   storeLocation (result);
   result.name := readIdent;
   on_const (result);
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.typ := parse_type ();
   end;
   checkSymbol (EQUAL);
   result.val := parse_expr ();
   checkSymbol (SEMICOLON);
   add_const (result);
   result := result;
end;

function Parser.parse_const_sect : TConstSect;
begin
   result := TConstSect.create;
   storeLocation (result);
   checkSymbol (keyword_const);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_const_decl ();
   while isSymbol (identifier) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_const_decl ();
   end;
   result := result;
end;

function Parser.parse_type_decl : TTypeDecl;
begin
   result := TTypeDecl.create;
   storeLocation (result);
   result.name := readIdent;
   on_type (result);
   checkSymbol (EQUAL);
   result.typ := parse_type ();
   checkSymbol (SEMICOLON);
   add_type (result);
   result := result;
end;

function Parser.parse_type_sect : TTypeSect;
begin
   result := TTypeSect.create;
   storeLocation (result);
   checkSymbol (keyword_type);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_type_decl ();
   while isSymbol (identifier) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_type_decl ();
   end;
   result := result;
end;

function Parser.parse_var_item : TVarItem;
begin
   result := TVarItem.create;
   storeLocation (result);
   result.name := readIdent;
   on_var (result);
   result := result;
end;

function Parser.parse_var_decl : TVarDecl;
begin
   result := TVarDecl.create;
   storeLocation (result);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_var_item ();
   while isSymbol (COMMA) do begin
      checkSymbol (COMMA);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_var_item ();
   end;
   checkSymbol (COLON);
   result.typ := parse_type ();
   if isSymbol (EQUAL) then begin
      checkSymbol (EQUAL);
      result.ini := parse_expr ();
   end;
   checkSymbol (SEMICOLON);
   add_var (result);
   result := result;
end;

function Parser.parse_var_sect : TVarSect;
begin
   result := TVarSect.create;
   storeLocation (result);
   checkSymbol (keyword_var);
   setLength (result.items, length (result.items) + 1); 
   result.items [ high (result.items)] := parse_var_decl ();
   while isSymbol (identifier) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_var_decl ();
   end;
   result := result;
end;

function Parser.parse_proc_head (param : TProcDecl) : TProcDecl;
begin
   result := param;
   if isSymbol (keyword_class) then begin
      checkSymbol (keyword_class);
      result.a_static := true;
   end;
   if isSymbol (keyword_procedure) then begin
      checkSymbol (keyword_procedure);
      result.style := ProcedureStyle;
   end
   else if isSymbol (keyword_function) then begin
      checkSymbol (keyword_function);
      result.style := FunctionStyle;
   end
   else if isSymbol (keyword_constructor) then begin
      checkSymbol (keyword_constructor);
      result.style := ConstructorStyle;
   end
   else if isSymbol (keyword_destructor) then begin
      checkSymbol (keyword_destructor);
      result.style := DestructorStyle;
   end
   else begin
      stop ();
   end;
   result.proc_name := parse_qualified_name ();
   on_proc (result);
   result.param_list := parse_formal_param_list ();
   if isSymbol (COLON) then begin
      checkSymbol (COLON);
      result.answer := parse_result_type ();
   end;
   checkSymbol (SEMICOLON);
   result := result;
end;

function Parser.parse_proc_decl : TProcDecl;
begin
   result := TProcDecl.create;
   storeLocation (result);
   open_proc (result);
   parse_proc_head (result);
   if isSymbol (keyword_forward) then begin
      checkSymbol (keyword_forward);
      result.a_forward := true;
   end
   else if isSymbol (keyword_external) then begin
      parse_proc_external (result);
      result.external_spec := true;
   end
   else if testSymbols (set_11) then begin
      if isSymbol (keyword_inline) then begin
         checkSymbol (keyword_inline);
         checkSymbol (SEMICOLON);
         result.a_inline := true;
      end;
      result.local := parse_decl_part ();
      on_begin_proc (result);
      checkSymbol (keyword_begin);
      result.body := parse_stat_list ();
      on_end_proc (result);
      checkSymbol (keyword_end);
      on_tail_proc (result);
   end
   else begin
      stop ();
   end;
   checkSymbol (SEMICOLON);
   close_proc (result);
   result := result;
end;

function Parser.parse_proc_external (param : TProcDecl) : TProcDecl;
begin
   result := param;
   checkSymbol (keyword_external);
   result.a_external := true;
   if testSymbols (set_4) then begin
      result.a_lib := parse_expr ();
   end;
   checkSymbol (SEMICOLON);
   result := result;
end;

function Parser.parse_proc_intf_decl : TProcDecl;
begin
   result := TProcDecl.create;
   storeLocation (result);
   open_proc (result);
   parse_proc_head (result);
   if isSymbol (keyword_inline) then begin
      checkSymbol (keyword_inline);
      checkSymbol (SEMICOLON);
      result.a_inline := true;
   end;
   if isSymbol (keyword_external) then begin
      parse_proc_external (result);
      result.external_spec := true;
   end;
   close_proc (result);
   result := result;
end;

function Parser.parse_intf_decl : TDeclSect;
begin
   result := nil;
   if isSymbol (keyword_const) then begin
      result := parse_const_sect ();
   end
   else if isSymbol (keyword_type) then begin
      result := parse_type_sect ();
   end
   else if isSymbol (keyword_var) then begin
      result := parse_var_sect ();
   end
   else if testSymbols (set_8) then begin
      result := parse_proc_intf_decl ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_intf_decl_part : TDeclGroup;
begin
   result := TDeclGroup.create;
   storeLocation (result);
   while testSymbols (set_12) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_intf_decl ();
   end;
   result := result;
end;

function Parser.parse_decl : TDeclSect;
begin
   result := nil;
   if isSymbol (keyword_label) then begin
      result := parse_label_sect ();
   end
   else if isSymbol (keyword_const) then begin
      result := parse_const_sect ();
   end
   else if isSymbol (keyword_type) then begin
      result := parse_type_sect ();
   end
   else if isSymbol (keyword_var) then begin
      result := parse_var_sect ();
   end
   else if testSymbols (set_8) then begin
      result := parse_proc_decl ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.parse_decl_part : TDeclGroup;
begin
   result := TDeclGroup.create;
   storeLocation (result);
   while testSymbols (set_13) do begin
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_decl ();
   end;
   result := result;
end;

function Parser.parse_import_item : TImportItem;
begin
   result := TImportItem.create;
   storeLocation (result);
   result.name := readIdent;
   on_import (result);
   if isSymbol (keyword_in) then begin
      checkSymbol (keyword_in);
      result.path := readString;
   end;
   result := result;
end;

function Parser.parse_import_sect : TImportSect;
begin
   result := TImportSect.create;
   storeLocation (result);
   if isSymbol (keyword_uses) then begin
      checkSymbol (keyword_uses);
      setLength (result.items, length (result.items) + 1); 
      result.items [ high (result.items)] := parse_import_item ();
      while isSymbol (COMMA) do begin
         checkSymbol (COMMA);
         setLength (result.items, length (result.items) + 1); 
         result.items [ high (result.items)] := parse_import_item ();
      end;
      checkSymbol (SEMICOLON);
   end;
   result := result;
end;

function Parser.parse_unit_decl : TUnitModule;
begin
   result := TUnitModule.create;
   storeLocation (result);
   open_module (result);
   checkSymbol (keyword_unit);
   result.name := readIdent;
   on_module (result);
   checkSymbol (SEMICOLON);
   checkSymbol (keyword_interface);
   result.intf_imports := parse_import_sect ();
   result.intf_decl := parse_intf_decl_part ();
   checkSymbol (keyword_implementation);
   result.impl_imports := parse_import_sect ();
   result.impl_decl := parse_decl_part ();
   if isSymbol (keyword_finalization) or isSymbol (keyword_initialization) or isSymbol (keyword_begin) then begin
      if isSymbol (keyword_finalization) or isSymbol (keyword_initialization) then begin
         if isSymbol (keyword_initialization) then begin
            checkSymbol (keyword_initialization);
            result.init := parse_stat_list ();
         end;
         if isSymbol (keyword_finalization) then begin
            checkSymbol (keyword_finalization);
            result.finish := parse_stat_list ();
         end;
         result.no_begin := true;
      end
      else if isSymbol (keyword_begin) then begin
         checkSymbol (keyword_begin);
         result.init := parse_stat_list ();
      end
      else begin
         stop ();
      end;
   end;
   checkSymbol (keyword_end);
   checkSymbol (DOT);
   close_module (result);
   result := result;
end;

function Parser.parse_program_decl : TProgramModule;
begin
   result := TProgramModule.create;
   storeLocation (result);
   open_module (result);
   checkSymbol (keyword_program);
   result.name := readIdent;
   on_module (result);
   checkSymbol (SEMICOLON);
   result.impl_imports := parse_import_sect ();
   result.impl_decl := parse_decl_part ();
   checkSymbol (keyword_begin);
   result.init := parse_stat_list ();
   checkSymbol (keyword_end);
   checkSymbol (DOT);
   close_module (result);
   result := result;
end;

function Parser.parse_library_decl : TLibraryModule;
begin
   result := TLibraryModule.create;
   storeLocation (result);
   open_module (result);
   checkSymbol (keyword_library);
   result.name := readIdent;
   on_module (result);
   checkSymbol (SEMICOLON);
   result.impl_imports := parse_import_sect ();
   result.impl_decl := parse_decl_part ();
   checkSymbol (keyword_begin);
   result.init := parse_stat_list ();
   checkSymbol (keyword_end);
   checkSymbol (DOT);
   close_module (result);
   result := result;
end;

function Parser.parse_module_decl : TModule;
begin
   result := nil;
   if isSymbol (keyword_unit) then begin
      result := parse_unit_decl ();
   end
   else if isSymbol (keyword_program) then begin
      result := parse_program_decl ();
   end
   else if isSymbol (keyword_library) then begin
      result := parse_library_decl ();
   end
   else begin
      stop ();
   end;
   result := result;
end;

function Parser.test_1 : boolean;
var position : integer;
begin
   result := true;
   position := mark;
   if result and (token <> keyword_string) then begin
      result := false;
   end;
   if result then begin
      nextToken;
   end;
   if result and (token <> LPAREN) then begin
      result := false;
   end;
   if result then begin
      nextToken;
   end;
   rewind (position);
end;

function Parser.test_2 : boolean;
var position : integer;
begin
   result := true;
   position := mark;
   if result then begin
      if not test_label_ident then begin
         result := false;
      end;
   end;
   if result and (token <> COLON) then begin
      result := false;
   end;
   if result then begin
      nextToken;
   end;
   rewind (position);
end;

function Parser.test_3 : boolean;
var position : integer;
begin
   result := true;
   position := mark;
   if result then begin
      if not test_range_type then begin
         result := false;
      end;
   end;
   rewind (position);
end;

function Parser.test_4 : boolean;
var position : integer;
begin
   result := true;
   position := mark;
   if result then begin
      if not test_enum_type then begin
         result := false;
      end;
   end;
   rewind (position);
end;

function Parser.test_label_ident : boolean;
begin
   if token <> identifier then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_range_type : boolean;
begin
   if not test_simple_expr then begin
      result := false;
   end;
   if token <> RANGE then begin
      result := false;
   end;
   nextToken;
   if not test_simple_expr then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_simple_expr : boolean;
begin
   if not test_term then begin
      result := false;
   end;
   while isSymbol (PLUS) or isSymbol (MINUS) or isSymbol (keyword_or) or isSymbol (keyword_xor) do begin
      if isSymbol (PLUS) then begin
         nextToken;
      end
      else if isSymbol (MINUS) then begin
         nextToken;
      end
      else if isSymbol (keyword_or) then begin
         nextToken;
      end
      else if isSymbol (keyword_xor) then begin
         nextToken;
      end
      else begin
         result := false;
      end;
      if not test_term then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_term : boolean;
begin
   if not test_factor then begin
      result := false;
   end;
   while isSymbol (STAR) or isSymbol (SLASH) or isSymbol (keyword_div) or isSymbol (keyword_mod) or isSymbol (keyword_shl) or isSymbol (keyword_shr) or isSymbol (keyword_and) or isSymbol (keyword_as) do begin
      if isSymbol (STAR) then begin
         nextToken;
      end
      else if isSymbol (SLASH) then begin
         nextToken;
      end
      else if isSymbol (keyword_div) then begin
         nextToken;
      end
      else if isSymbol (keyword_mod) then begin
         nextToken;
      end
      else if isSymbol (keyword_shl) then begin
         nextToken;
      end
      else if isSymbol (keyword_shr) then begin
         nextToken;
      end
      else if isSymbol (keyword_and) then begin
         nextToken;
      end
      else if isSymbol (keyword_as) then begin
         nextToken;
      end
      else begin
         result := false;
      end;
      if not test_factor then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_factor : boolean;
begin
   if isSymbol (number) then begin
      if not test_int_value_expr then begin
         result := false;
      end;
   end
   else if isSymbol (real_number) then begin
      if not test_float_value_expr then begin
         result := false;
      end;
   end
   else if isSymbol (string_literal) then begin
      if not test_string_value_expr then begin
         result := false;
      end;
   end
   else if isSymbol (keyword_not) then begin
      if not test_not_expr then begin
         result := false;
      end;
   end
   else if isSymbol (PLUS) then begin
      if not test_plus_expr then begin
         result := false;
      end;
   end
   else if isSymbol (MINUS) then begin
      if not test_minus_expr then begin
         result := false;
      end;
   end
   else if isSymbol (ADDRESS) then begin
      if not test_adr_expr then begin
         result := false;
      end;
   end
   else if isSymbol (keyword_nil) then begin
      if not test_nil_expr then begin
         result := false;
      end;
   end
   else if isSymbol (LBRACKET) then begin
      if not test_set_expr then begin
         result := false;
      end;
   end
   else if isSymbol (keyword_string) and test_1 then begin
      if not test_string_type_expr then begin
         result := false;
      end;
   end
   else if isSymbol (identifier) or isSymbol (LPAREN) or isSymbol (keyword_inherited) then begin
      if not test_reference then begin
         result := false;
      end;
   end
   else begin
      result := false;
   end;
   result := true;
end;

function Parser.test_int_value_expr : boolean;
begin
   if token <> number then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_float_value_expr : boolean;
begin
   if token <> real_number then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_string_value_expr : boolean;
begin
   if token <> string_literal then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_not_expr : boolean;
begin
   if token <> keyword_not then begin
      result := false;
   end;
   nextToken;
   if not test_factor then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_plus_expr : boolean;
begin
   if token <> PLUS then begin
      result := false;
   end;
   nextToken;
   if not test_factor then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_minus_expr : boolean;
begin
   if token <> MINUS then begin
      result := false;
   end;
   nextToken;
   if not test_factor then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_adr_expr : boolean;
begin
   if token <> ADDRESS then begin
      result := false;
   end;
   nextToken;
   if not test_factor then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_nil_expr : boolean;
begin
   if token <> keyword_nil then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_set_expr : boolean;
begin
   if token <> LBRACKET then begin
      result := false;
   end;
   nextToken;
   if not test_elem_sect then begin
      result := false;
   end;
   if token <> RBRACKET then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_elem_sect : boolean;
begin
   if not test_elem_item then begin
      result := false;
   end;
   while isSymbol (COMMA) do begin
      nextToken;
      if not test_elem_item then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_elem_item : boolean;
begin
   if not test_expr then begin
      result := false;
   end;
   if isSymbol (RANGE) then begin
      nextToken;
      if not test_expr then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_expr : boolean;
begin
   if not test_simple_expr then begin
      result := false;
   end;
   if isSymbol (EQUAL) or isSymbol (UNEQUAL) or isSymbol (LESS) or isSymbol (GREATER) or isSymbol (LESS_OR_EQUAL) or isSymbol (GREATER_OR_EQUAL) or isSymbol (keyword_in) or isSymbol (keyword_is) then begin
      if isSymbol (EQUAL) then begin
         nextToken;
      end
      else if isSymbol (UNEQUAL) then begin
         nextToken;
      end
      else if isSymbol (LESS) then begin
         nextToken;
      end
      else if isSymbol (GREATER) then begin
         nextToken;
      end
      else if isSymbol (LESS_OR_EQUAL) then begin
         nextToken;
      end
      else if isSymbol (GREATER_OR_EQUAL) then begin
         nextToken;
      end
      else if isSymbol (keyword_in) then begin
         nextToken;
      end
      else if isSymbol (keyword_is) then begin
         nextToken;
      end
      else begin
         result := false;
      end;
      if not test_simple_expr then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_string_type_expr : boolean;
begin
   if token <> keyword_string then begin
      result := false;
   end;
   nextToken;
   if token <> LPAREN then begin
      result := false;
   end;
   nextToken;
   if not test_expr then begin
      result := false;
   end;
   if token <> RPAREN then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_reference : boolean;
begin
   if not test_variable then begin
      result := false;
   end;
   while isSymbol (LBRACKET) or isSymbol (LPAREN) or isSymbol (ARROW) or isSymbol (DOT) do begin
      if isSymbol (LBRACKET) then begin
         if not test_index_expr then begin
            result := false;
         end;
      end
      else if isSymbol (LPAREN) then begin
         if not test_call_expr then begin
            result := false;
         end;
      end
      else if isSymbol (ARROW) then begin
         if not test_deref_expr then begin
            result := false;
         end;
      end
      else if isSymbol (DOT) then begin
         if not test_field_expr then begin
            result := false;
         end;
      end
      else begin
         result := false;
      end;
   end;
   ;
   result := true;
end;

function Parser.test_variable : boolean;
begin
   if isSymbol (identifier) then begin
      if not test_ident_expr then begin
         result := false;
      end;
   end
   else if isSymbol (LPAREN) then begin
      if not test_sub_expr then begin
         result := false;
      end;
   end
   else if isSymbol (keyword_inherited) then begin
      if not test_super_expr then begin
         result := false;
      end;
   end
   else begin
      result := false;
   end;
   result := true;
end;

function Parser.test_ident_expr : boolean;
begin
   if token <> identifier then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_sub_expr : boolean;
begin
   if token <> LPAREN then begin
      result := false;
   end;
   nextToken;
   if not test_expr then begin
      result := false;
   end;
   if token <> RPAREN then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_super_expr : boolean;
begin
   if token <> keyword_inherited then begin
      result := false;
   end;
   nextToken;
   if token <> identifier then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_index_expr : boolean;
begin
   if token <> LBRACKET then begin
      result := false;
   end;
   nextToken;
   if not test_index_expr_list then begin
      result := false;
   end;
   if token <> RBRACKET then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_index_expr_list : boolean;
begin
   if not test_index_expr_item then begin
      result := false;
   end;
   while isSymbol (COMMA) do begin
      nextToken;
      if not test_index_expr_item then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_index_expr_item : boolean;
begin
   if not test_expr then begin
      result := false;
   end;
   ;
   result := true;
end;

function Parser.test_call_expr : boolean;
begin
   if token <> LPAREN then begin
      result := false;
   end;
   nextToken;
   if not test_arg_list then begin
      result := false;
   end;
   if token <> RPAREN then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_arg_list : boolean;
begin
   if not test_arg_item then begin
      result := false;
   end;
   while isSymbol (COMMA) do begin
      nextToken;
      if not test_arg_item then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_arg_item : boolean;
begin
   if not test_expr then begin
      result := false;
   end;
   if isSymbol (COLON) then begin
      nextToken;
      if not test_expr then begin
         result := false;
      end;
      if isSymbol (COLON) then begin
         nextToken;
         if not test_expr then begin
            result := false;
         end;
         ;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_deref_expr : boolean;
begin
   if token <> ARROW then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_field_expr : boolean;
begin
   if token <> DOT then begin
      result := false;
   end;
   nextToken;
   if token <> identifier then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_enum_type : boolean;
begin
   if token <> LPAREN then begin
      result := false;
   end;
   nextToken;
   if not test_enum_sect then begin
      result := false;
   end;
   if token <> RPAREN then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

function Parser.test_enum_sect : boolean;
begin
   if not test_enum_item then begin
      result := false;
   end;
   while isSymbol (COMMA) do begin
      nextToken;
      if not test_enum_item then begin
         result := false;
      end;
      ;
   end;
   ;
   result := true;
end;

function Parser.test_enum_item : boolean;
begin
   if token <> identifier then begin
      result := false;
   end;
   nextToken;
   ;
   result := true;
end;

procedure Parser.lookupKeyword;
var s : string;
var n : integer;
begin
   s := tokenText;
   n := length (s);
   if n = 2 then begin
      if s[1] = 'a' then
      begin
         if s[2] = 's' then
         begin
            token := keyword_as;
         end
      end
      else if s[1] = 'd' then
      begin
         if s[2] = 'o' then
         begin
            token := keyword_do;
         end
      end
      else if s[1] = 'i' then
      begin
         if s[2] = 'f' then
         begin
            token := keyword_if;
         end
         else if s[2] = 'n' then
         begin
            token := keyword_in;
         end
         else if s[2] = 's' then
         begin
            token := keyword_is;
         end
      end
      else if s[1] = 'o' then
      begin
         if s[2] = 'f' then
         begin
            token := keyword_of;
         end
         else if s[2] = 'n' then
         begin
            token := keyword_on;
         end
         else if s[2] = 'r' then
         begin
            token := keyword_or;
         end
      end
      else if s[1] = 't' then
      begin
         if s[2] = 'o' then
         begin
            token := keyword_to;
         end
      end
   end
   else if n = 3 then begin
      if s[1] = 'a' then
      begin
         if copy (s, 2, 2) = 'nd' then
         begin
            token := keyword_and;
         end
      end
      else if s[1] = 'd' then
      begin
         if copy (s, 2, 2) = 'iv' then
         begin
            token := keyword_div;
         end
      end
      else if s[1] = 'e' then
      begin
         if copy (s, 2, 2) = 'nd' then
         begin
            token := keyword_end;
         end
      end
      else if s[1] = 'f' then
      begin
         if copy (s, 2, 2) = 'or' then
         begin
            token := keyword_for;
         end
      end
      else if s[1] = 'm' then
      begin
         if copy (s, 2, 2) = 'od' then
         begin
            token := keyword_mod;
         end
      end
      else if s[1] = 'n' then
      begin
         if s[2] = 'i' then
         begin
            if s[3] = 'l' then
            begin
               token := keyword_nil;
            end
         end
         else if s[2] = 'o' then
         begin
            if s[3] = 't' then
            begin
               token := keyword_not;
            end
         end
      end
      else if s[1] = 'o' then
      begin
         if copy (s, 2, 2) = 'ut' then
         begin
            token := keyword_out;
         end
      end
      else if s[1] = 's' then
      begin
         if s[2] = 'e' then
         begin
            if s[3] = 't' then
            begin
               token := keyword_set;
            end
         end
         else if s[2] = 'h' then
         begin
            if s[3] = 'l' then
            begin
               token := keyword_shl;
            end
            else if s[3] = 'r' then
            begin
               token := keyword_shr;
            end
         end
      end
      else if s[1] = 't' then
      begin
         if copy (s, 2, 2) = 'ry' then
         begin
            token := keyword_try;
         end
      end
      else if s[1] = 'v' then
      begin
         if copy (s, 2, 2) = 'ar' then
         begin
            token := keyword_var;
         end
      end
      else if s[1] = 'x' then
      begin
         if copy (s, 2, 2) = 'or' then
         begin
            token := keyword_xor;
         end
      end
   end
   else if n = 4 then begin
      if s[1] = 'c' then
      begin
         if copy (s, 2, 3) = 'ase' then
         begin
            token := keyword_case;
         end
      end
      else if s[1] = 'e' then
      begin
         if copy (s, 2, 3) = 'lse' then
         begin
            token := keyword_else;
         end
      end
      else if s[1] = 'f' then
      begin
         if copy (s, 2, 3) = 'ile' then
         begin
            token := keyword_file;
         end
      end
      else if s[1] = 'g' then
      begin
         if copy (s, 2, 3) = 'oto' then
         begin
            token := keyword_goto;
         end
      end
      else if s[1] = 'r' then
      begin
         if copy (s, 2, 3) = 'ead' then
         begin
            token := keyword_read;
         end
      end
      else if s[1] = 't' then
      begin
         if s[2] = 'h' then
         begin
            if copy (s, 3, 2) = 'en' then
            begin
               token := keyword_then;
            end
         end
         else if s[2] = 'y' then
         begin
            if copy (s, 3, 2) = 'pe' then
            begin
               token := keyword_type;
            end
         end
      end
      else if s[1] = 'u' then
      begin
         if s[2] = 'n' then
         begin
            if copy (s, 3, 2) = 'it' then
            begin
               token := keyword_unit;
            end
         end
         else if s[2] = 's' then
         begin
            if copy (s, 3, 2) = 'es' then
            begin
               token := keyword_uses;
            end
         end
      end
      else if s[1] = 'w' then
      begin
         if copy (s, 2, 3) = 'ith' then
         begin
            token := keyword_with;
         end
      end
   end
   else if n = 5 then begin
      if s[1] = 'a' then
      begin
         if copy (s, 2, 4) = 'rray' then
         begin
            token := keyword_array;
         end
      end
      else if s[1] = 'b' then
      begin
         if copy (s, 2, 4) = 'egin' then
         begin
            token := keyword_begin;
         end
      end
      else if s[1] = 'c' then
      begin
         if s[2] = 'd' then
         begin
            if copy (s, 3, 3) = 'ecl' then
            begin
               token := keyword_cdecl;
            end
         end
         else if s[2] = 'l' then
         begin
            if copy (s, 3, 3) = 'ass' then
            begin
               token := keyword_class;
            end
         end
         else if s[2] = 'o' then
         begin
            if copy (s, 3, 3) = 'nst' then
            begin
               token := keyword_const;
            end
         end
      end
      else if s[1] = 'l' then
      begin
         if copy (s, 2, 4) = 'abel' then
         begin
            token := keyword_label;
         end
      end
      else if s[1] = 'r' then
      begin
         if copy (s, 2, 4) = 'aise' then
         begin
            token := keyword_raise;
         end
      end
      else if s[1] = 'u' then
      begin
         if copy (s, 2, 4) = 'ntil' then
         begin
            token := keyword_until;
         end
      end
      else if s[1] = 'w' then
      begin
         if s[2] = 'h' then
         begin
            if copy (s, 3, 3) = 'ile' then
            begin
               token := keyword_while;
            end
         end
         else if s[2] = 'r' then
         begin
            if copy (s, 3, 3) = 'ite' then
            begin
               token := keyword_write;
            end
         end
      end
   end
   else if n = 6 then begin
      if s[1] = 'd' then
      begin
         if copy (s, 2, 5) = 'ownto' then
         begin
            token := keyword_downto;
         end
      end
      else if s[1] = 'e' then
      begin
         if copy (s, 2, 5) = 'xcept' then
         begin
            token := keyword_except;
         end
      end
      else if s[1] = 'i' then
      begin
         if copy (s, 2, 5) = 'nline' then
         begin
            token := keyword_inline;
         end
      end
      else if s[1] = 'o' then
      begin
         if copy (s, 2, 5) = 'bject' then
         begin
            token := keyword_object;
         end
      end
      else if s[1] = 'p' then
      begin
         if s[2] = 'a' then
         begin
            if s[3] = 'c' then
            begin
               if copy (s, 4, 3) = 'ked' then
               begin
                  token := keyword_packed;
               end
            end
            else if s[3] = 's' then
            begin
               if copy (s, 4, 3) = 'cal' then
               begin
                  token := keyword_pascal;
               end
            end
         end
         else if s[2] = 'u' then
         begin
            if copy (s, 3, 4) = 'blic' then
            begin
               token := keyword_public;
            end
         end
      end
      else if s[1] = 'r' then
      begin
         if s[2] = 'e' then
         begin
            if s[3] = 'c' then
            begin
               if copy (s, 4, 3) = 'ord' then
               begin
                  token := keyword_record;
               end
            end
            else if s[3] = 'p' then
            begin
               if copy (s, 4, 3) = 'eat' then
               begin
                  token := keyword_repeat;
               end
            end
         end
      end
      else if s[1] = 's' then
      begin
         if s[2] = 't' then
         begin
            if s[3] = 'o' then
            begin
               if copy (s, 4, 3) = 'red' then
               begin
                  token := keyword_stored;
               end
            end
            else if s[3] = 'r' then
            begin
               if copy (s, 4, 3) = 'ing' then
               begin
                  token := keyword_string;
               end
            end
         end
      end
   end
   else if n = 7 then begin
      if s[1] = 'd' then
      begin
         if s[2] = 'e' then
         begin
            if copy (s, 3, 5) = 'fault' then
            begin
               token := keyword_default;
            end
         end
         else if s[2] = 'y' then
         begin
            if copy (s, 3, 5) = 'namic' then
            begin
               token := keyword_dynamic;
            end
         end
      end
      else if s[1] = 'f' then
      begin
         if s[2] = 'i' then
         begin
            if copy (s, 3, 5) = 'nally' then
            begin
               token := keyword_finally;
            end
         end
         else if s[2] = 'o' then
         begin
            if copy (s, 3, 5) = 'rward' then
            begin
               token := keyword_forward;
            end
         end
      end
      else if s[1] = 'l' then
      begin
         if copy (s, 2, 6) = 'ibrary' then
         begin
            token := keyword_library;
         end
      end
      else if s[1] = 'p' then
      begin
         if s[2] = 'r' then
         begin
            if s[3] = 'i' then
            begin
               if copy (s, 4, 4) = 'vate' then
               begin
                  token := keyword_private;
               end
            end
            else if s[3] = 'o' then
            begin
               if copy (s, 4, 4) = 'gram' then
               begin
                  token := keyword_program;
               end
            end
         end
      end
      else if s[1] = 's' then
      begin
         if copy (s, 2, 6) = 'tdcall' then
         begin
            token := keyword_stdcall;
         end
      end
      else if s[1] = 'v' then
      begin
         if copy (s, 2, 6) = 'irtual' then
         begin
            token := keyword_virtual;
         end
      end
   end
   else if n = 8 then begin
      if s[1] = 'a' then
      begin
         if copy (s, 2, 7) = 'bstract' then
         begin
            token := keyword_abstract;
         end
      end
      else if s[1] = 'e' then
      begin
         if copy (s, 2, 7) = 'xternal' then
         begin
            token := keyword_external;
         end
      end
      else if s[1] = 'f' then
      begin
         if copy (s, 2, 7) = 'unction' then
         begin
            token := keyword_function;
         end
      end
      else if s[1] = 'o' then
      begin
         if copy (s, 2, 7) = 'verride' then
         begin
            token := keyword_override;
         end
      end
      else if s[1] = 'p' then
      begin
         if copy (s, 2, 7) = 'roperty' then
         begin
            token := keyword_property;
         end
      end
      else if s[1] = 'r' then
      begin
         if copy (s, 2, 7) = 'egister' then
         begin
            token := keyword_register;
         end
      end
      else if s[1] = 's' then
      begin
         if copy (s, 2, 7) = 'afecall' then
         begin
            token := keyword_safecall;
         end
      end
   end
   else if n = 9 then begin
      if s[1] = 'a' then
      begin
         if copy (s, 2, 8) = 'utomated' then
         begin
            token := keyword_automated;
         end
      end
      else if s[1] = 'i' then
      begin
         if s[2] = 'n' then
         begin
            if s[3] = 'h' then
            begin
               if copy (s, 4, 6) = 'erited' then
               begin
                  token := keyword_inherited;
               end
            end
            else if s[3] = 't' then
            begin
               if copy (s, 4, 6) = 'erface' then
               begin
                  token := keyword_interface;
               end
            end
         end
      end
      else if s[1] = 'n' then
      begin
         if copy (s, 2, 8) = 'odefault' then
         begin
            token := keyword_nodefault;
         end
      end
      else if s[1] = 'p' then
      begin
         if s[2] = 'r' then
         begin
            if s[3] = 'o' then
            begin
               if s[4] = 'c' then
               begin
                  if copy (s, 5, 5) = 'edure' then
                  begin
                     token := keyword_procedure;
                  end
               end
               else if s[4] = 't' then
               begin
                  if copy (s, 5, 5) = 'ected' then
                  begin
                     token := keyword_protected;
                  end
               end
            end
         end
         else if s[2] = 'u' then
         begin
            if copy (s, 3, 7) = 'blished' then
            begin
               token := keyword_published;
            end
         end
      end
   end
   else if n = 10 then begin
      if s[1] = 'd' then
      begin
         if copy (s, 2, 9) = 'estructor' then
         begin
            token := keyword_destructor;
         end
      end
      else if s[1] = 'i' then
      begin
         if copy (s, 2, 9) = 'mplements' then
         begin
            token := keyword_implements;
         end
      end
   end
   else if n = 11 then begin
      if copy (s, 1, 11) = 'constructor' then
      begin
         token := keyword_constructor;
      end
   end
   else if n = 12 then begin
      if copy (s, 1, 12) = 'finalization' then
      begin
         token := keyword_finalization;
      end
   end
   else if n = 14 then begin
      if s[1] = 'i' then
      begin
         if s[2] = 'm' then
         begin
            if copy (s, 3, 12) = 'plementation' then
            begin
               token := keyword_implementation;
            end
         end
         else if s[2] = 'n' then
         begin
            if copy (s, 3, 12) = 'itialization' then
            begin
               token := keyword_initialization;
            end
         end
      end
   end
end;

procedure Parser.processSeparator;
begin
   if tokenText = '(' then begin
      token := LPAREN;
   end;
   if tokenText = ')' then begin
      token := RPAREN;
   end;
   if tokenText = '*' then begin
      token := STAR;
   end;
   if tokenText = '+' then begin
      token := PLUS;
   end;
   if tokenText = ',' then begin
      token := COMMA;
   end;
   if tokenText = '-' then begin
      token := MINUS;
   end;
   if tokenText = '.' then begin
      token := DOT;
      if inpCh = '.' then begin
         token := RANGE;
         tokenText := tokenText + inpCh;
         nextCh;
      end;
   end;
   if tokenText = '/' then begin
      token := SLASH;
   end;
   if tokenText = ':' then begin
      token := COLON;
      if inpCh = '=' then begin
         token := ASSIGN;
         tokenText := tokenText + inpCh;
         nextCh;
      end;
   end;
   if tokenText = ';' then begin
      token := SEMICOLON;
   end;
   if tokenText = '<' then begin
      token := LESS;
      if inpCh = '=' then begin
         token := LESS_OR_EQUAL;
         tokenText := tokenText + inpCh;
         nextCh;
      end;
      if inpCh = '>' then begin
         token := UNEQUAL;
         tokenText := tokenText + inpCh;
         nextCh;
      end;
   end;
   if tokenText = '=' then begin
      token := EQUAL;
   end;
   if tokenText = '>' then begin
      token := GREATER;
      if inpCh = '=' then begin
         token := GREATER_OR_EQUAL;
         tokenText := tokenText + inpCh;
         nextCh;
      end;
   end;
   if tokenText = '@' then begin
      token := ADDRESS;
   end;
   if tokenText = '[' then begin
      token := LBRACKET;
   end;
   if tokenText = ']' then begin
      token := RBRACKET;
   end;
   if tokenText = '^' then begin
      token := ARROW;
   end;
   if token = separator then begin
      error ('Unknown separator');
   end;
end;

function Parser.tokenToString (value : Symbol) : string;
begin
   if ord (value) = 0 then result := '<end of source text>';
   if ord (value) = 1 then result := '<identifier>';
   if ord (value) = 2 then result := '<number>';
   if ord (value) = 3 then result := '<real_number>';
   if ord (value) = 4 then result := '<character_literal>';
   if ord (value) = 5 then result := '<string_literal>';
   if ord (value) = 6 then result := '<unknown separator>';
   if ord (value) = 7 then result := '<end of line>';
   if ord (value) = 8 then result := '(';
   if ord (value) = 9 then result := ')';
   if ord (value) = 10 then result := '*';
   if ord (value) = 11 then result := '+';
   if ord (value) = 12 then result := ',';
   if ord (value) = 13 then result := '-';
   if ord (value) = 14 then result := '.';
   if ord (value) = 15 then result := '..';
   if ord (value) = 16 then result := '/';
   if ord (value) = 17 then result := ':';
   if ord (value) = 18 then result := ':=';
   if ord (value) = 19 then result := ';';
   if ord (value) = 20 then result := '<';
   if ord (value) = 21 then result := '<=';
   if ord (value) = 22 then result := '<>';
   if ord (value) = 23 then result := '=';
   if ord (value) = 24 then result := '>';
   if ord (value) = 25 then result := '>=';
   if ord (value) = 26 then result := '@';
   if ord (value) = 27 then result := '[';
   if ord (value) = 28 then result := ']';
   if ord (value) = 29 then result := '^';
   if ord (value) = 30 then result := 'abstract';
   if ord (value) = 31 then result := 'and';
   if ord (value) = 32 then result := 'array';
   if ord (value) = 33 then result := 'as';
   if ord (value) = 34 then result := 'automated';
   if ord (value) = 35 then result := 'begin';
   if ord (value) = 36 then result := 'case';
   if ord (value) = 37 then result := 'cdecl';
   if ord (value) = 38 then result := 'class';
   if ord (value) = 39 then result := 'const';
   if ord (value) = 40 then result := 'constructor';
   if ord (value) = 41 then result := 'default';
   if ord (value) = 42 then result := 'destructor';
   if ord (value) = 43 then result := 'div';
   if ord (value) = 44 then result := 'do';
   if ord (value) = 45 then result := 'downto';
   if ord (value) = 46 then result := 'dynamic';
   if ord (value) = 47 then result := 'else';
   if ord (value) = 48 then result := 'end';
   if ord (value) = 49 then result := 'except';
   if ord (value) = 50 then result := 'external';
   if ord (value) = 51 then result := 'file';
   if ord (value) = 52 then result := 'finalization';
   if ord (value) = 53 then result := 'finally';
   if ord (value) = 54 then result := 'for';
   if ord (value) = 55 then result := 'forward';
   if ord (value) = 56 then result := 'function';
   if ord (value) = 57 then result := 'goto';
   if ord (value) = 58 then result := 'if';
   if ord (value) = 59 then result := 'implementation';
   if ord (value) = 60 then result := 'implements';
   if ord (value) = 61 then result := 'in';
   if ord (value) = 62 then result := 'inherited';
   if ord (value) = 63 then result := 'initialization';
   if ord (value) = 64 then result := 'inline';
   if ord (value) = 65 then result := 'interface';
   if ord (value) = 66 then result := 'is';
   if ord (value) = 67 then result := 'label';
   if ord (value) = 68 then result := 'library';
   if ord (value) = 69 then result := 'mod';
   if ord (value) = 70 then result := 'nil';
   if ord (value) = 71 then result := 'nodefault';
   if ord (value) = 72 then result := 'not';
   if ord (value) = 73 then result := 'object';
   if ord (value) = 74 then result := 'of';
   if ord (value) = 75 then result := 'on';
   if ord (value) = 76 then result := 'or';
   if ord (value) = 77 then result := 'out';
   if ord (value) = 78 then result := 'override';
   if ord (value) = 79 then result := 'packed';
   if ord (value) = 80 then result := 'pascal';
   if ord (value) = 81 then result := 'private';
   if ord (value) = 82 then result := 'procedure';
   if ord (value) = 83 then result := 'program';
   if ord (value) = 84 then result := 'property';
   if ord (value) = 85 then result := 'protected';
   if ord (value) = 86 then result := 'public';
   if ord (value) = 87 then result := 'published';
   if ord (value) = 88 then result := 'raise';
   if ord (value) = 89 then result := 'read';
   if ord (value) = 90 then result := 'record';
   if ord (value) = 91 then result := 'register';
   if ord (value) = 92 then result := 'repeat';
   if ord (value) = 93 then result := 'safecall';
   if ord (value) = 94 then result := 'set';
   if ord (value) = 95 then result := 'shl';
   if ord (value) = 96 then result := 'shr';
   if ord (value) = 97 then result := 'stdcall';
   if ord (value) = 98 then result := 'stored';
   if ord (value) = 99 then result := 'string';
   if ord (value) = 100 then result := 'then';
   if ord (value) = 101 then result := 'to';
   if ord (value) = 102 then result := 'try';
   if ord (value) = 103 then result := 'type';
   if ord (value) = 104 then result := 'unit';
   if ord (value) = 105 then result := 'until';
   if ord (value) = 106 then result := 'uses';
   if ord (value) = 107 then result := 'var';
   if ord (value) = 108 then result := 'virtual';
   if ord (value) = 109 then result := 'while';
   if ord (value) = 110 then result := 'with';
   if ord (value) = 111 then result := 'write';
   if ord (value) = 112 then result := 'xor';
   result := '<unknown symbol>';
end;

procedure Parser.translate;
begin
   if tokenKind = identToken then begin
      token := identifier;
      lookupKeyword;
   end
   else if tokenKind = numberToken then begin
      token := number;
   end
   else if tokenKind = realToken then begin
      token := real_number;
   end
   else if tokenKind = charToken then begin
      token := character_literal;
   end
   else if tokenKind = stringToken then begin
      token := string_literal;
   end
   else if tokenKind = eofToken then begin
      token := eos;
   end
   else begin
      token := separator;
      processSeparator;
   end;
end;

procedure Parser.storeLocation (item : TItem);
begin
   item.src_line := TokenLine;
   item.src_col := TokenCol;
end;

constructor Parser.create;
begin
   inherited create (nil);
end;

function Parser.isSymbol (sym : Symbol) : boolean;
begin
   result := token = sym;
end;

procedure Parser.checkSymbol (sym : Symbol);
begin
   if token <> sym then
      error (tokenToString (sym) + ' expected');
   nextToken;
end;

function Parser.testSymbols (table : array of byte) : boolean;
var pos, bit: integer;
begin
   pos := ord (token) div 8;
   bit := ord (token) mod 8;
   result := table [pos] and (1 shl bit) <> 0;
end;

procedure Parser.stop;
begin
   error ('Unexpected' + tokenToString (token));
end;

procedure Parser.on_ident_expr (item: TIdentExpr); begin end;
procedure Parser.on_field_expr (item: TFieldExpr); begin end;
procedure Parser.on_param (item: TParamIdent); begin end;
procedure Parser.add_param (item: TParamItem); begin end;
procedure Parser.open_class (item: TClassType); begin end;
procedure Parser.close_class (item: TClassType); begin end;
procedure Parser.open_interface (item: TInterfaceType); begin end;
procedure Parser.close_interface (item: TInterfaceType); begin end;
procedure Parser.on_field (item: TFieldItem); begin end;
procedure Parser.add_field (item: TFieldDecl); begin end;
procedure Parser.open_proc (item: TProcDecl); begin end;
procedure Parser.close_proc (item: TProcDecl); begin end;
procedure Parser.simple_type (item: TItem); begin end;
procedure Parser.on_const (item: TConstDecl); begin end;
procedure Parser.add_const (item: TConstDecl); begin end;
procedure Parser.on_type (item: TTypeDecl); begin end;
procedure Parser.add_type (item: TTypeDecl); begin end;
procedure Parser.on_var (item: TVarItem); begin end;
procedure Parser.add_var (item: TVarDecl); begin end;
procedure Parser.on_proc (item: TProcDecl); begin end;
procedure Parser.on_begin_proc (item: TProcDecl); begin end;
procedure Parser.on_end_proc (item: TProcDecl); begin end;
procedure Parser.on_tail_proc (item: TProcDecl); begin end;
procedure Parser.on_import (item: TImportItem); begin end;
procedure Parser.open_module (item: TItem); begin end;
procedure Parser.on_module (item: TItem); begin end;
procedure Parser.close_module (item: TItem); begin end;

constructor TBasic.create;
begin
   inherited create;
   src_file := 0;
   src_line := 0;
   src_column := 0;
end;

function TBasic.conv_TBasic : TBasic; begin result := self; end;

constructor TExpr.create;
begin
   inherited create;
   fce := TFce (0);
end;

function TExpr.conv_TBinaryExpr : TBinaryExpr; begin result := nil; end;
function TExpr.conv_TIdentExpr : TIdentExpr; begin result := nil; end;
function TExpr.conv_TIntValueExpr : TIntValueExpr; begin result := nil; end;
function TExpr.conv_TFltValueExpr : TFltValueExpr; begin result := nil; end;
function TExpr.conv_TStrValueExpr : TStrValueExpr; begin result := nil; end;
function TExpr.conv_TNilExpr : TNilExpr; begin result := nil; end;
function TExpr.conv_TStructExpr : TStructExpr; begin result := nil; end;
function TExpr.conv_TNotExpr : TNotExpr; begin result := nil; end;
function TExpr.conv_TPlusExpr : TPlusExpr; begin result := nil; end;
function TExpr.conv_TMinusExpr : TMinusExpr; begin result := nil; end;
function TExpr.conv_TAdrExpr : TAdrExpr; begin result := nil; end;
function TExpr.conv_TSetExpr : TSetExpr; begin result := nil; end;
function TExpr.conv_TSuperExpr : TSuperExpr; begin result := nil; end;
function TExpr.conv_TStringExpr : TStringExpr; begin result := nil; end;
function TExpr.conv_TIndexExpr : TIndexExpr; begin result := nil; end;
function TExpr.conv_TCallExpr : TCallExpr; begin result := nil; end;
function TExpr.conv_TDerefExpr : TDerefExpr; begin result := nil; end;
function TExpr.conv_TFieldExpr : TFieldExpr; begin result := nil; end;
function TExpr.conv_TTermExpr : TTermExpr; begin result := nil; end;
function TExpr.conv_TSimpleExpr : TSimpleExpr; begin result := nil; end;
function TExpr.conv_TCompleteExpr : TCompleteExpr; begin result := nil; end;
function TExpr.conv_TExpr : TExpr; begin result := self; end;

constructor TBinaryExpr.create;
begin
   inherited create;
   left := nil;
   right := nil;
end;

function TBinaryExpr.conv_TBinaryExpr : TBinaryExpr; begin result := self; end;

constructor TComponentsItem.create;
begin
   inherited create;
   acs := TAccess (0);
   members := nil;
end;

function TComponentsItem.conv_TComponentsItem : TComponentsItem; begin result := self; end;

constructor TParamItem.create;
begin
   inherited create;
   mode := TParamMode (0);
   items := [ ];
   typ := nil;
   ini := nil;
end;

function TParamItem.conv_TParamItem : TParamItem; begin result := self; end;

constructor TModule.create;
begin
   inherited create;
   intf_imports := nil;
   impl_imports := nil;
   intf_decl := nil;
   impl_decl := nil;
   init := nil;
   finish := nil;
end;

function TModule.conv_TUnitModule : TUnitModule; begin result := nil; end;
function TModule.conv_TProgramModule : TProgramModule; begin result := nil; end;
function TModule.conv_TLibraryModule : TLibraryModule; begin result := nil; end;
function TModule.conv_TModule : TModule; begin result := self; end;

constructor TLabelIdent.create;
begin
   inherited create;
   id := '';
end;

function TLabelIdent.conv_TLabelIdent : TLabelIdent; begin result := self; end;

constructor TQualName.create;
begin
   inherited create;
   id := '';
   items := [ ];
end;

function TQualName.conv_TQualName : TQualName; begin result := self; end;

constructor TContName.create;
begin
   inherited create;
   id := '';
end;

function TContName.conv_TContName : TContName; begin result := self; end;

constructor TType.create;
begin
   inherited create;
end;

function TType.conv_TAliasType : TAliasType; begin result := nil; end;
function TType.conv_TStringType : TStringType; begin result := nil; end;
function TType.conv_TFileType : TFileType; begin result := nil; end;
function TType.conv_TClassType : TClassType; begin result := nil; end;
function TType.conv_TInterfaceType : TInterfaceType; begin result := nil; end;
function TType.conv_TEnumType : TEnumType; begin result := nil; end;
function TType.conv_TArrayType : TArrayType; begin result := nil; end;
function TType.conv_TRecordType : TRecordType; begin result := nil; end;
function TType.conv_TPointerType : TPointerType; begin result := nil; end;
function TType.conv_TSetType : TSetType; begin result := nil; end;
function TType.conv_TClassOfType : TClassOfType; begin result := nil; end;
function TType.conv_TProcType : TProcType; begin result := nil; end;
function TType.conv_TSubrangeType : TSubrangeType; begin result := nil; end;
function TType.conv_TType : TType; begin result := self; end;

constructor TAliasType.create;
begin
   inherited create;
   alias_name := nil;
end;

function TAliasType.conv_TAliasType : TAliasType; begin result := self; end;

constructor TStringType.create;
begin
   inherited create;
   lim := nil;
end;

function TStringType.conv_TStringType : TStringType; begin result := self; end;

constructor TFileType.create;
begin
   inherited create;
   elem := nil;
end;

function TFileType.conv_TFileType : TFileType; begin result := self; end;

constructor TInxItem.create;
begin
   inherited create;
   ref := nil;
end;

function TInxItem.conv_TInxItem : TInxItem; begin result := self; end;

constructor TInxList.create;
begin
   inherited create;
   items := [ ];
end;

function TInxList.conv_TInxList : TInxList; begin result := self; end;

constructor TArgItem.create;
begin
   inherited create;
   value := nil;
   width := nil;
   digits := nil;
end;

function TArgItem.conv_TArgItem : TArgItem; begin result := self; end;

constructor TArgSect.create;
begin
   inherited create;
   items := [ ];
end;

function TArgSect.conv_TArgSect : TArgSect; begin result := self; end;

constructor TElemSect.create;
begin
   inherited create;
   items := [ ];
end;

function TElemSect.conv_TElemSect : TElemSect; begin result := self; end;

constructor TElemItem.create;
begin
   inherited create;
   low := nil;
   high := nil;
end;

function TElemItem.conv_TElemItem : TElemItem; begin result := self; end;

constructor TStructSect.create;
begin
   inherited create;
   name := '';
   value := nil;
   items := [ ];
end;

function TStructSect.conv_TStructSect : TStructSect; begin result := self; end;

constructor TIdentExpr.create;
begin
   inherited create;
   name := '';
end;

function TIdentExpr.conv_TIdentExpr : TIdentExpr; begin result := self; end;

constructor TIntValueExpr.create;
begin
   inherited create;
   value := '';
end;

function TIntValueExpr.conv_TIntValueExpr : TIntValueExpr; begin result := self; end;

constructor TFltValueExpr.create;
begin
   inherited create;
   value := '';
end;

function TFltValueExpr.conv_TFltValueExpr : TFltValueExpr; begin result := self; end;

constructor TStrValueExpr.create;
begin
   inherited create;
   value := '';
end;

function TStrValueExpr.conv_TStrValueExpr : TStrValueExpr; begin result := self; end;

constructor TNilExpr.create;
begin
   inherited create;
end;

function TNilExpr.conv_TNilExpr : TNilExpr; begin result := self; end;

constructor TStructExpr.create;
begin
   inherited create;
   value := nil;
end;

function TStructExpr.conv_TStructExpr : TStructExpr; begin result := self; end;

constructor TNotExpr.create;
begin
   inherited create;
   param := nil;
end;

function TNotExpr.conv_TNotExpr : TNotExpr; begin result := self; end;

constructor TPlusExpr.create;
begin
   inherited create;
   param := nil;
end;

function TPlusExpr.conv_TPlusExpr : TPlusExpr; begin result := self; end;

constructor TMinusExpr.create;
begin
   inherited create;
   param := nil;
end;

function TMinusExpr.conv_TMinusExpr : TMinusExpr; begin result := self; end;

constructor TAdrExpr.create;
begin
   inherited create;
   param := nil;
end;

function TAdrExpr.conv_TAdrExpr : TAdrExpr; begin result := self; end;

constructor TSetExpr.create;
begin
   inherited create;
   list := nil;
end;

function TSetExpr.conv_TSetExpr : TSetExpr; begin result := self; end;

constructor TSuperExpr.create;
begin
   inherited create;
   name := '';
end;

function TSuperExpr.conv_TSuperExpr : TSuperExpr; begin result := self; end;

constructor TStringExpr.create;
begin
   inherited create;
   param := nil;
end;

function TStringExpr.conv_TStringExpr : TStringExpr; begin result := self; end;

constructor TIndexExpr.create;
begin
   inherited create;
   left := nil;
   list := nil;
end;

function TIndexExpr.conv_TIndexExpr : TIndexExpr; begin result := self; end;

constructor TCallExpr.create;
begin
   inherited create;
   func := nil;
   list := nil;
end;

function TCallExpr.conv_TCallExpr : TCallExpr; begin result := self; end;

constructor TDerefExpr.create;
begin
   inherited create;
   param := nil;
end;

function TDerefExpr.conv_TDerefExpr : TDerefExpr; begin result := self; end;

constructor TFieldExpr.create;
begin
   inherited create;
   param := nil;
   name := '';
end;

function TFieldExpr.conv_TFieldExpr : TFieldExpr; begin result := self; end;

constructor TStat.create;
begin
   inherited create;
end;

function TStat.conv_TGotoStat : TGotoStat; begin result := nil; end;
function TStat.conv_TBlockStat : TBlockStat; begin result := nil; end;
function TStat.conv_TIfStat : TIfStat; begin result := nil; end;
function TStat.conv_TCaseStat : TCaseStat; begin result := nil; end;
function TStat.conv_TWhileStat : TWhileStat; begin result := nil; end;
function TStat.conv_TRepeatStat : TRepeatStat; begin result := nil; end;
function TStat.conv_TForStat : TForStat; begin result := nil; end;
function TStat.conv_TWithStat : TWithStat; begin result := nil; end;
function TStat.conv_TRaiseStat : TRaiseStat; begin result := nil; end;
function TStat.conv_TTryStat : TTryStat; begin result := nil; end;
function TStat.conv_TEmptyStat : TEmptyStat; begin result := nil; end;
function TStat.conv_TAssignStat : TAssignStat; begin result := nil; end;
function TStat.conv_TCallStat : TCallStat; begin result := nil; end;
function TStat.conv_TLabeledTStat : TLabeledTStat; begin result := nil; end;
function TStat.conv_TStat : TStat; begin result := self; end;

constructor TGotoStat.create;
begin
   inherited create;
   goto_lab := nil;
end;

function TGotoStat.conv_TGotoStat : TGotoStat; begin result := self; end;

constructor TBlockStat.create;
begin
   inherited create;
   body_seq := nil;
end;

function TBlockStat.conv_TBlockStat : TBlockStat; begin result := self; end;

constructor TStatSeq.create;
begin
   inherited create;
   items := [ ];
end;

function TStatSeq.conv_TStatSeq : TStatSeq; begin result := self; end;

constructor TIfStat.create;
begin
   inherited create;
   cond_expr := nil;
   then_stat := nil;
   else_stat := nil;
end;

function TIfStat.conv_TIfStat : TIfStat; begin result := self; end;

constructor TCaseStat.create;
begin
   inherited create;
   case_expr := nil;
   case_list := nil;
   else_seq := nil;
end;

function TCaseStat.conv_TCaseStat : TCaseStat; begin result := self; end;

constructor TCaseSect.create;
begin
   inherited create;
   items := [ ];
end;

function TCaseSect.conv_TCaseSect : TCaseSect; begin result := self; end;

constructor TCaseItem.create;
begin
   inherited create;
   sel_list := nil;
   sel_stat := nil;
end;

function TCaseItem.conv_TCaseItem : TCaseItem; begin result := self; end;

constructor TWhileStat.create;
begin
   inherited create;
   cond_expr := nil;
   body_stat := nil;
end;

function TWhileStat.conv_TWhileStat : TWhileStat; begin result := self; end;

constructor TRepeatStat.create;
begin
   inherited create;
   body_seq := nil;
   until_expr := nil;
end;

function TRepeatStat.conv_TRepeatStat : TRepeatStat; begin result := self; end;

constructor TForStat.create;
begin
   inherited create;
   var_expr := nil;
   from_expr := nil;
   incr := false;
   to_expr := nil;
   body_stat := nil;
end;

function TForStat.conv_TForStat : TForStat; begin result := self; end;

constructor TWithStat.create;
begin
   inherited create;
   with_list := nil;
   body_stat := nil;
end;

function TWithStat.conv_TWithStat : TWithStat; begin result := self; end;

constructor TWithSect.create;
begin
   inherited create;
   items := [ ];
end;

function TWithSect.conv_TWithSect : TWithSect; begin result := self; end;

constructor TWithItem.create;
begin
   inherited create;
   expr := nil;
end;

function TWithItem.conv_TWithItem : TWithItem; begin result := self; end;

constructor TRaiseStat.create;
begin
   inherited create;
   raise_expr := nil;
end;

function TRaiseStat.conv_TRaiseStat : TRaiseStat; begin result := self; end;

constructor TTryStat.create;
begin
   inherited create;
   body_seq := nil;
   finally_branch := nil;
   except_branch := nil;
end;

function TTryStat.conv_TTryStat : TTryStat; begin result := self; end;

constructor TFinallyPart.create;
begin
   inherited create;
   finally_seq := nil;
end;

function TFinallyPart.conv_TFinallyPart : TFinallyPart; begin result := self; end;

constructor TExceptPart.create;
begin
   inherited create;
   on_list := nil;
   else_seq := nil;
end;

function TExceptPart.conv_TExceptPart : TExceptPart; begin result := self; end;

constructor TOnSect.create;
begin
   inherited create;
   items := [ ];
   semicolon := false;
end;

function TOnSect.conv_TOnSect : TOnSect; begin result := self; end;

constructor TOnItem.create;
begin
   inherited create;
   on_ident := '';
   on_type := nil;
   body_stat := nil;
end;

function TOnItem.conv_TOnItem : TOnItem; begin result := self; end;

constructor TEmptyStat.create;
begin
   inherited create;
end;

function TEmptyStat.conv_TEmptyStat : TEmptyStat; begin result := self; end;

constructor TAssignStat.create;
begin
   inherited create;
   left_expr := nil;
   right_expr := nil;
end;

function TAssignStat.conv_TAssignStat : TAssignStat; begin result := self; end;

constructor TCallStat.create;
begin
   inherited create;
   call_expr := nil;
end;

function TCallStat.conv_TCallStat : TCallStat; begin result := self; end;

constructor TLabeledTStat.create;
begin
   inherited create;
   lab := nil;
   body := nil;
end;

function TLabeledTStat.conv_TLabeledTStat : TLabeledTStat; begin result := self; end;

constructor TParamIdent.create;
begin
   inherited create;
   name := '';
end;

function TParamIdent.conv_TParamIdent : TParamIdent; begin result := self; end;

constructor TParamSect.create;
begin
   inherited create;
   items := [ ];
end;

function TParamSect.conv_TParamSect : TParamSect; begin result := self; end;

constructor TClassType.create;
begin
   inherited create;
   parent := nil;
   ifc_list := nil;
   components := nil;
end;

function TClassType.conv_TClassType : TClassType; begin result := self; end;

constructor TInterfaceType.create;
begin
   inherited create;
   ifc_list := nil;
   components := nil;
end;

function TInterfaceType.conv_TInterfaceType : TInterfaceType; begin result := self; end;

constructor TInterfaceSect.create;
begin
   inherited create;
   items := [ ];
end;

function TInterfaceSect.conv_TInterfaceSect : TInterfaceSect; begin result := self; end;

constructor TIntefaceItem.create;
begin
   inherited create;
   ifc := nil;
end;

function TIntefaceItem.conv_TIntefaceItem : TIntefaceItem; begin result := self; end;

constructor TComponetsSect.create;
begin
   inherited create;
   items := [ ];
end;

function TComponetsSect.conv_TComponetsSect : TComponetsSect; begin result := self; end;

constructor TDeclGroup.create;
begin
   inherited create;
   items := [ ];
end;

function TDeclGroup.conv_TDeclGroup : TDeclGroup; begin result := self; end;

constructor TDeclSect.create;
begin
   inherited create;
end;

function TDeclSect.conv_TFieldDecl : TFieldDecl; begin result := nil; end;
function TDeclSect.conv_TPropertyDecl : TPropertyDecl; begin result := nil; end;
function TDeclSect.conv_TLabelSect : TLabelSect; begin result := nil; end;
function TDeclSect.conv_TConstSect : TConstSect; begin result := nil; end;
function TDeclSect.conv_TTypeSect : TTypeSect; begin result := nil; end;
function TDeclSect.conv_TVarSect : TVarSect; begin result := nil; end;
function TDeclSect.conv_TProcDecl : TProcDecl; begin result := nil; end;
function TDeclSect.conv_TDeclSect : TDeclSect; begin result := self; end;

constructor TFieldItem.create;
begin
   inherited create;
   name := '';
end;

function TFieldItem.conv_TFieldItem : TFieldItem; begin result := self; end;

constructor TFieldDecl.create;
begin
   inherited create;
   items := [ ];
   typ := nil;
end;

function TFieldDecl.conv_TFieldDecl : TFieldDecl; begin result := self; end;

constructor TPropertyDecl.create;
begin
   inherited create;
   name := '';
   param_list := nil;
   typ := nil;
   a_read := nil;
   a_write := nil;
   a_stored := false;
   a_default := false;
   a_nodefault := false;
   a_implements := nil;
   a_def_array := false;
end;

function TPropertyDecl.conv_TPropertyDecl : TPropertyDecl; begin result := self; end;

constructor TEnumType.create;
begin
   inherited create;
   elements := nil;
end;

function TEnumType.conv_TEnumType : TEnumType; begin result := self; end;

constructor TEnumSect.create;
begin
   inherited create;
   items := [ ];
end;

function TEnumSect.conv_TEnumSect : TEnumSect; begin result := self; end;

constructor TEnumItem.create;
begin
   inherited create;
   name := '';
end;

function TEnumItem.conv_TEnumItem : TEnumItem; begin result := self; end;

constructor TArrayType.create;
begin
   inherited create;
   index_list := nil;
   elem := nil;
end;

function TArrayType.conv_TArrayType : TArrayType; begin result := self; end;

constructor TIndexTypeSect.create;
begin
   inherited create;
   items := [ ];
end;

function TIndexTypeSect.conv_TIndexTypeSect : TIndexTypeSect; begin result := self; end;

constructor TIndexTypeItem.create;
begin
   inherited create;
   index := nil;
end;

function TIndexTypeItem.conv_TIndexTypeItem : TIndexTypeItem; begin result := self; end;

constructor TRecordType.create;
begin
   inherited create;
   a_packed := false;
   fields := nil;
end;

function TRecordType.conv_TRecordType : TRecordType; begin result := self; end;

constructor TFieldDeclGroup.create;
begin
   inherited create;
   items := [ ];
end;

function TFieldDeclGroup.conv_TFieldDeclGroup : TFieldDeclGroup; begin result := self; end;

constructor TPointerType.create;
begin
   inherited create;
   elem := nil;
end;

function TPointerType.conv_TPointerType : TPointerType; begin result := self; end;

constructor TSetType.create;
begin
   inherited create;
   elem := nil;
end;

function TSetType.conv_TSetType : TSetType; begin result := self; end;

constructor TClassOfType.create;
begin
   inherited create;
   elem := nil;
end;

function TClassOfType.conv_TClassOfType : TClassOfType; begin result := self; end;

constructor TProcType.create;
begin
   inherited create;
   style := TStyle (0);
   call_conv := TCall (0);
   param_list := nil;
   answer := nil;
   of_object := false;
end;

function TProcType.conv_TProcType : TProcType; begin result := self; end;

constructor TSubrangeType.create;
begin
   inherited create;
   low := nil;
   high := nil;
end;

function TSubrangeType.conv_TSubrangeType : TSubrangeType; begin result := self; end;

constructor TLabelDecl.create;
begin
   inherited create;
   name := nil;
end;

function TLabelDecl.conv_TLabelDecl : TLabelDecl; begin result := self; end;

constructor TLabelSect.create;
begin
   inherited create;
   items := [ ];
end;

function TLabelSect.conv_TLabelSect : TLabelSect; begin result := self; end;

constructor TConstDecl.create;
begin
   inherited create;
   name := '';
   typ := nil;
   val := nil;
end;

function TConstDecl.conv_TConstDecl : TConstDecl; begin result := self; end;

constructor TConstSect.create;
begin
   inherited create;
   items := [ ];
end;

function TConstSect.conv_TConstSect : TConstSect; begin result := self; end;

constructor TTypeDecl.create;
begin
   inherited create;
   name := '';
   typ := nil;
end;

function TTypeDecl.conv_TTypeDecl : TTypeDecl; begin result := self; end;

constructor TTypeSect.create;
begin
   inherited create;
   items := [ ];
end;

function TTypeSect.conv_TTypeSect : TTypeSect; begin result := self; end;

constructor TVarItem.create;
begin
   inherited create;
   name := '';
end;

function TVarItem.conv_TVarItem : TVarItem; begin result := self; end;

constructor TVarDecl.create;
begin
   inherited create;
   items := [ ];
   typ := nil;
   ini := nil;
end;

function TVarDecl.conv_TVarDecl : TVarDecl; begin result := self; end;

constructor TVarSect.create;
begin
   inherited create;
   items := [ ];
end;

function TVarSect.conv_TVarSect : TVarSect; begin result := self; end;

constructor TProcDecl.create;
begin
   inherited create;
   style := TStyle (0);
   call_conv := TCall (0);
   a_virtual := false;
   a_dynamic := false;
   a_override := false;
   a_abstract := false;
   a_static := false;
   proc_name := nil;
   param_list := nil;
   answer := nil;
   a_forward := false;
   external_spec := false;
   a_inline := false;
   local := nil;
   body := nil;
   a_external := false;
   a_lib := nil;
end;

function TProcDecl.conv_TProcDecl : TProcDecl; begin result := self; end;

constructor TImportItem.create;
begin
   inherited create;
   name := '';
   path := '';
end;

function TImportItem.conv_TImportItem : TImportItem; begin result := self; end;

constructor TImportSect.create;
begin
   inherited create;
   items := [ ];
end;

function TImportSect.conv_TImportSect : TImportSect; begin result := self; end;

constructor TUnitModule.create;
begin
   inherited create;
   name := '';
   no_begin := false;
end;

function TUnitModule.conv_TUnitModule : TUnitModule; begin result := self; end;

constructor TProgramModule.create;
begin
   inherited create;
   name := '';
end;

function TProgramModule.conv_TProgramModule : TProgramModule; begin result := self; end;

constructor TLibraryModule.create;
begin
   inherited create;
   name := '';
end;

function TLibraryModule.conv_TLibraryModule : TLibraryModule; begin result := self; end;

constructor TTermExpr.create;
begin
   inherited create;
end;

function TTermExpr.conv_TTermExpr : TTermExpr; begin result := self; end;

constructor TSimpleExpr.create;
begin
   inherited create;
end;

function TSimpleExpr.conv_TSimpleExpr : TSimpleExpr; begin result := self; end;

constructor TCompleteExpr.create;
begin
   inherited create;
end;

function TCompleteExpr.conv_TCompleteExpr : TCompleteExpr; begin result := self; end;

end.
