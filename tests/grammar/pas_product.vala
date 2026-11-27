public class Product : Output
{

   public void send_label_ident (TLabelIdent param)
   {
         send (param.id);
   }

   public void send_qualified_name (TQualName param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send (param.id);
         while (inx < cnt)
         {
            send_cont_name (param.items[inx]);
            inx++;
         }
   }

   public void send_cont_name (TContName param)
   {
         style_no_space ();
         send (".");
         style_no_space ();
         send (param.id);
   }

   public void send_ifc_type (TType param)
   {
         send_simple_alias_type (param.conv_TAliasType ());
   }

   public void send_param_type (TType param)
   {
         if (param.conv_TAliasType () != null)
         {
            TAliasType param0 = param.conv_TAliasType ();
            send_simple_alias_type (param0.conv_TAliasType ());
         }
         else if (param.conv_TStringType () != null)
         {
            TStringType param0 = param.conv_TStringType ();
            send_simple_string_type (param0.conv_TStringType ());
         }
         else if (param.conv_TFileType () != null)
         {
            TFileType param0 = param.conv_TFileType ();
            send_simple_file_type (param0.conv_TFileType ());
         }
   }

   public void send_result_type (TType param)
   {
         if (param.conv_TAliasType () != null)
         {
            TAliasType param0 = param.conv_TAliasType ();
            send_simple_alias_type (param0.conv_TAliasType ());
         }
         else if (param.conv_TStringType () != null)
         {
            TStringType param0 = param.conv_TStringType ();
            send_simple_string_type (param0.conv_TStringType ());
         }
   }

   public void send_simple_alias_type (TAliasType param)
   {
         send_qualified_name (param.alias_name);
   }

   public void send_simple_string_type (TStringType param)
   {
         send ("string");
   }

   public void send_simple_file_type (TFileType param)
   {
         send ("file");
   }

   public void send_index_expr_item (TInxItem param)
   {
         send_expr (param.ref);
   }

   public void send_index_expr_list (TInxList param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_index_expr_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_index_expr_item (param.items[inx]);
            inx++;
         }
   }

   public void send_arg_item (TArgItem param)
   {
         send_expr (param.value);
         if (param.width != null)
         {
            send (":");
            send_expr (param.width);
            if (param.digits != null)
            {
               send (":");
               send_expr (param.digits);
            }
         }
   }

   public void send_arg_list (TArgSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_arg_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_arg_item (param.items[inx]);
            inx++;
         }
   }

   public void send_elem_sect (TElemSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_elem_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_elem_item (param.items[inx]);
            inx++;
         }
   }

   public void send_elem_item (TElemItem param)
   {
         send_expr (param.low);
         if (param.high != null)
         {
            send ("..");
            send_expr (param.high);
         }
   }

   public void send_struct_item (TStructSect param)
   {
         if (param.name != "")
         {
            send (param.name);
            send (":");
         }
         send_expr (param.value);
   }

   public void send_struct_sect (TStructSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_struct_item (param.items[inx]);
         inx++;
         if (inx < cnt || inx < cnt)
         {
            if (inx < cnt)
            {
               send (",");
               send_struct_item (param.items[inx]);
               inx++;
               while (inx < cnt)
               {
                  send (",");
                  send_struct_item (param.items[inx]);
                  inx++;
               }
            }
            else if (inx < cnt)
            {
               send (";");
               send_struct_item (param.items[inx]);
               inx++;
               while (inx < cnt)
               {
                  send (";");
                  send_struct_item (param.items[inx]);
                  inx++;
               }
            }
         }
   }

   public void send_ident_expr (TIdentExpr param)
   {
         send (param.name);
   }

   public void send_int_value_expr (TIntValueExpr param)
   {
         send (param.value);
   }

   public void send_float_value_expr (TFltValueExpr param)
   {
         send (param.value);
   }

   public void send_string_value_expr (TStrValueExpr param)
   {
         putString (param.value);
   }

   public void send_nil_expr (TNilExpr param)
   {
         send ("nil");
   }

   public void send_sub_expr (TStructExpr param)
   {
         send ("(");
         send_expr (param.value);
         send (")");
   }

   public void send_not_expr (TNotExpr param)
   {
         send ("not");
         send_factor (param.param);
   }

   public void send_plus_expr (TPlusExpr param)
   {
         send ("+");
         send_factor (param.param);
   }

   public void send_minus_expr (TMinusExpr param)
   {
         send ("-");
         send_factor (param.param);
   }

   public void send_adr_expr (TAdrExpr param)
   {
         send ("@");
         send_factor (param.param);
   }

   public void send_set_expr (TSetExpr param)
   {
         send ("[");
         send_elem_sect (param.list);
         send ("]");
   }

   public void send_super_expr (TSuperExpr param)
   {
         send ("inherited");
         send (param.name);
   }

   public void send_string_type_expr (TStringExpr param)
   {
         send ("string");
         send ("(");
         send_expr (param.param);
         send (")");
   }

   public void send_variable (TExpr param)
   {
         if (param.conv_TIdentExpr () != null)
         {
            TIdentExpr param0 = param.conv_TIdentExpr ();
            send_ident_expr (param0.conv_TIdentExpr ());
         }
         else if (param.conv_TStructExpr () != null)
         {
            TStructExpr param0 = param.conv_TStructExpr ();
            send_sub_expr (param0.conv_TStructExpr ());
         }
         else if (param.conv_TSuperExpr () != null)
         {
            TSuperExpr param0 = param.conv_TSuperExpr ();
            send_super_expr (param0.conv_TSuperExpr ());
         }
   }

   public void send_reference (TExpr param)
   {
         if (param.conv_TIndexExpr () != null)
         {
            TIndexExpr param0 = param.conv_TIndexExpr ();
            send_variable (param0.left);
            send_index_expr (param0.conv_TIndexExpr ());
         }
         else if (param.conv_TCallExpr () != null)
         {
            TCallExpr param0 = param.conv_TCallExpr ();
            send_variable (param0.func);
            send_call_expr (param0.conv_TCallExpr ());
         }
         else if (param.conv_TDerefExpr () != null)
         {
            TDerefExpr param0 = param.conv_TDerefExpr ();
            send_variable (param0.param);
            send_deref_expr (param0.conv_TDerefExpr ());
         }
         else if (param.conv_TFieldExpr () != null)
         {
            TFieldExpr param0 = param.conv_TFieldExpr ();
            send_variable (param0.param);
            send_field_expr (param0.conv_TFieldExpr ());
         }
         else {
            send_variable (param);
         }
   }

   public void send_index_expr (TIndexExpr param)
   {
         send ("[");
         send_index_expr_list (param.list);
         send ("]");
   }

   public void send_call_expr (TCallExpr param)
   {
         send ("(");
         send_arg_list (param.list);
         send (")");
   }

   public void send_deref_expr (TDerefExpr param)
   {
         send ("^");
   }

   public void send_field_expr (TFieldExpr param)
   {
         style_no_space ();
         send (".");
         style_no_space ();
         send (param.name);
   }

   public void send_factor (TExpr param)
   {
         if (param.conv_TIntValueExpr () != null)
         {
            TIntValueExpr param0 = param.conv_TIntValueExpr ();
            send_int_value_expr (param0.conv_TIntValueExpr ());
         }
         else if (param.conv_TFltValueExpr () != null)
         {
            TFltValueExpr param0 = param.conv_TFltValueExpr ();
            send_float_value_expr (param0.conv_TFltValueExpr ());
         }
         else if (param.conv_TStrValueExpr () != null)
         {
            TStrValueExpr param0 = param.conv_TStrValueExpr ();
            send_string_value_expr (param0.conv_TStrValueExpr ());
         }
         else if (param.conv_TNotExpr () != null)
         {
            TNotExpr param0 = param.conv_TNotExpr ();
            send_not_expr (param0.conv_TNotExpr ());
         }
         else if (param.conv_TPlusExpr () != null)
         {
            TPlusExpr param0 = param.conv_TPlusExpr ();
            send_plus_expr (param0.conv_TPlusExpr ());
         }
         else if (param.conv_TMinusExpr () != null)
         {
            TMinusExpr param0 = param.conv_TMinusExpr ();
            send_minus_expr (param0.conv_TMinusExpr ());
         }
         else if (param.conv_TAdrExpr () != null)
         {
            TAdrExpr param0 = param.conv_TAdrExpr ();
            send_adr_expr (param0.conv_TAdrExpr ());
         }
         else if (param.conv_TNilExpr () != null)
         {
            TNilExpr param0 = param.conv_TNilExpr ();
            send_nil_expr (param0.conv_TNilExpr ());
         }
         else if (param.conv_TSetExpr () != null)
         {
            TSetExpr param0 = param.conv_TSetExpr ();
            send_set_expr (param0.conv_TSetExpr ());
         }
         else if (param.conv_TStringExpr () != null)
         {
            TStringExpr param0 = param.conv_TStringExpr ();
            send_string_type_expr (param0.conv_TStringExpr ());
         }
         else if (param.conv_TExpr () != null)
         {
            TExpr param0 = param.conv_TExpr ();
            send_reference (param0);
         }
   }

   public void send_term (TExpr param)
   {
         if (param.fce == MulExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("*");
            send_factor (param0.right);
         }
         else if (param.fce == RDivExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("/");
            send_factor (param0.right);
         }
         else if (param.fce == DivExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("div");
            send_factor (param0.right);
         }
         else if (param.fce == ModExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("mod");
            send_factor (param0.right);
         }
         else if (param.fce == ShlExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("shl");
            send_factor (param0.right);
         }
         else if (param.fce == ShrExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("shr");
            send_factor (param0.right);
         }
         else if (param.fce == AndExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("and");
            send_factor (param0.right);
         }
         else if (param.fce == AsExp)
         {
            TTermExpr param0 = param.conv_TTermExpr ();
            send_factor (param0.left);
            send ("as");
            send_factor (param0.right);
         }
         else {
            send_factor (param);
         }
   }

   public void send_simple_expr (TExpr param)
   {
         if (param.fce == AddExp)
         {
            TSimpleExpr param0 = param.conv_TSimpleExpr ();
            send_term (param0.left);
            send ("+");
            send_term (param0.right);
         }
         else if (param.fce == SubExp)
         {
            TSimpleExpr param0 = param.conv_TSimpleExpr ();
            send_term (param0.left);
            send ("-");
            send_term (param0.right);
         }
         else if (param.fce == OrExp)
         {
            TSimpleExpr param0 = param.conv_TSimpleExpr ();
            send_term (param0.left);
            send ("or");
            send_term (param0.right);
         }
         else if (param.fce == XorExp)
         {
            TSimpleExpr param0 = param.conv_TSimpleExpr ();
            send_term (param0.left);
            send ("xor");
            send_term (param0.right);
         }
         else {
            send_term (param);
         }
   }

   public void send_expr (TExpr param)
   {
         if (param.fce == EqExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("=");
            send_simple_expr (param0.right);
         }
         else if (param.fce == NeExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("<>");
            send_simple_expr (param0.right);
         }
         else if (param.fce == LtExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("<");
            send_simple_expr (param0.right);
         }
         else if (param.fce == GtExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send (">");
            send_simple_expr (param0.right);
         }
         else if (param.fce == LeExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("<=");
            send_simple_expr (param0.right);
         }
         else if (param.fce == GeExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send (">=");
            send_simple_expr (param0.right);
         }
         else if (param.fce == InExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("in");
            send_simple_expr (param0.right);
         }
         else if (param.fce == IsExp)
         {
            TCompleteExpr param0 = param.conv_TCompleteExpr ();
            send_simple_expr (param0.left);
            send ("is");
            send_simple_expr (param0.right);
         }
         else {
            send_simple_expr (param);
         }
   }

   public void send_goto_stat (TGotoStat param)
   {
         send ("goto");
         send_label_ident (param.goto_lab);
   }

   public void send_begin_stat (TBlockStat param)
   {
         send ("begin");
         send_stat_list (param.body_seq);
         send ("end");
   }

   public void send_stat_list (TStatSeq param)
   {
         int inx = 0;
         int cnt = param.items.length;
         style_new_line ();
         style_indent ();
         send_stat (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (";");
            style_new_line ();
            send_stat (param.items[inx]);
            inx++;
         }
         style_unindent ();
         style_new_line ();
   }

   public void send_inner_stat (TStat param)
   {
         style_new_line ();
         style_indent ();
         send_stat (param);
         style_unindent ();
   }

   public void send_if_stat (TIfStat param)
   {
         send ("if");
         send_expr (param.cond_expr);
         send ("then");
         send_inner_stat (param.then_stat);
         if (param.else_stat != null)
         {
            send ("else");
            send_inner_stat (param.else_stat);
         }
   }

   public void send_case_stat (TCaseStat param)
   {
         send ("case");
         send_expr (param.case_expr);
         send ("of");
         send_case_sect (param.case_list);
         if (param.else_seq != null)
         {
            send ("else");
            send_stat_list (param.else_seq);
         }
         send ("end");
   }

   public void send_case_sect (TCaseSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_case_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (";");
            style_new_line ();
            send_case_item (param.items[inx]);
            inx++;
         }
   }

   public void send_case_item (TCaseItem param)
   {
         send_elem_sect (param.sel_list);
         send (":");
         send_inner_stat (param.sel_stat);
   }

   public void send_while_stat (TWhileStat param)
   {
         send ("while");
         send_expr (param.cond_expr);
         send ("do");
         send_inner_stat (param.body_stat);
   }

   public void send_repeat_stat (TRepeatStat param)
   {
         send ("repeat");
         send_stat_list (param.body_seq);
         send ("until");
         send_expr (param.until_expr);
   }

   public void send_for_stat (TForStat param)
   {
         send ("for");
         send_variable (param.var_expr);
         send (":=");
         send_expr (param.from_expr);
         if (param.incr)
         {
            send ("to");
         }
         else if (! param.incr)
         {
            send ("downto");
         }
         send_expr (param.to_expr);
         send ("do");
         send_inner_stat (param.body_stat);
   }

   public void send_with_stat (TWithStat param)
   {
         send ("with");
         send_with_sect (param.with_list);
         send ("do");
         send_inner_stat (param.body_stat);
   }

   public void send_with_sect (TWithSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_with_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_with_item (param.items[inx]);
            inx++;
         }
   }

   public void send_with_item (TWithItem param)
   {
         send_variable (param.expr);
   }

   public void send_raise_stat (TRaiseStat param)
   {
         send ("raise");
         if (param.raise_expr != null)
         {
            send_expr (param.raise_expr);
         }
   }

   public void send_try_stat (TTryStat param)
   {
         send ("try");
         send_stat_list (param.body_seq);
         if (param.finally_branch != null)
         {
            send_finally_part (param.finally_branch);
         }
         else if (param.except_branch != null)
         {
            send_except_part (param.except_branch);
         }
         send ("end");
   }

   public void send_finally_part (TFinallyPart param)
   {
         send ("finally");
         send_stat_list (param.finally_seq);
   }

   public void send_except_part (TExceptPart param)
   {
         send ("except");
         if (param.on_list != null)
         {
            send_on_sect (param.on_list);
            if (param.else_seq != null)
            {
               send ("else");
               send_stat_list (param.else_seq);
            }
         }
         else if (param.else_seq != null)
         {
            send_stat_list (param.else_seq);
         }
   }

   public void send_on_sect (TOnSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_on_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (";");
            send_on_item (param.items[inx]);
            inx++;
         }
         if (param.semicolon)
         {
            send (";");
         }
   }

   public void send_on_item (TOnItem param)
   {
         send ("on");
         if (param.on_ident != "")
         {
            send (param.on_ident);
            send (":");
         }
         send_type (param.on_type);
         send ("do");
         send_inner_stat (param.body_stat);
   }

   public void send_empty_stat (TEmptyStat param)
   {
   }

   public void send_simple_stat (TStat param)
   {
         if (param.conv_TAssignStat () != null)
         {
            TAssignStat param0 = param.conv_TAssignStat ();
            send_expr (param0.left_expr);
            send_assign_stat (param0.conv_TAssignStat ());
         }
         else if (param.conv_TCallStat () != null)
         {
            TCallStat param0 = param.conv_TCallStat ();
            send_expr (param0.call_expr);
            send_call_stat (param0.conv_TCallStat ());
         }
   }

   public void send_assign_stat (TAssignStat param)
   {
         send (":=");
         send_expr (param.right_expr);
   }

   public void send_call_stat (TCallStat param)
   {
   }

   public void send_labeled_stat (TLabeledTStat param)
   {
         send_label_ident (param.lab);
         send (":");
         send_stat (param.body);
   }

   public void send_stat (TStat param)
   {
         if (param.conv_TLabeledTStat () != null)
         {
            TLabeledTStat param0 = param.conv_TLabeledTStat ();
            send_labeled_stat (param0.conv_TLabeledTStat ());
         }
         else if (param.conv_TStat () != null)
         {
            TStat param0 = param.conv_TStat ();
            send_simple_stat (param0);
         }
         else if (param.conv_TEmptyStat () != null)
         {
            TEmptyStat param0 = param.conv_TEmptyStat ();
            send_empty_stat (param0.conv_TEmptyStat ());
         }
         else if (param.conv_TGotoStat () != null)
         {
            TGotoStat param0 = param.conv_TGotoStat ();
            send_goto_stat (param0.conv_TGotoStat ());
         }
         else if (param.conv_TBlockStat () != null)
         {
            TBlockStat param0 = param.conv_TBlockStat ();
            send_begin_stat (param0.conv_TBlockStat ());
         }
         else if (param.conv_TIfStat () != null)
         {
            TIfStat param0 = param.conv_TIfStat ();
            send_if_stat (param0.conv_TIfStat ());
         }
         else if (param.conv_TCaseStat () != null)
         {
            TCaseStat param0 = param.conv_TCaseStat ();
            send_case_stat (param0.conv_TCaseStat ());
         }
         else if (param.conv_TWhileStat () != null)
         {
            TWhileStat param0 = param.conv_TWhileStat ();
            send_while_stat (param0.conv_TWhileStat ());
         }
         else if (param.conv_TRepeatStat () != null)
         {
            TRepeatStat param0 = param.conv_TRepeatStat ();
            send_repeat_stat (param0.conv_TRepeatStat ());
         }
         else if (param.conv_TForStat () != null)
         {
            TForStat param0 = param.conv_TForStat ();
            send_for_stat (param0.conv_TForStat ());
         }
         else if (param.conv_TWithStat () != null)
         {
            TWithStat param0 = param.conv_TWithStat ();
            send_with_stat (param0.conv_TWithStat ());
         }
         else if (param.conv_TRaiseStat () != null)
         {
            TRaiseStat param0 = param.conv_TRaiseStat ();
            send_raise_stat (param0.conv_TRaiseStat ());
         }
         else if (param.conv_TTryStat () != null)
         {
            TTryStat param0 = param.conv_TTryStat ();
            send_try_stat (param0.conv_TTryStat ());
         }
   }

   public void send_param_ident (TParamIdent param)
   {
         send (param.name);
   }

   public void send_param_item (TParamItem param)
   {
         int inx = 0;
         int cnt = param.items.length;
         if (param.mode == VarParam)
         {
            send ("var");
         }
         else if (param.mode == ConstParam)
         {
            send ("const");
         }
         else if (param.mode == OutParam)
         {
            send ("out");
         }
         else if (param.mode == ValueParam)
         {
         }
         send_param_ident (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_param_ident (param.items[inx]);
            inx++;
         }
         if (param.typ != null)
         {
            send (":");
            send_param_type (param.typ);
            if (param.ini != null)
            {
               send ("=");
               send_expr (param.ini);
            }
         }
   }

   public void send_formal_param_list (TParamSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         if (inx < cnt)
         {
            send ("(");
            send_param_item (param.items[inx]);
            inx++;
            while (inx < cnt)
            {
               send (";");
               send_param_item (param.items[inx]);
               inx++;
            }
            send (")");
         }
   }

   public void send_property_param_list (TParamSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send ("[");
         send_param_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (";");
            send_param_item (param.items[inx]);
            inx++;
         }
         send ("]");
   }

   public void send_class_type (TClassType param)
   {
         send ("class");
         if (param.parent != null)
         {
            send ("(");
            send_ifc_type (param.parent);
            if (param.ifc_list != null)
            {
               send (",");
               send_interface_sect (param.ifc_list);
            }
            send (")");
         }
         style_indent ();
         send_components_sect (param.components);
         style_unindent ();
         send ("end");
   }

   public void send_interface_type (TInterfaceType param)
   {
         send ("interface");
         if (param.ifc_list != null)
         {
            send ("(");
            send_interface_sect (param.ifc_list);
            send (")");
         }
         style_indent ();
         send_components_sect (param.components);
         style_unindent ();
         send ("end");
   }

   public void send_interface_sect (TInterfaceSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_interface_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_interface_item (param.items[inx]);
            inx++;
         }
   }

   public void send_interface_item (TIntefaceItem param)
   {
         send_ifc_type (param.ifc);
   }

   public void send_components_sect (TComponetsSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_components_first_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send_components_item (param.items[inx]);
            inx++;
         }
   }

   public void send_components_item (TComponentsItem param)
   {
         if (param.acs == PrivateAccess)
         {
            send ("private");
         }
         else if (param.acs == ProtectedAccess)
         {
            send ("protected");
         }
         else if (param.acs == PublicAccess)
         {
            send ("public");
         }
         else if (param.acs == PublishedAccess)
         {
            send ("published");
         }
         else if (param.acs == AutomatedAccess)
         {
            send ("automated");
         }
         send_member_sect (param.members);
   }

   public void send_components_first_item (TComponentsItem param)
   {
         send_member_sect (param.members);
   }

   public void send_member_sect (TDeclGroup param)
   {
         int inx = 0;
         int cnt = param.items.length;
         while (inx < cnt)
         {
            style_new_line ();
            send_member_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_member_decl (TDeclSect param)
   {
         if (param.conv_TFieldDecl () != null)
         {
            TFieldDecl param0 = param.conv_TFieldDecl ();
            send_field_decl (param0.conv_TFieldDecl ());
         }
         else if (param.conv_TProcDecl () != null)
         {
            TProcDecl param0 = param.conv_TProcDecl ();
            send_method_decl (param0.conv_TProcDecl ());
         }
         else if (param.conv_TPropertyDecl () != null)
         {
            TPropertyDecl param0 = param.conv_TPropertyDecl ();
            send_property_decl (param0.conv_TPropertyDecl ());
         }
   }

   public void send_field_ident (TFieldItem param)
   {
         send (param.name);
   }

   public void send_field_decl (TFieldDecl param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_field_ident (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_field_ident (param.items[inx]);
            inx++;
         }
         send (":");
         send_type (param.typ);
         send (";");
   }

   public void send_method_decl (TProcDecl param)
   {
         send_proc_head (param);
         if (param.a_virtual || param.a_dynamic || param.a_override || param.a_abstract)
         {
            if (param.a_virtual)
            {
               send ("virtual");
               send (";");
            }
            else if (param.a_dynamic)
            {
               send ("dynamic");
               send (";");
            }
            else if (param.a_override)
            {
               send ("override");
               send (";");
            }
            else if (param.a_abstract)
            {
               send ("abstract");
               send (";");
            }
         }
   }

   public void send_property_decl (TPropertyDecl param)
   {
         send ("property");
         send (param.name);
         if (param.param_list != null)
         {
            send_property_param_list (param.param_list);
         }
         if (param.typ != null)
         {
            send (":");
            send_result_type (param.typ);
         }
         if (param.a_read != null)
         {
            send ("read");
            send_expr (param.a_read);
         }
         if (param.a_write != null)
         {
            send ("write");
            send_expr (param.a_write);
         }
         if (param.a_stored)
         {
            send ("stored");
         }
         if (param.a_default)
         {
            send ("default");
         }
         if (param.a_nodefault)
         {
            send ("nodefault");
         }
         if (param.a_implements != null)
         {
            send ("implements");
            send_interface_sect (param.a_implements);
         }
         if (param.a_def_array)
         {
            send (";");
            send ("default");
         }
         send (";");
   }

   public void send_enum_type (TEnumType param)
   {
         send ("(");
         send_enum_sect (param.elements);
         send (")");
   }

   public void send_enum_sect (TEnumSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_enum_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_enum_item (param.items[inx]);
            inx++;
         }
   }

   public void send_enum_item (TEnumItem param)
   {
         send (param.name);
   }

   public void send_string_type (TStringType param)
   {
         send ("string");
         if (param.lim != null)
         {
            send ("[");
            send_expr (param.lim);
            send ("]");
         }
   }

   public void send_array_type (TArrayType param)
   {
         send ("array");
         if (param.index_list != null)
         {
            send ("[");
            send_index_type_sect (param.index_list);
            send ("]");
         }
         send ("of");
         send_type (param.elem);
   }

   public void send_index_type_sect (TIndexTypeSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_index_type_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_index_type_item (param.items[inx]);
            inx++;
         }
   }

   public void send_index_type_item (TIndexTypeItem param)
   {
         send_type (param.index);
   }

   public void send_record_type (TRecordType param)
   {
         if (param.a_packed)
         {
            send ("packed");
         }
         send ("record");
         send_field_sect (param.fields);
         send ("end");
   }

   public void send_field_sect (TFieldDeclGroup param)
   {
         int inx = 0;
         int cnt = param.items.length;
         while (inx < cnt)
         {
            send_field_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_pointer_type (TPointerType param)
   {
         send ("^");
         send_type (param.elem);
   }

   public void send_set_type (TSetType param)
   {
         send ("set");
         send ("of");
         send_type (param.elem);
   }

   public void send_file_type (TFileType param)
   {
         send ("file");
         if (param.elem != null)
         {
            send ("of");
            send_type (param.elem);
         }
   }

   public void send_class_of_type (TClassOfType param)
   {
         send ("class");
         send ("of");
         send_type (param.elem);
   }

   public void send_proc_type (TProcType param)
   {
         if (param.style == ProcedureStyle)
         {
            send ("procedure");
         }
         else if (param.style == FunctionStyle)
         {
            send ("function");
         }
         send_formal_param_list (param.param_list);
         if (param.answer != null)
         {
            send (":");
            send_result_type (param.answer);
         }
         if (param.of_object)
         {
            send ("of");
            send ("object");
         }
         if (param.call_conv == RegisterCall || param.call_conv == PascalCall || param.call_conv == CdeclCall || param.call_conv == StdcallCall || param.call_conv == SafecallCall)
         {
            if (param.call_conv == RegisterCall)
            {
               send ("register");
            }
            else if (param.call_conv == PascalCall)
            {
               send ("pascal");
            }
            else if (param.call_conv == CdeclCall)
            {
               send ("cdecl");
            }
            else if (param.call_conv == StdcallCall)
            {
               send ("stdcall");
            }
            else if (param.call_conv == SafecallCall)
            {
               send ("safecall");
            }
         }
   }

   public void send_range_type (TSubrangeType param)
   {
         send_simple_expr (param.low);
         send ("..");
         send_simple_expr (param.high);
   }

   public void send_alias_type (TAliasType param)
   {
         send_qualified_name (param.alias_name);
   }

   public void send_type (TType param)
   {
         if (param.conv_TStringType () != null)
         {
            TStringType param0 = param.conv_TStringType ();
            send_string_type (param0.conv_TStringType ());
         }
         else if (param.conv_TArrayType () != null)
         {
            TArrayType param0 = param.conv_TArrayType ();
            send_array_type (param0.conv_TArrayType ());
         }
         else if (param.conv_TSetType () != null)
         {
            TSetType param0 = param.conv_TSetType ();
            send_set_type (param0.conv_TSetType ());
         }
         else if (param.conv_TFileType () != null)
         {
            TFileType param0 = param.conv_TFileType ();
            send_file_type (param0.conv_TFileType ());
         }
         else if (param.conv_TRecordType () != null)
         {
            TRecordType param0 = param.conv_TRecordType ();
            send_record_type (param0.conv_TRecordType ());
         }
         else if (param.conv_TClassType () != null)
         {
            TClassType param0 = param.conv_TClassType ();
            send_class_type (param0.conv_TClassType ());
         }
         else if (param.conv_TClassOfType () != null)
         {
            TClassOfType param0 = param.conv_TClassOfType ();
            send_class_of_type (param0.conv_TClassOfType ());
         }
         else if (param.conv_TInterfaceType () != null)
         {
            TInterfaceType param0 = param.conv_TInterfaceType ();
            send_interface_type (param0.conv_TInterfaceType ());
         }
         else if (param.conv_TProcType () != null)
         {
            TProcType param0 = param.conv_TProcType ();
            send_proc_type (param0.conv_TProcType ());
         }
         else if (param.conv_TPointerType () != null)
         {
            TPointerType param0 = param.conv_TPointerType ();
            send_pointer_type (param0.conv_TPointerType ());
         }
         else if (param.conv_TSubrangeType () != null)
         {
            TSubrangeType param0 = param.conv_TSubrangeType ();
            send_range_type (param0.conv_TSubrangeType ());
         }
         else if (param.conv_TEnumType () != null)
         {
            TEnumType param0 = param.conv_TEnumType ();
            send_enum_type (param0.conv_TEnumType ());
         }
         else if (param.conv_TAliasType () != null)
         {
            TAliasType param0 = param.conv_TAliasType ();
            send_alias_type (param0.conv_TAliasType ());
         }
   }

   public void send_label_decl (TLabelDecl param)
   {
         send_label_ident (param.name);
   }

   public void send_label_sect (TLabelSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send ("label");
         send_label_decl (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_label_decl (param.items[inx]);
            inx++;
         }
         send (";");
   }

   public void send_const_decl (TConstDecl param)
   {
         send (param.name);
         if (param.typ != null)
         {
            send (":");
            send_type (param.typ);
         }
         send ("=");
         send_expr (param.val);
         send (";");
   }

   public void send_const_sect (TConstSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send ("const");
         send_const_decl (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send_const_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_type_decl (TTypeDecl param)
   {
         send (param.name);
         send ("=");
         send_type (param.typ);
         send (";");
   }

   public void send_type_sect (TTypeSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send ("type");
         send_type_decl (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send_type_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_var_item (TVarItem param)
   {
         send (param.name);
   }

   public void send_var_decl (TVarDecl param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send_var_item (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            send (",");
            send_var_item (param.items[inx]);
            inx++;
         }
         send (":");
         send_type (param.typ);
         if (param.ini != null)
         {
            send ("=");
            send_expr (param.ini);
         }
         send (";");
   }

   public void send_var_sect (TVarSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         send ("var");
         style_indent ();
         style_new_line ();
         send_var_decl (param.items[inx]);
         inx++;
         while (inx < cnt)
         {
            style_new_line ();
            send_var_decl (param.items[inx]);
            inx++;
         }
         style_unindent ();
   }

   public void send_proc_head (TProcDecl param)
   {
         if (param.a_static)
         {
            send ("class");
         }
         if (param.style == ProcedureStyle)
         {
            send ("procedure");
         }
         else if (param.style == FunctionStyle)
         {
            send ("function");
         }
         else if (param.style == ConstructorStyle)
         {
            send ("constructor");
         }
         else if (param.style == DestructorStyle)
         {
            send ("destructor");
         }
         send_qualified_name (param.proc_name);
         send_formal_param_list (param.param_list);
         if (param.answer != null)
         {
            send (":");
            send_result_type (param.answer);
         }
         send (";");
   }

   public void send_proc_decl (TProcDecl param)
   {
         send_proc_head (param);
         if (param.a_forward)
         {
            send ("forward");
         }
         else if (param.external_spec)
         {
            send_proc_external (param);
         }
         else if (param.local != null)
         {
            if (param.a_inline)
            {
               send ("inline");
               send (";");
            }
            send_decl_part (param.local);
            style_new_line ();
            send ("begin");
            send_stat_list (param.body);
            send ("end");
         }
         send (";");
         style_empty_line ();
   }

   public void send_proc_external (TProcDecl param)
   {
         send ("external");
         if (param.a_lib != null)
         {
            send_expr (param.a_lib);
         }
         send (";");
         style_empty_line ();
   }

   public void send_proc_intf_decl (TProcDecl param)
   {
         send_proc_head (param);
         if (param.a_inline)
         {
            send ("inline");
            send (";");
         }
         if (param.external_spec)
         {
            send_proc_external (param);
         }
   }

   public void send_intf_decl (TDeclSect param)
   {
         if (param.conv_TConstSect () != null)
         {
            TConstSect param0 = param.conv_TConstSect ();
            send_const_sect (param0.conv_TConstSect ());
         }
         else if (param.conv_TTypeSect () != null)
         {
            TTypeSect param0 = param.conv_TTypeSect ();
            send_type_sect (param0.conv_TTypeSect ());
         }
         else if (param.conv_TVarSect () != null)
         {
            TVarSect param0 = param.conv_TVarSect ();
            send_var_sect (param0.conv_TVarSect ());
         }
         else if (param.conv_TProcDecl () != null)
         {
            TProcDecl param0 = param.conv_TProcDecl ();
            send_proc_intf_decl (param0.conv_TProcDecl ());
         }
   }

   public void send_intf_decl_part (TDeclGroup param)
   {
         int inx = 0;
         int cnt = param.items.length;
         while (inx < cnt)
         {
            style_new_line ();
            send_intf_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_decl (TDeclSect param)
   {
         if (param.conv_TLabelSect () != null)
         {
            TLabelSect param0 = param.conv_TLabelSect ();
            send_label_sect (param0.conv_TLabelSect ());
         }
         else if (param.conv_TConstSect () != null)
         {
            TConstSect param0 = param.conv_TConstSect ();
            send_const_sect (param0.conv_TConstSect ());
         }
         else if (param.conv_TTypeSect () != null)
         {
            TTypeSect param0 = param.conv_TTypeSect ();
            send_type_sect (param0.conv_TTypeSect ());
         }
         else if (param.conv_TVarSect () != null)
         {
            TVarSect param0 = param.conv_TVarSect ();
            send_var_sect (param0.conv_TVarSect ());
         }
         else if (param.conv_TProcDecl () != null)
         {
            TProcDecl param0 = param.conv_TProcDecl ();
            send_proc_decl (param0.conv_TProcDecl ());
         }
   }

   public void send_decl_part (TDeclGroup param)
   {
         int inx = 0;
         int cnt = param.items.length;
         while (inx < cnt)
         {
            style_new_line ();
            send_decl (param.items[inx]);
            inx++;
         }
   }

   public void send_import_item (TImportItem param)
   {
         send (param.name);
         if (param.path != "")
         {
            send ("in");
            putString (param.path);
         }
   }

   public void send_import_sect (TImportSect param)
   {
         int inx = 0;
         int cnt = param.items.length;
         if (inx < cnt)
         {
            style_empty_line ();
            send ("uses");
            send_import_item (param.items[inx]);
            inx++;
            while (inx < cnt)
            {
               send (",");
               send_import_item (param.items[inx]);
               inx++;
            }
            send (";");
            style_empty_line ();
         }
   }

   public void send_unit_decl (TUnitModule param)
   {
         send ("unit");
         send (param.name);
         send (";");
         style_empty_line ();
         send ("interface");
         style_empty_line ();
         send_import_sect (param.intf_imports);
         send_intf_decl_part (param.intf_decl);
         style_empty_line ();
         send ("implementation");
         style_empty_line ();
         send_import_sect (param.impl_imports);
         send_decl_part (param.impl_decl);
         if (param.no_begin || param.init != null)
         {
            if (param.no_begin)
            {
               if (param.init != null)
               {
                  send ("initialization");
                  send_stat_list (param.init);
               }
               if (param.finish != null)
               {
                  send ("finalization");
                  send_stat_list (param.finish);
               }
            }
            else if (param.init != null)
            {
               send ("begin");
               send_stat_list (param.init);
            }
         }
         send ("end");
         style_no_space ();
         send (".");
   }

   public void send_program_decl (TProgramModule param)
   {
         send ("program");
         send (param.name);
         send (";");
         style_empty_line ();
         send_import_sect (param.impl_imports);
         send_decl_part (param.impl_decl);
         style_new_line ();
         send ("begin");
         send_stat_list (param.init);
         send ("end");
         style_no_space ();
         send (".");
   }

   public void send_library_decl (TLibraryModule param)
   {
         send ("library");
         send (param.name);
         send (";");
         style_empty_line ();
         send_import_sect (param.impl_imports);
         send_decl_part (param.impl_decl);
         style_new_line ();
         send ("begin");
         send_stat_list (param.init);
         send ("end");
         style_no_space ();
         send (".");
   }

   public void send_module_decl (TModule param)
   {
         if (param.conv_TUnitModule () != null)
         {
            TUnitModule param0 = param.conv_TUnitModule ();
            send_unit_decl (param0.conv_TUnitModule ());
         }
         else if (param.conv_TProgramModule () != null)
         {
            TProgramModule param0 = param.conv_TProgramModule ();
            send_program_decl (param0.conv_TProgramModule ());
         }
         else if (param.conv_TLibraryModule () != null)
         {
            TLibraryModule param0 = param.conv_TLibraryModule ();
            send_library_decl (param0.conv_TLibraryModule ());
         }
   }
}
