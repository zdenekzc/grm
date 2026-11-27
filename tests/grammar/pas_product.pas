unit pas_product;

interface

uses textio, pas_parser;

type Product = class (TTextOutput)
public
   procedure send_label_ident (param : TLabelIdent);
   procedure send_qualified_name (param : TQualName);
   procedure send_cont_name (param : TContName);
   procedure send_ifc_type (param : TType);
   procedure send_param_type (param : TType);
   procedure send_result_type (param : TType);
   procedure send_simple_alias_type (param : TAliasType);
   procedure send_simple_string_type (param : TStringType);
   procedure send_simple_file_type (param : TFileType);
   procedure send_index_expr_item (param : TInxItem);
   procedure send_index_expr_list (param : TInxList);
   procedure send_arg_item (param : TArgItem);
   procedure send_arg_list (param : TArgSect);
   procedure send_elem_sect (param : TElemSect);
   procedure send_elem_item (param : TElemItem);
   procedure send_struct_item (param : TStructSect);
   procedure send_struct_sect (param : TStructSect);
   procedure send_ident_expr (param : TIdentExpr);
   procedure send_int_value_expr (param : TIntValueExpr);
   procedure send_float_value_expr (param : TFltValueExpr);
   procedure send_string_value_expr (param : TStrValueExpr);
   procedure send_nil_expr (param : TNilExpr);
   procedure send_sub_expr (param : TStructExpr);
   procedure send_not_expr (param : TNotExpr);
   procedure send_plus_expr (param : TPlusExpr);
   procedure send_minus_expr (param : TMinusExpr);
   procedure send_adr_expr (param : TAdrExpr);
   procedure send_set_expr (param : TSetExpr);
   procedure send_super_expr (param : TSuperExpr);
   procedure send_string_type_expr (param : TStringExpr);
   procedure send_variable (param : TExpr);
   procedure send_reference (param : TExpr);
   procedure send_index_expr (param : TIndexExpr);
   procedure send_call_expr (param : TCallExpr);
   procedure send_deref_expr (param : TDerefExpr);
   procedure send_field_expr (param : TFieldExpr);
   procedure send_factor (param : TExpr);
   procedure send_term (param : TExpr);
   procedure send_simple_expr (param : TExpr);
   procedure send_expr (param : TExpr);
   procedure send_goto_stat (param : TGotoStat);
   procedure send_begin_stat (param : TBlockStat);
   procedure send_stat_list (param : TStatSeq);
   procedure send_inner_stat (param : TStat);
   procedure send_if_stat (param : TIfStat);
   procedure send_case_stat (param : TCaseStat);
   procedure send_case_sect (param : TCaseSect);
   procedure send_case_item (param : TCaseItem);
   procedure send_while_stat (param : TWhileStat);
   procedure send_repeat_stat (param : TRepeatStat);
   procedure send_for_stat (param : TForStat);
   procedure send_with_stat (param : TWithStat);
   procedure send_with_sect (param : TWithSect);
   procedure send_with_item (param : TWithItem);
   procedure send_raise_stat (param : TRaiseStat);
   procedure send_try_stat (param : TTryStat);
   procedure send_finally_part (param : TFinallyPart);
   procedure send_except_part (param : TExceptPart);
   procedure send_on_sect (param : TOnSect);
   procedure send_on_item (param : TOnItem);
   procedure send_empty_stat (param : TEmptyStat);
   procedure send_simple_stat (param : TStat);
   procedure send_assign_stat (param : TAssignStat);
   procedure send_call_stat (param : TCallStat);
   procedure send_labeled_stat (param : TLabeledTStat);
   procedure send_stat (param : TStat);
   procedure send_param_ident (param : TParamIdent);
   procedure send_param_item (param : TParamItem);
   procedure send_formal_param_list (param : TParamSect);
   procedure send_property_param_list (param : TParamSect);
   procedure send_class_type (param : TClassType);
   procedure send_interface_type (param : TInterfaceType);
   procedure send_interface_sect (param : TInterfaceSect);
   procedure send_interface_item (param : TIntefaceItem);
   procedure send_components_sect (param : TComponetsSect);
   procedure send_components_item (param : TComponentsItem);
   procedure send_components_first_item (param : TComponentsItem);
   procedure send_member_sect (param : TDeclGroup);
   procedure send_member_decl (param : TDeclSect);
   procedure send_field_ident (param : TFieldItem);
   procedure send_field_decl (param : TFieldDecl);
   procedure send_method_decl (param : TProcDecl);
   procedure send_property_decl (param : TPropertyDecl);
   procedure send_enum_type (param : TEnumType);
   procedure send_enum_sect (param : TEnumSect);
   procedure send_enum_item (param : TEnumItem);
   procedure send_string_type (param : TStringType);
   procedure send_array_type (param : TArrayType);
   procedure send_index_type_sect (param : TIndexTypeSect);
   procedure send_index_type_item (param : TIndexTypeItem);
   procedure send_record_type (param : TRecordType);
   procedure send_field_sect (param : TFieldDeclGroup);
   procedure send_pointer_type (param : TPointerType);
   procedure send_set_type (param : TSetType);
   procedure send_file_type (param : TFileType);
   procedure send_class_of_type (param : TClassOfType);
   procedure send_proc_type (param : TProcType);
   procedure send_range_type (param : TSubrangeType);
   procedure send_alias_type (param : TAliasType);
   procedure send_type (param : TType);
   procedure send_label_decl (param : TLabelDecl);
   procedure send_label_sect (param : TLabelSect);
   procedure send_const_decl (param : TConstDecl);
   procedure send_const_sect (param : TConstSect);
   procedure send_type_decl (param : TTypeDecl);
   procedure send_type_sect (param : TTypeSect);
   procedure send_var_item (param : TVarItem);
   procedure send_var_decl (param : TVarDecl);
   procedure send_var_sect (param : TVarSect);
   procedure send_proc_head (param : TProcDecl);
   procedure send_proc_decl (param : TProcDecl);
   procedure send_proc_external (param : TProcDecl);
   procedure send_proc_intf_decl (param : TProcDecl);
   procedure send_intf_decl (param : TDeclSect);
   procedure send_intf_decl_part (param : TDeclGroup);
   procedure send_decl (param : TDeclSect);
   procedure send_decl_part (param : TDeclGroup);
   procedure send_import_item (param : TImportItem);
   procedure send_import_sect (param : TImportSect);
   procedure send_unit_decl (param : TUnitModule);
   procedure send_program_decl (param : TProgramModule);
   procedure send_library_decl (param : TLibraryModule);
   procedure send_module_decl (param : TModule);
end;

implementation

procedure Product.send_label_ident (param : TLabelIdent);
begin
   send (param.id);
end;

procedure Product.send_qualified_name (param : TQualName);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send (param.id);
   while (inx < cnt) do begin
      send_cont_name (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_cont_name (param : TContName);
begin
   style_no_space ();
   send ('.');
   style_no_space ();
   send (param.id);
end;

procedure Product.send_ifc_type (param : TType);
begin
   send_simple_alias_type (param.conv_TAliasType);
end;

procedure Product.send_param_type (param : TType);
begin
   if (param is TAliasType) then begin
      send_simple_alias_type (param.conv_TAliasType);
   end
   else if (param is TStringType) then begin
      send_simple_string_type (param.conv_TStringType);
   end
   else if (param is TFileType) then begin
      send_simple_file_type (param.conv_TFileType);
   end;
end;

procedure Product.send_result_type (param : TType);
begin
   if (param is TAliasType) then begin
      send_simple_alias_type (param.conv_TAliasType);
   end
   else if (param is TStringType) then begin
      send_simple_string_type (param.conv_TStringType);
   end;
end;

procedure Product.send_simple_alias_type (param : TAliasType);
begin
   send_qualified_name (param.alias_name);
end;

procedure Product.send_simple_string_type (param : TStringType);
begin
   send ('string');
end;

procedure Product.send_simple_file_type (param : TFileType);
begin
   send ('file');
end;

procedure Product.send_index_expr_item (param : TInxItem);
begin
   send_expr (param.ref);
end;

procedure Product.send_index_expr_list (param : TInxList);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_index_expr_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_index_expr_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_arg_item (param : TArgItem);
begin
   send_expr (param.value);
   if (param.width <> nil) then begin
      send (':');
      send_expr (param.width);
      if (param.digits <> nil) then begin
         send (':');
         send_expr (param.digits);
      end;
   end;
end;

procedure Product.send_arg_list (param : TArgSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_arg_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_arg_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_elem_sect (param : TElemSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_elem_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_elem_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_elem_item (param : TElemItem);
begin
   send_expr (param.low);
   if (param.high <> nil) then begin
      send ('..');
      send_expr (param.high);
   end;
end;

procedure Product.send_struct_item (param : TStructSect);
begin
   if (param.name <> '') then begin
      send (param.name);
      send (':');
   end;
   send_expr (param.value);
end;

procedure Product.send_struct_sect (param : TStructSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_struct_item (param.items [inx]);
   inc (inx);
   if (inx < cnt) or (inx < cnt) then begin

      if (inx < cnt) then begin
         send (',');
         send_struct_item (param.items [inx]);
         inc (inx);
         while (inx < cnt) do begin
            send (',');
            send_struct_item (param.items [inx]);
            inc (inx);
         end;
      end
      else if (inx < cnt) then begin
         send (';');
         send_struct_item (param.items [inx]);
         inc (inx);
         while (inx < cnt) do begin
            send (';');
            send_struct_item (param.items [inx]);
            inc (inx);
         end;
      end;
   end;
end;

procedure Product.send_ident_expr (param : TIdentExpr);
begin
   send (param.name);
end;

procedure Product.send_int_value_expr (param : TIntValueExpr);
begin
   send (param.value);
end;

procedure Product.send_float_value_expr (param : TFltValueExpr);
begin
   send (param.value);
end;

procedure Product.send_string_value_expr (param : TStrValueExpr);
begin
   putString (param.value);
end;

procedure Product.send_nil_expr (param : TNilExpr);
begin
   send ('nil');
end;

procedure Product.send_sub_expr (param : TStructExpr);
begin
   send ('(');
   send_expr (param.value);
   send (')');
end;

procedure Product.send_not_expr (param : TNotExpr);
begin
   send ('not');
   send_factor (param.param);
end;

procedure Product.send_plus_expr (param : TPlusExpr);
begin
   send ('+');
   send_factor (param.param);
end;

procedure Product.send_minus_expr (param : TMinusExpr);
begin
   send ('-');
   send_factor (param.param);
end;

procedure Product.send_adr_expr (param : TAdrExpr);
begin
   send ('@');
   send_factor (param.param);
end;

procedure Product.send_set_expr (param : TSetExpr);
begin
   send ('[');
   send_elem_sect (param.list);
   send (']');
end;

procedure Product.send_super_expr (param : TSuperExpr);
begin
   send ('inherited');
   send (param.name);
end;

procedure Product.send_string_type_expr (param : TStringExpr);
begin
   send ('string');
   send ('(');
   send_expr (param.param);
   send (')');
end;

procedure Product.send_variable (param : TExpr);
begin
   if (param is TIdentExpr) then begin
      send_ident_expr (param.conv_TIdentExpr);
   end
   else if (param is TStructExpr) then begin
      send_sub_expr (param.conv_TStructExpr);
   end
   else if (param is TSuperExpr) then begin
      send_super_expr (param.conv_TSuperExpr);
   end;
end;

procedure Product.send_reference (param : TExpr);
begin
   if (param is TIndexExpr) then begin
      send_variable (param.conv_TIndexExpr.left.conv_TExpr);
      send_index_expr (param.conv_TIndexExpr.conv_TIndexExpr);
   end
   else if (param is TCallExpr) then begin
      send_variable (param.conv_TCallExpr.func.conv_TExpr);
      send_call_expr (param.conv_TCallExpr.conv_TCallExpr);
   end
   else if (param is TDerefExpr) then begin
      send_variable (param.conv_TDerefExpr.param.conv_TExpr);
      send_deref_expr (param.conv_TDerefExpr.conv_TDerefExpr);
   end
   else if (param is TFieldExpr) then begin
      send_variable (param.conv_TFieldExpr.param.conv_TExpr);
      send_field_expr (param.conv_TFieldExpr.conv_TFieldExpr);
   end
   else begin
      send_variable (param.conv_TExpr);
   end;
   ;
end;

procedure Product.send_index_expr (param : TIndexExpr);
begin
   send ('[');
   send_index_expr_list (param.list);
   send (']');
end;

procedure Product.send_call_expr (param : TCallExpr);
begin
   send ('(');
   send_arg_list (param.list);
   send (')');
end;

procedure Product.send_deref_expr (param : TDerefExpr);
begin
   send ('^');
end;

procedure Product.send_field_expr (param : TFieldExpr);
begin
   style_no_space ();
   send ('.');
   style_no_space ();
   send (param.name);
end;

procedure Product.send_factor (param : TExpr);
begin
   if (param is TIntValueExpr) then begin
      send_int_value_expr (param.conv_TIntValueExpr);
   end
   else if (param is TFltValueExpr) then begin
      send_float_value_expr (param.conv_TFltValueExpr);
   end
   else if (param is TStrValueExpr) then begin
      send_string_value_expr (param.conv_TStrValueExpr);
   end
   else if (param is TNotExpr) then begin
      send_not_expr (param.conv_TNotExpr);
   end
   else if (param is TPlusExpr) then begin
      send_plus_expr (param.conv_TPlusExpr);
   end
   else if (param is TMinusExpr) then begin
      send_minus_expr (param.conv_TMinusExpr);
   end
   else if (param is TAdrExpr) then begin
      send_adr_expr (param.conv_TAdrExpr);
   end
   else if (param is TNilExpr) then begin
      send_nil_expr (param.conv_TNilExpr);
   end
   else if (param is TSetExpr) then begin
      send_set_expr (param.conv_TSetExpr);
   end
   else if (param is TStringExpr) then begin
      send_string_type_expr (param.conv_TStringExpr);
   end
   else if (param is TExpr) then begin
      send_reference (param.conv_TExpr);
   end;
end;

procedure Product.send_term (param : TExpr);
begin
   if param.fce = MulExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('*');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = RDivExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('/');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = DivExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('div');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = ModExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('mod');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = ShlExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('shl');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = ShrExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('shr');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = AndExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('and');
      send_factor (param.conv_TTermExpr.right);
   end
   else if param.fce = AsExp then begin
      send_factor (param.conv_TTermExpr.left.conv_TExpr);
      send ('as');
      send_factor (param.conv_TTermExpr.right);
   end
   else begin
      send_factor (param.conv_TExpr);
   end;
   ;
end;

procedure Product.send_simple_expr (param : TExpr);
begin
   if param.fce = AddExp then begin
      send_term (param.conv_TSimpleExpr.left.conv_TExpr);
      send ('+');
      send_term (param.conv_TSimpleExpr.right);
   end
   else if param.fce = SubExp then begin
      send_term (param.conv_TSimpleExpr.left.conv_TExpr);
      send ('-');
      send_term (param.conv_TSimpleExpr.right);
   end
   else if param.fce = OrExp then begin
      send_term (param.conv_TSimpleExpr.left.conv_TExpr);
      send ('or');
      send_term (param.conv_TSimpleExpr.right);
   end
   else if param.fce = XorExp then begin
      send_term (param.conv_TSimpleExpr.left.conv_TExpr);
      send ('xor');
      send_term (param.conv_TSimpleExpr.right);
   end
   else begin
      send_term (param.conv_TExpr);
   end;
   ;
end;

procedure Product.send_expr (param : TExpr);
begin
   if param.fce = EqExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('=');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = NeExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('<>');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = LtExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('<');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = GtExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('>');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = LeExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('<=');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = GeExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('>=');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = InExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('in');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else if param.fce = IsExp then begin
      send_simple_expr (param.conv_TCompleteExpr.left.conv_TExpr);
      send ('is');
      send_simple_expr (param.conv_TCompleteExpr.right);
   end
   else begin
      send_simple_expr (param.conv_TExpr);
   end;
   ;
end;

procedure Product.send_goto_stat (param : TGotoStat);
begin
   send ('goto');
   send_label_ident (param.goto_lab);
end;

procedure Product.send_begin_stat (param : TBlockStat);
begin
   send ('begin');
   send_stat_list (param.body_seq);
   send ('end');
end;

procedure Product.send_stat_list (param : TStatSeq);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   style_new_line ();
   style_indent ();
   send_stat (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (';');
      style_new_line ();
      send_stat (param.items [inx]);
      inc (inx);
   end;
   style_unindent ();
   style_new_line ();
end;

procedure Product.send_inner_stat (param : TStat);
begin
   style_new_line ();
   style_indent ();
   send_stat (param.conv_TStat);
   style_unindent ();
end;

procedure Product.send_if_stat (param : TIfStat);
begin
   send ('if');
   send_expr (param.cond_expr);
   send ('then');
   send_inner_stat (param.then_stat);
   if (param.else_stat <> nil) then begin
      send ('else');
      send_inner_stat (param.else_stat);
   end;
end;

procedure Product.send_case_stat (param : TCaseStat);
begin
   send ('case');
   send_expr (param.case_expr);
   send ('of');
   send_case_sect (param.case_list);
   if (param.else_seq <> nil) then begin
      send ('else');
      send_stat_list (param.else_seq);
   end;
   send ('end');
end;

procedure Product.send_case_sect (param : TCaseSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_case_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (';');
      style_new_line ();
      send_case_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_case_item (param : TCaseItem);
begin
   send_elem_sect (param.sel_list);
   send (':');
   send_inner_stat (param.sel_stat);
end;

procedure Product.send_while_stat (param : TWhileStat);
begin
   send ('while');
   send_expr (param.cond_expr);
   send ('do');
   send_inner_stat (param.body_stat);
end;

procedure Product.send_repeat_stat (param : TRepeatStat);
begin
   send ('repeat');
   send_stat_list (param.body_seq);
   send ('until');
   send_expr (param.until_expr);
end;

procedure Product.send_for_stat (param : TForStat);
begin
   send ('for');
   send_variable (param.var_expr);
   send (':=');
   send_expr (param.from_expr);

   if param.incr then begin
      send ('to');
   end
   else if not param.incr then begin
      send ('downto');
   end;
   send_expr (param.to_expr);
   send ('do');
   send_inner_stat (param.body_stat);
end;

procedure Product.send_with_stat (param : TWithStat);
begin
   send ('with');
   send_with_sect (param.with_list);
   send ('do');
   send_inner_stat (param.body_stat);
end;

procedure Product.send_with_sect (param : TWithSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_with_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_with_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_with_item (param : TWithItem);
begin
   send_variable (param.expr);
end;

procedure Product.send_raise_stat (param : TRaiseStat);
begin
   send ('raise');
   if (param.raise_expr <> nil) then begin
      send_expr (param.raise_expr);
   end;
end;

procedure Product.send_try_stat (param : TTryStat);
begin
   send ('try');
   send_stat_list (param.body_seq);

   if (param.finally_branch <> nil) then begin
      send_finally_part (param.finally_branch);
   end
   else if (param.except_branch <> nil) then begin
      send_except_part (param.except_branch);
   end;
   send ('end');
end;

procedure Product.send_finally_part (param : TFinallyPart);
begin
   send ('finally');
   send_stat_list (param.finally_seq);
end;

procedure Product.send_except_part (param : TExceptPart);
begin
   send ('except');

   if (param.on_list <> nil) then begin
      send_on_sect (param.on_list);
      if (param.else_seq <> nil) then begin
         send ('else');
         send_stat_list (param.else_seq);
      end;
   end
   else if (param.else_seq <> nil) then begin
      send_stat_list (param.else_seq);
   end;
end;

procedure Product.send_on_sect (param : TOnSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_on_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (';');
      send_on_item (param.items [inx]);
      inc (inx);
   end;
   if param.semicolon then begin
      send (';');
   end;
end;

procedure Product.send_on_item (param : TOnItem);
begin
   send ('on');
   if (param.on_ident <> '') then begin
      send (param.on_ident);
      send (':');
   end;
   send_type (param.on_type);
   send ('do');
   send_inner_stat (param.body_stat);
end;

procedure Product.send_empty_stat (param : TEmptyStat);
begin
end;

procedure Product.send_simple_stat (param : TStat);
begin
   if (param is TAssignStat) then begin
      send_expr (param.conv_TAssignStat.left_expr.conv_TExpr);
      send_assign_stat (param.conv_TAssignStat.conv_TAssignStat);
   end
   else if (param is TCallStat) then begin
      send_expr (param.conv_TCallStat.call_expr.conv_TExpr);
      send_call_stat (param.conv_TCallStat.conv_TCallStat);
   end;
end;

procedure Product.send_assign_stat (param : TAssignStat);
begin
   send (':=');
   send_expr (param.right_expr);
end;

procedure Product.send_call_stat (param : TCallStat);
begin
end;

procedure Product.send_labeled_stat (param : TLabeledTStat);
begin
   send_label_ident (param.lab);
   send (':');
   send_stat (param.body);
end;

procedure Product.send_stat (param : TStat);
begin
   if (param is TLabeledTStat) then begin
      send_labeled_stat (param.conv_TLabeledTStat);
   end
   else if (param is TStat) then begin
      send_simple_stat (param.conv_TStat);
   end
   else if (param is TEmptyStat) then begin
      send_empty_stat (param.conv_TEmptyStat);
   end
   else if (param is TGotoStat) then begin
      send_goto_stat (param.conv_TGotoStat);
   end
   else if (param is TBlockStat) then begin
      send_begin_stat (param.conv_TBlockStat);
   end
   else if (param is TIfStat) then begin
      send_if_stat (param.conv_TIfStat);
   end
   else if (param is TCaseStat) then begin
      send_case_stat (param.conv_TCaseStat);
   end
   else if (param is TWhileStat) then begin
      send_while_stat (param.conv_TWhileStat);
   end
   else if (param is TRepeatStat) then begin
      send_repeat_stat (param.conv_TRepeatStat);
   end
   else if (param is TForStat) then begin
      send_for_stat (param.conv_TForStat);
   end
   else if (param is TWithStat) then begin
      send_with_stat (param.conv_TWithStat);
   end
   else if (param is TRaiseStat) then begin
      send_raise_stat (param.conv_TRaiseStat);
   end
   else if (param is TTryStat) then begin
      send_try_stat (param.conv_TTryStat);
   end;
end;

procedure Product.send_param_ident (param : TParamIdent);
begin
   send (param.name);
end;

procedure Product.send_param_item (param : TParamItem);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);

   if (param.mode = VarParam) then begin
      send ('var');
   end
   else if (param.mode = ConstParam) then begin
      send ('const');
   end
   else if (param.mode = OutParam) then begin
      send ('out');
   end
   else if (param.mode = ValueParam) then begin
   end;
   send_param_ident (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_param_ident (param.items [inx]);
      inc (inx);
   end;
   if (param.typ <> nil) then begin
      send (':');
      send_param_type (param.typ);
      if (param.ini <> nil) then begin
         send ('=');
         send_expr (param.ini);
      end;
   end;
end;

procedure Product.send_formal_param_list (param : TParamSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   if (inx < cnt) then begin
      send ('(');
      send_param_item (param.items [inx]);
      inc (inx);
      while (inx < cnt) do begin
         send (';');
         send_param_item (param.items [inx]);
         inc (inx);
      end;
      send (')');
   end;
end;

procedure Product.send_property_param_list (param : TParamSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send ('[');
   send_param_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (';');
      send_param_item (param.items [inx]);
      inc (inx);
   end;
   send (']');
end;

procedure Product.send_class_type (param : TClassType);
begin
   send ('class');
   if (param.parent <> nil) then begin
      send ('(');
      send_ifc_type (param.parent);
      if (param.ifc_list <> nil) then begin
         send (',');
         send_interface_sect (param.ifc_list);
      end;
      send (')');
   end;
   style_indent ();
   send_components_sect (param.components);
   style_unindent ();
   send ('end');
end;

procedure Product.send_interface_type (param : TInterfaceType);
begin
   send ('interface');
   if (param.ifc_list <> nil) then begin
      send ('(');
      send_interface_sect (param.ifc_list);
      send (')');
   end;
   style_indent ();
   send_components_sect (param.components);
   style_unindent ();
   send ('end');
end;

procedure Product.send_interface_sect (param : TInterfaceSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_interface_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_interface_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_interface_item (param : TIntefaceItem);
begin
   send_ifc_type (param.ifc);
end;

procedure Product.send_components_sect (param : TComponetsSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_components_first_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send_components_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_components_item (param : TComponentsItem);
begin

   if (param.acs = PrivateAccess) then begin
      send ('private');
   end
   else if (param.acs = ProtectedAccess) then begin
      send ('protected');
   end
   else if (param.acs = PublicAccess) then begin
      send ('public');
   end
   else if (param.acs = PublishedAccess) then begin
      send ('published');
   end
   else if (param.acs = AutomatedAccess) then begin
      send ('automated');
   end;
   send_member_sect (param.members);
end;

procedure Product.send_components_first_item (param : TComponentsItem);
begin
   send_member_sect (param.members);
end;

procedure Product.send_member_sect (param : TDeclGroup);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   while (inx < cnt) do begin
      style_new_line ();
      send_member_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_member_decl (param : TDeclSect);
begin
   if (param is TFieldDecl) then begin
      send_field_decl (param.conv_TFieldDecl);
   end
   else if (param is TProcDecl) then begin
      send_method_decl (param.conv_TProcDecl);
   end
   else if (param is TPropertyDecl) then begin
      send_property_decl (param.conv_TPropertyDecl);
   end;
end;

procedure Product.send_field_ident (param : TFieldItem);
begin
   send (param.name);
end;

procedure Product.send_field_decl (param : TFieldDecl);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_field_ident (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_field_ident (param.items [inx]);
      inc (inx);
   end;
   send (':');
   send_type (param.typ);
   send (';');
end;

procedure Product.send_method_decl (param : TProcDecl);
begin
   send_proc_head (param);
   if param.a_virtual or param.a_dynamic or param.a_override or param.a_abstract then begin

      if param.a_virtual then begin
         send ('virtual');
         send (';');
      end
      else if param.a_dynamic then begin
         send ('dynamic');
         send (';');
      end
      else if param.a_override then begin
         send ('override');
         send (';');
      end
      else if param.a_abstract then begin
         send ('abstract');
         send (';');
      end;
   end;
end;

procedure Product.send_property_decl (param : TPropertyDecl);
begin
   send ('property');
   send (param.name);
   if (param.param_list <> nil) then begin
      send_property_param_list (param.param_list);
   end;
   if (param.typ <> nil) then begin
      send (':');
      send_result_type (param.typ);
   end;
   if (param.a_read <> nil) then begin
      send ('read');
      send_expr (param.a_read);
   end;
   if (param.a_write <> nil) then begin
      send ('write');
      send_expr (param.a_write);
   end;
   if param.a_stored then begin
      send ('stored');
   end;
   if param.a_default then begin
      send ('default');
   end;
   if param.a_nodefault then begin
      send ('nodefault');
   end;
   if (param.a_implements <> nil) then begin
      send ('implements');
      send_interface_sect (param.a_implements);
   end;
   if param.a_def_array then begin
      send (';');
      send ('default');
   end;
   send (';');
end;

procedure Product.send_enum_type (param : TEnumType);
begin
   send ('(');
   send_enum_sect (param.elements);
   send (')');
end;

procedure Product.send_enum_sect (param : TEnumSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_enum_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_enum_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_enum_item (param : TEnumItem);
begin
   send (param.name);
end;

procedure Product.send_string_type (param : TStringType);
begin
   send ('string');
   if (param.lim <> nil) then begin
      send ('[');
      send_expr (param.lim);
      send (']');
   end;
end;

procedure Product.send_array_type (param : TArrayType);
begin
   send ('array');
   if (param.index_list <> nil) then begin
      send ('[');
      send_index_type_sect (param.index_list);
      send (']');
   end;
   send ('of');
   send_type (param.elem);
end;

procedure Product.send_index_type_sect (param : TIndexTypeSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_index_type_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_index_type_item (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_index_type_item (param : TIndexTypeItem);
begin
   send_type (param.index);
end;

procedure Product.send_record_type (param : TRecordType);
begin
   if param.a_packed then begin
      send ('packed');
   end;
   send ('record');
   send_field_sect (param.fields);
   send ('end');
end;

procedure Product.send_field_sect (param : TFieldDeclGroup);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   while (inx < cnt) do begin
      send_field_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_pointer_type (param : TPointerType);
begin
   send ('^');
   send_type (param.elem);
end;

procedure Product.send_set_type (param : TSetType);
begin
   send ('set');
   send ('of');
   send_type (param.elem);
end;

procedure Product.send_file_type (param : TFileType);
begin
   send ('file');
   if (param.elem <> nil) then begin
      send ('of');
      send_type (param.elem);
   end;
end;

procedure Product.send_class_of_type (param : TClassOfType);
begin
   send ('class');
   send ('of');
   send_type (param.elem);
end;

procedure Product.send_proc_type (param : TProcType);
begin

   if (param.style = ProcedureStyle) then begin
      send ('procedure');
   end
   else if (param.style = FunctionStyle) then begin
      send ('function');
   end;
   send_formal_param_list (param.param_list);
   if (param.answer <> nil) then begin
      send (':');
      send_result_type (param.answer);
   end;
   if param.of_object then begin
      send ('of');
      send ('object');
   end;
   if (param.call_conv = RegisterCall) or (param.call_conv = PascalCall) or (param.call_conv = CdeclCall) or (param.call_conv = StdcallCall) or (param.call_conv = SafecallCall) then begin

      if (param.call_conv = RegisterCall) then begin
         send ('register');
      end
      else if (param.call_conv = PascalCall) then begin
         send ('pascal');
      end
      else if (param.call_conv = CdeclCall) then begin
         send ('cdecl');
      end
      else if (param.call_conv = StdcallCall) then begin
         send ('stdcall');
      end
      else if (param.call_conv = SafecallCall) then begin
         send ('safecall');
      end;
   end;
end;

procedure Product.send_range_type (param : TSubrangeType);
begin
   send_simple_expr (param.low);
   send ('..');
   send_simple_expr (param.high);
end;

procedure Product.send_alias_type (param : TAliasType);
begin
   send_qualified_name (param.alias_name);
end;

procedure Product.send_type (param : TType);
begin
   if (param is TStringType) then begin
      send_string_type (param.conv_TStringType);
   end
   else if (param is TArrayType) then begin
      send_array_type (param.conv_TArrayType);
   end
   else if (param is TSetType) then begin
      send_set_type (param.conv_TSetType);
   end
   else if (param is TFileType) then begin
      send_file_type (param.conv_TFileType);
   end
   else if (param is TRecordType) then begin
      send_record_type (param.conv_TRecordType);
   end
   else if (param is TClassType) then begin
      send_class_type (param.conv_TClassType);
   end
   else if (param is TClassOfType) then begin
      send_class_of_type (param.conv_TClassOfType);
   end
   else if (param is TInterfaceType) then begin
      send_interface_type (param.conv_TInterfaceType);
   end
   else if (param is TProcType) then begin
      send_proc_type (param.conv_TProcType);
   end
   else if (param is TPointerType) then begin
      send_pointer_type (param.conv_TPointerType);
   end
   else if (param is TSubrangeType) then begin
      send_range_type (param.conv_TSubrangeType);
   end
   else if (param is TEnumType) then begin
      send_enum_type (param.conv_TEnumType);
   end
   else if (param is TAliasType) then begin
      send_alias_type (param.conv_TAliasType);
   end;
end;

procedure Product.send_label_decl (param : TLabelDecl);
begin
   send_label_ident (param.name);
end;

procedure Product.send_label_sect (param : TLabelSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send ('label');
   send_label_decl (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_label_decl (param.items [inx]);
      inc (inx);
   end;
   send (';');
end;

procedure Product.send_const_decl (param : TConstDecl);
begin
   send (param.name);
   if (param.typ <> nil) then begin
      send (':');
      send_type (param.typ);
   end;
   send ('=');
   send_expr (param.val);
   send (';');
end;

procedure Product.send_const_sect (param : TConstSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send ('const');
   send_const_decl (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send_const_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_type_decl (param : TTypeDecl);
begin
   send (param.name);
   send ('=');
   send_type (param.typ);
   send (';');
end;

procedure Product.send_type_sect (param : TTypeSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send ('type');
   send_type_decl (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send_type_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_var_item (param : TVarItem);
begin
   send (param.name);
end;

procedure Product.send_var_decl (param : TVarDecl);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send_var_item (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      send (',');
      send_var_item (param.items [inx]);
      inc (inx);
   end;
   send (':');
   send_type (param.typ);
   if (param.ini <> nil) then begin
      send ('=');
      send_expr (param.ini);
   end;
   send (';');
end;

procedure Product.send_var_sect (param : TVarSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   send ('var');
   style_indent ();
   style_new_line ();
   send_var_decl (param.items [inx]);
   inc (inx);
   while (inx < cnt) do begin
      style_new_line ();
      send_var_decl (param.items [inx]);
      inc (inx);
   end;
   style_unindent ();
end;

procedure Product.send_proc_head (param : TProcDecl);
begin
   if param.a_static then begin
      send ('class');
   end;

   if (param.style = ProcedureStyle) then begin
      send ('procedure');
   end
   else if (param.style = FunctionStyle) then begin
      send ('function');
   end
   else if (param.style = ConstructorStyle) then begin
      send ('constructor');
   end
   else if (param.style = DestructorStyle) then begin
      send ('destructor');
   end;
   send_qualified_name (param.proc_name);
   send_formal_param_list (param.param_list);
   if (param.answer <> nil) then begin
      send (':');
      send_result_type (param.answer);
   end;
   send (';');
end;

procedure Product.send_proc_decl (param : TProcDecl);
begin
   send_proc_head (param);

   if param.a_forward then begin
      send ('forward');
   end
   else if param.external_spec then begin
      send_proc_external (param);
   end
   else if (param.local <> nil) then begin
      if param.a_inline then begin
         send ('inline');
         send (';');
      end;
      send_decl_part (param.local);
      style_new_line ();
      send ('begin');
      send_stat_list (param.body);
      send ('end');
   end;
   send (';');
   style_empty_line ();
end;

procedure Product.send_proc_external (param : TProcDecl);
begin
   send ('external');
   if (param.a_lib <> nil) then begin
      send_expr (param.a_lib);
   end;
   send (';');
   style_empty_line ();
end;

procedure Product.send_proc_intf_decl (param : TProcDecl);
begin
   send_proc_head (param);
   if param.a_inline then begin
      send ('inline');
      send (';');
   end;
   if param.external_spec then begin
      send_proc_external (param);
   end;
end;

procedure Product.send_intf_decl (param : TDeclSect);
begin
   if (param is TConstSect) then begin
      send_const_sect (param.conv_TConstSect);
   end
   else if (param is TTypeSect) then begin
      send_type_sect (param.conv_TTypeSect);
   end
   else if (param is TVarSect) then begin
      send_var_sect (param.conv_TVarSect);
   end
   else if (param is TProcDecl) then begin
      send_proc_intf_decl (param.conv_TProcDecl);
   end;
end;

procedure Product.send_intf_decl_part (param : TDeclGroup);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   while (inx < cnt) do begin
      style_new_line ();
      send_intf_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_decl (param : TDeclSect);
begin
   if (param is TLabelSect) then begin
      send_label_sect (param.conv_TLabelSect);
   end
   else if (param is TConstSect) then begin
      send_const_sect (param.conv_TConstSect);
   end
   else if (param is TTypeSect) then begin
      send_type_sect (param.conv_TTypeSect);
   end
   else if (param is TVarSect) then begin
      send_var_sect (param.conv_TVarSect);
   end
   else if (param is TProcDecl) then begin
      send_proc_decl (param.conv_TProcDecl);
   end;
end;

procedure Product.send_decl_part (param : TDeclGroup);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   while (inx < cnt) do begin
      style_new_line ();
      send_decl (param.items [inx]);
      inc (inx);
   end;
end;

procedure Product.send_import_item (param : TImportItem);
begin
   send (param.name);
   if (param.path <> '') then begin
      send ('in');
      putString (param.path);
   end;
end;

procedure Product.send_import_sect (param : TImportSect);
var inx, cnt: integer;
begin
   inx := 0;
   cnt := length (param.items);
   if (inx < cnt) then begin
      style_empty_line ();
      send ('uses');
      send_import_item (param.items [inx]);
      inc (inx);
      while (inx < cnt) do begin
         send (',');
         send_import_item (param.items [inx]);
         inc (inx);
      end;
      send (';');
      style_empty_line ();
   end;
end;

procedure Product.send_unit_decl (param : TUnitModule);
begin
   send ('unit');
   send (param.name);
   send (';');
   style_empty_line ();
   send ('interface');
   style_empty_line ();
   send_import_sect (param.intf_imports);
   send_intf_decl_part (param.intf_decl);
   style_empty_line ();
   send ('implementation');
   style_empty_line ();
   send_import_sect (param.impl_imports);
   send_decl_part (param.impl_decl);
   if param.no_begin or (param.init <> nil) then begin

      if param.no_begin then begin
         if (param.init <> nil) then begin
            send ('initialization');
            send_stat_list (param.init);
         end;
         if (param.finish <> nil) then begin
            send ('finalization');
            send_stat_list (param.finish);
         end;
      end
      else if (param.init <> nil) then begin
         send ('begin');
         send_stat_list (param.init);
      end;
   end;
   send ('end');
   style_no_space ();
   send ('.');
end;

procedure Product.send_program_decl (param : TProgramModule);
begin
   send ('program');
   send (param.name);
   send (';');
   style_empty_line ();
   send_import_sect (param.impl_imports);
   send_decl_part (param.impl_decl);
   style_new_line ();
   send ('begin');
   send_stat_list (param.init);
   send ('end');
   style_no_space ();
   send ('.');
end;

procedure Product.send_library_decl (param : TLibraryModule);
begin
   send ('library');
   send (param.name);
   send (';');
   style_empty_line ();
   send_import_sect (param.impl_imports);
   send_decl_part (param.impl_decl);
   style_new_line ();
   send ('begin');
   send_stat_list (param.init);
   send ('end');
   style_no_space ();
   send ('.');
end;

procedure Product.send_module_decl (param : TModule);
begin
   if (param is TUnitModule) then begin
      send_unit_decl (param.conv_TUnitModule);
   end
   else if (param is TProgramModule) then begin
      send_program_decl (param.conv_TProgramModule);
   end
   else if (param is TLibraryModule) then begin
      send_library_decl (param.conv_TLibraryModule);
   end;
end;

end.
