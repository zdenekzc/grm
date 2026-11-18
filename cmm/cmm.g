
/* cmm.g */

/* --------------------------------------------------------------------- */

< struct CmmBasic {
     int src_file;
     int src_line;
     int src_column;
} >

< struct CmmCommon : CmmBasic {
    enum CmmKind { };
    CmmKind kind;
} >

< struct CmmExpr : CmmCommon {
    bool type_flag;
    bool constructor_flag;
    bool destructor_flag;
    CmmDecl * item_decl;
    ptr item_type;

    str alt_assign;
    str alt_assign_index;
    str alt_assign_param;
    str alt_read;
    str alt_connect;
    CmmExpr * alt_connect_expr;
    CmmDecl * alt_connect_decl;
    str alt_connect_signal;

    str alt_display;
    str alt_store;
    str alt_read_json;
    str alt_write_json;
    str alt_read_xml;
    str alt_write_xml;
    
    bool gpu_global;

    // auxiliary variables
    
    bool extra_assign; // assign inside condition
    bool call_func; // function call
    CmmClassDecl * class_member; // compound name with base class
    bool var_field; // .var. formal field
    bool str_field; // .str. formal field
    
    bool stream_flag; // cin, cout, ...
    
    bool leading_flag;
    list CmmDecl following_items;
} >

< struct CmmName : CmmExpr { } >
< struct CmmUnaryExpr : CmmExpr {  } >
< struct CmmBinaryExpr : CmmExpr {  } >

< struct CmmStat : CmmCommon {
   bool move_statement;
} >

< struct CmmDecl : CmmStat { } >

< struct CmmSimpleItem : CmmDecl {
     // auxiliary variables
     bool no_init; // skip initialization in for statement
     bool extra_assign; // assign inside condition
     bool cont_line; // do not end line
} >

< struct CmmDeclarator { enum CmmDeclaratorKind { }; CmmDeclaratorKind kind; } >
< struct CmmPtrSpecifier { enum CmmPtrKind { }; CmmPtrKind kind; } >
< struct CmmContSpecifier { enum CmmContKind { }; CmmContKind kind; } >

< struct CmmTemplateParam { enum CmmTemplateParamKind { }; CmmTemplateParamKind kind; } >

/* --------------------------------------------------------------------- */

< type Namespace = CmmNamespaceDecl >
< type Class = CmmClassDecl >
< type Enum = CmmEnumDecl >
< type Typedef = CmmTypedefDecl >
< type Variable = CmmSimpleItem >

// < struct CmmType : CmmCommon { } >
// < struct CmmNamedType : CmmType, kind = namedType { } >

/* --------------------------------------------------------------------- */

< group expr rewrite ( CmmExpr )
             call    ( allocation_expr, deallocation_expr,
                       decl_specifier, type_specifier,
                       modern_cast_expr, special_function ) >

< group stat reuse   ( CmmStat )
             include ( stat, flexible_stat, declaration, member_item )
             exclude ( nested_stat, tail_stat,
                       constructor_declaration, constructor_item,
                       condition, condition_declaration, condition_value, condition_item,
                       parameter_declaration, plain_parameter, value_parameter )
             priority ( simple_stat ) >

/* --------------------------------------------------------------------- */

< struct CmmExtensionStat : CmmStat, kind = extensionStat { } >
< artificial stat, extension_stat, CmmExtensionStat >

/* --------------------------------------------------------------------- */

< execute_on_choose
     on_binary_expr :
        pm_expr,
        multiplicative_expr,
        additive_expr,
        shift_expr,
        relational_expr,
        equality_expr,
        and_expr,
        exclusive_or_expr,
        inclusive_or_expr,
        logical_and_expr,
        logical_or_expr,
        assignment_expr,
        colon_expr,
        comma_expr >

< predicate_on_choose
     is_binary_expression :
        pm_expr,
        multiplicative_expr,
        additive_expr,
        shift_expr,
        relational_expr,
        equality_expr,
        and_expr,
        exclusive_or_expr,
        inclusive_or_expr,
        logical_and_expr,
        logical_or_expr,
        assignment_expr,
        colon_expr,
        comma_expr >

< predicate_on_choose
     is_postfix_expression :
        postfix_expr >

< predicate_on_choose
     is_cast_expression :
        cast_expr >

< execute_on_end on_ident_expr : ident_expr >
< execute_on_end on_int_value : int_value >
< execute_on_end on_real_value : real_value >
< execute_on_end on_char_value : char_value >
< execute_on_end on_string_value : string_value >
< execute_on_end on_this_expr : this_expr >
< execute_on_end on_subexpr_expr : subexpr_expr >

< execute_on_end on_modern_cast_expr : modern_cast_expr >
< execute_on_end on_typeid_expr : typeid_expr >
< execute_on_end on_type_name : type_name >
< execute_on_end on_type_specifier : type_specifier >
< execute_on_end on_const_specifier : const_specifier >
< execute_on_end on_volatile_specifier : volatile_specifier >
< execute_on_end on_decl_specifier : decl_specifier >

< execute_on_end on_index_expr : index_expr >
< execute_on_end on_call_expr : call_expr >
< execute_on_end on_field_expr : field_expr >
< execute_on_end on_ptr_field_expr : ptr_field_expr >
< execute_on_end on_post_inc_expr : post_inc_expr >
< execute_on_end on_post_dec_expr : post_dec_expr >

< execute_on_end on_bit_not_expr : bit_not_expr >
< execute_on_end on_inc_expr : inc_expr >
< execute_on_end on_dec_expr : dec_expr >
< execute_on_end on_deref_expr : deref_expr >
< execute_on_end on_addr_expr : addr_expr >
< execute_on_end on_plus_expr : plus_expr >
< execute_on_end on_minus_expr : minus_expr >
< execute_on_end on_log_not_expr : log_not_expr >
< execute_on_end on_sizeof_expr : sizeof_expr >
< execute_on_end on_allocation_expr : allocation_expr >
< execute_on_end on_deallocation_expr : deallocation_expr >
< execute_on_end on_throw_expr : throw_expr >

/* --------------------------------------------------------------------- */

< literals // identifiers for literals
   LPAREN     : '(' ;
   RPAREN     : ')' ;
   LBRACKET   : '[' ;
   RBRACKET   : ']' ;
   LBRACE     : '{' ;
   RBRACE     : '}' ;

   DOT        : '.'  ;
   ARROW      : "->" ;
   SCOPE      : "::" ;

   LOG_NOT    : '!' ;
   BIT_NOT    : '~' ;

   INC        : "++"  ;
   DEC        : "--"  ;

   DOT_STAR   : ".*"  ;
   ARROW_STAR : "->*" ;

   STAR       : '*' ;
   SLASH      : '/' ;
   MOD        : '%' ;

   PLUS       : '+' ;
   MINUS      : '-' ;

   SHL        : "<<" ;
   SHR        : ">>" ;

   LESS             : '<'  ;
   GREATER          : '>'  ;
   LESS_OR_EQUAL    : "<=" ;
   GREATER_OR_EQUAL : ">=" ;

   EQUAL            : "==" ;
   UNEQUAL          : "!=" ;

   BIT_AND    : '&' ;
   BIT_XOR    : '^' ;
   BIT_OR     : '|' ;

   LOG_AND    : "&&" ;
   LOG_OR     : "||" ;

   ASSIGN         : '='   ;
   MUL_ASSIGN     : "*="  ;
   DIV_ASSIGN     : "/="  ;
   MOD_ASSIGN     : "%="  ;
   PLUS_ASSIGN    : "+="  ;
   MINUS_ASSIGN   : "-="  ;
   SHL_ASSIGN     : "<<=" ;
   SHR_ASSIGN     : ">>=" ;
   BIT_AND_ASSIGN : "&="  ;
   BIT_XOR_ASSIGN : "^="  ;
   BIT_OR_ASSIGN  : "|="  ;

   QUESTION   : '?' ;
   COMMA      : ',' ;

   COLON      : ':' ;
   SEMICOLON  : ';' ;
   DOTS       : "..." ;
>

/*
identifier
number
real_number
character_literal
string_literal
*/

/* --------------------------------------------------------------------- */

/* simple name */

simple_name <CmmSimpleName:CmmName, kind=simpleName>:
   id:identifier ;

/* base name */

global_variant <select CmmName>:
   simple_name |
   special_function ;

global_name <CmmGlobalName:CmmName, kind=globalName>:
   "::"
   inner_name:global_variant ;

base_variant <select CmmName>:
   global_name |
   simple_name |
   special_function ;

base_name <choose CmmName>:
   base_variant
   <execute on_base_name> ;

/* compound name */

destructor_name <CmmDestructorName:CmmName, kind=destructorName>:
   "~"
   inner_name:simple_name ;

cont_variant <select CmmName>:
   simple_name |
   special_function |
   destructor_name ;

cont_name <CmmCompoundName:CmmName, kind=compoundName>:
   <store left:CmmName>
   <no_space> "::" <no_space>
   right:cont_variant
   <execute on_cont_name> ;

/* template name */

template_name <CmmTemplateName:CmmName, kind=templateName>:
   <store left:CmmName>
   template_args:template_arg_list
   <execute on_template_name> ;

field_name <choose CmmName>:
   simple_name
   (
      { is_template_name (CmmName) }?
      template_name
      <execute on_base_name> // !?
   )*;

/* qualified name */

qualified_name <choose CmmName>:
   base_name
   (
      cont_name
      <execute on_base_name>
   |
      { is_template_name (CmmName) }?
      template_name
      <execute on_base_name>
   )*;

new_qualified_name <choose CmmName>:
   base_variant
   (
      <execute on_base_name>
      cont_name
   |
      { is_template_name (CmmName) }?
      <execute on_base_name>
      template_name
   )*;

/* --------------------------------------------------------------------- */

/* primary expression */

primary_expr <select CmmExpr>:
   ident_expr |
   int_value |
   real_value |
   char_value |
   string_value |
   this_expr |
   lambda_expr |
   subexpr_expr ;

ident_expr <return CmmName>:
   qualified_name ;

int_value <CmmIntValue:CmmExpr, kind=intValue>:
   value:number ;

real_value <CmmRealValue:CmmExpr, kind=realValue>:
   value:real_number ;

char_value <CmmCharValue:CmmExpr, kind=charValue>:
   value:character_literal ;

string_value <CmmStringValue:CmmExpr, kind=stringValue>:
   value:string_literal
   ( <add> string_value_cont )* ; // !?

string_value_cont <CmmStringCont>:
   value:string_literal ;

this_expr <CmmThisExpr:CmmExpr, kind=thisExpr>:
   "this" ;

lambda_expr <CmmLambdaExpr:CmmExpr, kind=lambdaExpr>:
   '[' ( '&' <set by_reference = true> )? ']' body:compound_stat ;

subexpr_expr <CmmSubexprExpr:CmmExpr, kind=subexprExpr>:
   '(' param:expr ')' ;

/* postfix expression */

postfix_start <select CmmExpr>:
   { is_signal_slot () }? signal_slot_expr |
   primary_expr |
   modern_cast_expr |
   typeid_expr |
   type_name |
   type_specifier |
   const_specifier |
   volatile_specifier |
   decl_specifier;

signal_slot_expr <CmmSignalSlotExpr:CmmExpr, kind=signalSlotExpr >:
      macro_name:identifier
      '('
      func_name:identifier
      (
         '('
          parameters:parameter_declaration_list
         ')'
      )?
      ')' ;

modern_cast_expr <CmmModernCastExpr:CmmExpr, kind=modernCastExpr>:
   ( "dynamic_cast"       <set cast_kind = dynamicCast> |
     "static_cast"        <set cast_kind = staticCast>  |
     "const_cast"         <set cast_kind = constCast>   |
     "reinterpret_cast"   <set cast_kind = reinterpreterCast> )
   '<' <no_space> type:type_id <no_space> '>'
   '(' param:expr ')' ;

typeid_expr <CmmTypeIdExpr:CmmExpr, kind=typeIdExpr>:
   "typeid"
   '('
   value:expr
   ')' ;

postfix_expr <choose CmmExpr>:
   postfix_start
   (
      index_expr |
      call_expr |
      field_expr |
      ptr_field_expr |
      post_inc_expr |
      post_dec_expr
   )* ;

index_expr <CmmIndexExpr:CmmExpr, kind=indexExpr>:
   <store left:CmmExpr>
   '[' param:expr ']' ; // !?

call_expr <CmmCallExpr:CmmExpr, kind=callExpr>:
   <store left:CmmExpr>
   '(' param_list:expr_list ')' ;

field_expr <CmmFieldExpr:CmmExpr, kind=fieldExpr>:
   <store left:CmmExpr>
   <no_space> '.' <no_space>
   field_name:field_name ; // !?

ptr_field_expr <CmmPtrFieldExpr:CmmExpr, kind=ptrFieldExpr>:
   <store left:CmmExpr>
   <no_space> "->" <no_space>
   field_name:field_name ; // !?

post_inc_expr <CmmPostIncExpr:CmmExpr, kind=postIncExpr>:
   <store left:CmmExpr>
   "++" ;

post_dec_expr <CmmPostDecExpr:CmmExpr, kind=postDecExpr>:
   <store left:CmmExpr>
   "--" ;

expr_list <CmmExprList>:
   (
       <add> assignment_expr
       ( ',' <add> assignment_expr )*
   )? ;

/* unary expression */

unary_expr <select CmmExpr>:
   postfix_expr |
   inc_expr |
   dec_expr |
   deref_expr |
   addr_expr |
   plus_expr |
   minus_expr |
   bit_not_expr |
   log_not_expr |
   sizeof_expr |
   allocation_expr |
   deallocation_expr |
   throw_expr ;

inc_expr <CmmIncExpr:CmmUnaryExpr, kind=incExpr>:
   "++" param:cast_expr ;

dec_expr <CmmDecExpr:CmmUnaryExpr, kind=decExpr>:
   "--" param:cast_expr ;

deref_expr <CmmDerefExpr:CmmUnaryExpr, kind=derefExpr>:
   '*' param:cast_expr ;

addr_expr <CmmAddrExpr:CmmUnaryExpr, kind=addrExpr>:
   '&' param:cast_expr ;

plus_expr <CmmPlusExpr:CmmUnaryExpr, kind=plusExpr>:
   '+' param:cast_expr ;

minus_expr <CmmMinusExpr:CmmUnaryExpr, kind=minusExpr>:
   '-' param:cast_expr ;

bit_not_expr <CmmBitNotExpr:CmmUnaryExpr, kind=bitNotExpr>:
   '~' <execute on_middle_bit_not_expr> param:cast_expr ;

log_not_expr <CmmLogNotExpr:CmmUnaryExpr, kind=logNotExpr>:
   '!' param:cast_expr ;

sizeof_expr <CmmSizeofExpr:CmmUnaryExpr, kind=sizeofExpr>:
   "sizeof"
    value:unary_expr ;

/* new */

allocation_expr <CmmNewExpr:CmmUnaryExpr, kind=newExpr>:
   "new"
   (
      type1:new_type_id
   |
      '(' type2:type_id ')'
   )
   (
      '(' init_list:expr_list ')'
   )? ;

new_type_id <CmmNewTypeId>:
   type_spec:type_specifiers
   ptr:ptr_specifier_list
   ( <add> allocation_array_limit )* ;

allocation_array_limit <CmmNewArrayLimit>:
   '[' value:expr ']'  ;

/* delete */

deallocation_expr <CmmDeleteExpr:CmmUnaryExpr, kind=deleteExpr>:
   // ( "::" <set a_global = true> )?
   "delete"
   ( '[' ']' <set a_array = true> )?
   param:cast_expr ;

/* cast expression */

cast_expr <choose CmmExpr>:
   unary_expr
   (
      <new CmmCastExpr:CmmBinaryExpr>
      <set kind=castExpr>
      <store left:CmmExpr>
      right:cast_expr
   )? ;

/* pm expression */

pm_expr <choose CmmExpr>:
   cast_expr
   (
      <new CmmPtrMemExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( ".*"  <set kind=dotMemberExpr> |
        "->*" <set kind=arrowMemberExpr> )
      right:cast_expr
   )* ;

/* arithmetic and logical expressions */

multiplicative_expr <choose CmmExpr>:
   pm_expr
   (
      <new CmmMulExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '*' <set kind=mulExpr> |
        '/' <set kind=divExpr> |
        '%' <set kind=modExpr> |
        { is_mul }? <set kind=customMulExpr> custom_mul:identifier )
      right:pm_expr
   )* ;

additive_expr <choose CmmExpr>:
   multiplicative_expr
   (
      <new CmmAddExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '+' <set kind=addExpr> |
        '-' <set kind=subExpr> |
        { is_add }? <set kind=customAddExpr> custom_add:identifier )
      right:multiplicative_expr
   )* ;

shift_expr <choose CmmExpr>:
   additive_expr
   (
      <new CmmShiftExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( "<<" <set kind=shlExpr> |
        ">>" <set kind=shrExpr> )
      right:additive_expr
   )* ;

relational_expr <choose CmmExpr>:
   shift_expr
   (
      <new CmmRelExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '<'  <set kind=ltExpr> |
        '>'  <set kind=gtExpr> |
        "<=" <set kind=leExpr> |
        ">=" <set kind=geExpr> )
      right:shift_expr
   )* ;

equality_expr <choose CmmExpr>:
   relational_expr
   (
      <new CmmEqExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( "==" <set kind=eqExpr> |
        "!=" <set kind=neExpr> )
      right:relational_expr
   )* ;

and_expr <choose CmmExpr>:
   equality_expr
   (
      <new CmmAndExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      '&' <set kind=bitAndExpr>
      right:equality_expr
   )* ;

exclusive_or_expr <choose CmmExpr>:
   and_expr
   (
      <new CmmXorExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      '^' <set kind=bitXorExpr>
      right:and_expr
   )* ;

inclusive_or_expr <choose CmmExpr>:
   exclusive_or_expr
   (
      <new CmmOrExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '|' <set kind=bitOrExpr> )
      right:exclusive_or_expr
   )* ;

logical_and_expr <choose CmmExpr>:
   inclusive_or_expr
   (
      <new CmmAndAndExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      "&&" <set kind=logAndExpr>
      right:inclusive_or_expr
   )* ;

logical_or_expr <choose CmmExpr>:
   logical_and_expr
   (
      <new CmmOrOrExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      "||" <set kind=logOrExpr>
      right:logical_and_expr
   )* ;

/* conditional and assignment expression */

assignment_expr <choose CmmExpr>:
   logical_or_expr // !?
   (
      <new CmmAssignExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '='   <set kind=assignExpr>    |
        "+="  <set kind=addAssignExpr> |
        "-="  <set kind=subAssignExpr> |
        "*="  <set kind=mulAssignExpr> |
        "/="  <set kind=divAssignExpr> |
        "%="  <set kind=modAssignExpr> |
        "<<=" <set kind=shlAssignExpr> |
        ">>=" <set kind=shrAssignExpr> |
        "&="  <set kind=andAssignExpr> |
        "^="  <set kind=xorAssignExpr> |
        "|="  <set kind=orAssignExpr>  |
        '?'   <set kind=condExpr> middle:assignment_expr ':' )
      right:logical_or_expr // !?
   )? ;

/* expression */

colon_expr <return CmmExpr>:
   assignment_expr ;

/*
colon_expr <choose CmmExpr>:
   assignment_expr
   (
      <new CmmColonExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ':' <set kind=colonExpr> // !?
      right:assignment_expr
   )? ;
*/

comma_expr <choose CmmExpr>:
   colon_expr
   (
      <new CmmCommaExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ',' <set kind=commaExpr>
      right:colon_expr
   )* ;

expr <return CmmExpr>:
   comma_expr
   <execute on_expr> ;

/* constant expression */

const_expr <return CmmExpr>:
   assignment_expr ;

/* --------------------------------------------------------------------- */

/* statement */

stat <select CmmStat>:

   flexible_stat |
   empty_stat |
   compound_stat |
   if_stat |
   while_stat |
   do_stat |
   for_stat |
   switch_stat |
   case_stat |
   default_stat |
   break_stat |
   continue_stat |
   return_stat |
   goto_stat |
   try_stat ;

nested_stat <return CmmStat>: /* statement with different output indentation */
   <indent>
   stat
   <unindent> ;

tail_stat <return CmmStat>: /* statement with different output indentation (after else) */
   <indent>
   stat
   <unindent> ;

empty_stat <CmmEmptyStat:CmmStat, kind=emptyStat>:
   ';' ;

compound_stat <CmmCompoundStat:CmmStat, kind=compoundStat>:
   '{'
   <indent>
   <execute on_open_compound_statement>
   ( <new_line> <execute on_declaration> <add> stat )*
   <execute on_close_compound_statement>
   <unindent>
   '}' ;

if_stat <CmmIfStat:CmmStat, kind=ifStat>:
   "if"
   '(' cond:condition ')'
   <execute on_open_if_statement>
   then_stat:nested_stat
   (
      <silent>
      <new_line>
      "else"
      else_stat:tail_stat
   )?
   <execute on_close_if_statement> ;

while_stat <CmmWhileStat:CmmStat, kind=whileStat>:
   "while"
   '(' cond:condition ')'
   <execute on_open_while_statement>
   body:nested_stat
   <execute on_close_while_statement> ;

do_stat <CmmDoStat:CmmStat, kind=doStat>:
   "do"
   body:nested_stat
   "while" '(' cond_expr:expr ')' ';' ;

for_stat <CmmForStat:CmmStat, kind=forStat>:
   "for"
   '('
   ( from_expr:condition )?
   (
      ':'
      iter_expr:expr
   |
      ';'
      (cond_expr:expr)?
      ';'
      (step_expr:expr)?
   )
   ')'
   <execute on_open_for_statement>
   body:nested_stat
   <execute on_close_for_statement> ;

switch_stat <CmmSwitchStat:CmmStat, kind=switchStat>:
   "switch"
   '(' cond:condition ')'
   <execute on_open_switch_statement>
   body:nested_stat
   <execute on_close_switch_statement> ;

case_stat <CmmCaseStat:CmmStat, kind=caseStat>:
   "case" case_expr:expr ':'
   <new_line>
   body:nested_stat ;

default_stat <CmmDefaultStat:CmmStat, kind=defaultStat>:
   "default" ':'
   <new_line>
   body:nested_stat ;

break_stat <CmmBreakStat:CmmStat, kind=breakStat>:
   "break" ';' ;

continue_stat <CmmContinueStat:CmmStat, kind=continueStat>:
   "continue" ';' ;

return_stat <CmmReturnStat:CmmStat, kind=returnStat>:
   "return" (return_expr:expr)? ';' ;

goto_stat <CmmGotoStat:CmmStat, kind=gotoStat>:
   "goto" goto_lab:identifier ';' ;

/* simple statement */

flexible_stat <choose CmmStat>:
   <execute_no_param on_open_flexible_stat>
   expr
   (
      { is_expression (CmmExpr) }?
      simple_stat
   |
      { is_constructor (CmmExpr) }?
      constructor_declaration
   |
      simple_declaration
   ) ;

simple_stat <CmmSimpleStat:CmmStat, kind=simpleStat>:
   <store inner_expr:CmmExpr>
   <execute on_open_simple_stat>
   (
       <new_line>
       <execute on_open_expr_block>
       body:compound_stat
       <execute on_close_expr_block>
   |
      ';'
      <execute on_simple_statement>
   );

/* ---------------------------------------------------------------------- */

/* declaration specifiers */

decl_specifier <CmmDeclSpec:CmmExpr, kind=declSpec>:
   (
      "inline"   <set a_inline = true>   |
      "virtual"  <set a_virtual = true>  |
      "explicit" <set a_explicit = true> |
      "mutable"  <set a_mutable = true>  |

      // "extern"   <set a_extern = true>   |
      "static"   <set a_static = true>   |
      // "auto"     <set a_auto = true>     |
      "register" <set a_register = true>
   )
   ( "~" <set a_destructor = true> <execute on_middle_decl_specifier> )?
   param:type_specifiers ;

/* const / volatile */

const_specifier <CmmConstSpecifier:CmmExpr, kind=constSpec>:
   "const"
   param:type_specifiers ;

volatile_specifier <CmmVolatileSpecifier:CmmExpr, kind=volatileSpec>:
   "volatile"
   param:type_specifiers ;

/* type specifier */

type_specifier <CmmTypeSpec:CmmExpr, kind=typeSpec>:
   (
      "signed" <set a_signed = true>
   |
      "unsigned" <set a_unsigned = true>
   )?
   (
      "short"    <set a_short=true> |

      "long"     <set a_long=true>
         (
            "long"   <set a_long_long=true> |
            "double" <set a_long_double=true>
         )? |

      "bool"     <set a_bool = true>   |
      "char"     <set a_char = true>   |
      "wchar_t"  <set a_wchar = true>  |
      "int"      <set a_int = true>    |
      "float"    <set a_float = true>  |
      "double"   <set a_double = true> |
      "void"     <set a_void = true>
   ) ;

/* typename */

type_name <CmmTypeName:CmmExpr, kind=typeName>:
   "typename"
   qual_name:qualified_name ;

/* type specifiers */

type_specifiers <select CmmExpr>:
   ident_expr |
   type_name |
   type_specifier |
   const_specifier |
   volatile_specifier |
   decl_specifier;

/* ---------------------------------------------------------------------- */

/* pointer declarator */

pointer_declarator <CmmPointerDeclarator:CmmDeclarator, kind=pointerDeclarator>:
   '*'
   cv_spec:cv_specifier_list
   inner_declarator:declarator ;

/* reference declarator */

reference_declarator <CmmReferenceDeclator:CmmDeclarator, kind=referenceDeclarator>:
   '&'
   cv_spec:cv_specifier_list
   inner_declarator:declarator ;

cv_specifier_list <CmmCvSpecifier>:
   (
      "const" <set cv_const = true>
   |
      "volatile" <set cv_volatile = true>
   )* ;

/* basic, empty and nested declarator */

basic_declarator <CmmBasicDeclarator:CmmDeclarator, kind=basicDeclarator>:
   qual_name:new_qualified_name ;

empty_declarator <CmmEmptyDeclarator:CmmDeclarator, kind=emptyDeclarator>:
   ;

nested_declarator <CmmNestedDeclarator:CmmDeclarator, kind=nestedDeclarator>:
   '('
   inner_declarator:declarator
   ')' ;

/* array declarator */

array_declarator <CmmArrayDeclarator:CmmDeclarator, kind=arrayDeclarator>:
   <store inner_declarator:CmmDeclarator>
   '['
   ( lim:expr )?
   ']' ;

/* function declarator */

function_declarator <CmmFunctionDeclarator:CmmDeclarator, kind=functionDeclarator>:
   <store inner_declarator:CmmDeclarator>
   '('
   parameters:parameter_declaration_list
   ')'
   ( "const" <set a_const = true> )?
   ( "override" <set a_override = true> )?
   ( exception_spec:exception_specification )? ;

/* entry declarator */

entry_declarator <select CmmDeclarator>:
   basic_declarator |
   empty_declarator |
   nested_declarator ;

/* continue declarator */

continue_declarator <choose CmmDeclarator>:
   entry_declarator
   (
      array_declarator |
      function_declarator
   )* ;

/* declarator */

declarator <select CmmDeclarator>:
   pointer_declarator |
   reference_declarator |
   continue_declarator ;

/* simple declarator */

simple_declarator <return CmmDeclarator>:
   declarator
   <execute on_simple_declarator> ;

/* common declarator */

common_declarator <return CmmDeclarator>:
   declarator ;

/* constructor declarator */

constructor_declarator <choose CmmDeclarator>:
   empty_declarator
   (
      function_declarator
   ) ;

ptr_specifier_list <CmmPtrSpecifierSect>:
   ;

/* ---------------------------------------------------------------------- */

/* parameter declarations */

parameter_declaration_list <CmmStatSect>:
   (
      <add> parameter_declaration
      ( ',' <add> parameter_declaration )*
   )? ;

parameter_declaration <choose CmmStat>:
      assignment_expr
      (
         { is_value_parameter (CmmStat) }?
         value_parameter
      |
         plain_parameter
      )
   |
      dots_parameter
   ;

value_parameter <CmmSimpleStat>:
   <store inner_expr:CmmExpr> ;

plain_parameter <CmmSimpleDecl>:
   <store type_spec:CmmExpr>
   <add> parameter_item ;

parameter_item <CmmSimpleItem>:
   declarator:common_declarator
   ( init:initializer )?
   attr:attr_list ;

dots_parameter <CmmDotsParam:CmmStat, kind=dotsParam>:
   "..." ;

/* ---------------------------------------------------------------------- */

/* type id */

type_id <CmmTypeId>:
   type_spec:type_specifiers
   declarator:common_declarator ;

/* ---------------------------------------------------------------------- */

/* initializer */

initializer <CmmInitializer>:
   '=' value:initializer_item ;

initializer_item <select CmmInitItem>:
   simple_initializer |
   initializer_list ;

simple_initializer <CmmInitSimple:CmmInitItem>:
   inner_expr:assignment_expr ;

initializer_list <CmmInitList:CmmInitItem>:
   '{'
   <indent>
   (
      <add> initializer_item
      (
         ','
         <new_line>
         <add> initializer_item
      )*
   )?
   <unindent>
   '}' ;

/* ---------------------------------------------------------------------- */

/* attributes */

attr_item <CmmAttr>:
   attr_expr:assignment_expr ;

attr_group <CmmAttrGroup>:
   "[["
   <add> attr_item
   (
      ','
      <add> attr_item
   )*
   "]]";

attr_list <CmmAttrSect>:
   ( <add> attr_group )* ;

/* ---------------------------------------------------------------------- */

/* simple declaration */

simple_declaration <CmmSimpleDecl:CmmDecl, kind=simpleDecl>:
   <store type_spec:CmmExpr>
   <execute on_open_simple_declaration>
   <add> simple_item
   <execute on_simple_item>
   (
      ','
      <add> simple_item
      <execute on_simple_item>
   )*
   (
      <execute on_open_function>
      <new_line>
      body:compound_stat
      <execute on_close_function>
   |
      ';'
   )
   <execute on_simple_declaration> ;

simple_item <CmmSimpleItem, kind=simpleItem>:
   declarator:simple_declarator
   // !? ( ':' width:const_expr )?
   ( init:initializer )?
   attr:attr_list ;

/* constructor declaration */

constructor_declaration <CmmSimpleDecl:CmmDecl, kind=simpleDecl>:
   <store type_spec:CmmExpr>
   <execute on_open_constructor_declaration>
   <add> constructor_item
   <execute on_simple_item>
   (
      <execute on_open_function>
      (
        ':'
        <new_line>
        ctor_init:ctor_initializer
      )?
      <new_line>
      body:compound_stat
      <execute on_close_function>
   |
      ';'
   )
   <execute on_simple_declaration> ;

constructor_item <CmmSimpleItem>:
   declarator:constructor_declarator
   attr:attr_list ;

/* condition  */

condition <choose CmmStat>:
   expr
   (
      { is_expression (CmmExpr) }?
      condition_value
   |
      condition_declaration
   ) ;

condition_declaration <CmmSimpleDecl>:
   <store type_spec:CmmExpr>
   (
      <add> condition_item
      <execute on_simple_item>
      (
         ','
         <add> condition_item
         <execute on_simple_item>
      )*
   ) ;

condition_item <CmmSimpleItem>:
   declarator:simple_declarator
   // NO ( ':' width:const_expr )?
   ( init:initializer )?
   attr:attr_list ; // !?

condition_value <CmmSimpleStat>:
   <store inner_expr:CmmExpr> ;

/* ---------------------------------------------------------------------- */

/* declaration */

declaration_list <CmmStatSect> <start>:
   ( <execute on_declaration> <add> declaration <new_line> )* ;

declaration <select CmmStat>:

   flexible_stat |
   empty_stat |

   compound_stat |
   if_stat |
   while_stat |
   do_stat |
   for_stat |
   switch_stat |

   class_declaration |
   enum_declaration |

   typedef_declaration |
   friend_declaration |

   namespace_declaration |
   using_declaration |

   extern_declaration |
   template_declaration |
   stencil_declaration ;

/* ---------------------------------------------------------------------- */

/* namespace declaration */

namespace_declaration <CmmNamespaceDecl:CmmDecl, kind=namespaceDecl>:
   <execute on_start_namespace>
   "namespace"
   simp_name:simple_name
   attr:attr_list
   <execute on_namespace>
   <new_line>
   '{'
      <execute on_open_namespace>
      <new_line>
      <indent>
      members:declaration_list
      <unindent>
      <execute on_close_namespace>
   '}'
   <execute on_stop_namespace> ;

/* using declaration */

using_declaration <CmmUsingDecl:CmmDecl, kind=usingDecl>:
   "using"
   (
      "namespace" <set a_namespace = true>
   )?
   qual_name:qualified_name
   <execute on_using>
   ';' ;

/* linkage declaration */

extern_declaration <CmmExternDecl:CmmDecl, kind=externDecl>:
   "extern"
   ( language:string_literal )?
   (
      '{' members:declaration_list '}'
   |
      inner_declaration:declaration
   ) ;

/* typedef declaration */

typedef_declaration <CmmTypedefDecl:CmmDecl, kind=typedefDecl>:
   "typedef"
   type_spec:type_specifiers
   declarator:simple_declarator
   <execute on_typedef>
   ';' ;

/* friend declaration */

friend_declaration <CmmFriendDecl:CmmDecl, kind=friendDecl>:
   "friend"
   inner_declaration:declaration ;

/* ---------------------------------------------------------------------- */

/* enum */

enum_declaration <CmmEnumDecl:CmmDecl, kind=enumDecl>:
   <execute on_start_enum>
   "enum"
   simp_name:simple_name
   <execute on_enum>
   (
      <new_line>
      '{'
         <execute on_open_enum>
         <indent>
         enum_items:enum_list
         <unindent>
         <execute on_close_enum>
      '}'
    )?
    ';'
    <execute on_stop_enum> ;

enum_list <CmmEnumSect>:
   (
      <add> enumerator
      ( ',' <add> enumerator )*
   )? ;

enumerator <CmmEnumItem>:
   <new_line>
   simp_name:simple_name
   <execute on_enum_item>
   ( '=' init_value:const_expr )? ;

/* ---------------------------------------------------------------------- */

/* class */

class_declaration <CmmClassDecl:CmmDecl, kind=classDecl>:
   <execute on_start_class>
   (
      "class"  <set style = classStyle> |
      "struct" <set style = structStyle> |
      "union"  <set style = unionStyle>
   )
   simp_name:simple_name
   attr:attr_list
   <execute on_class>
   (
      ( ':' base_list:base_specifier_list )?
      <new_line>
     '{'
        <execute on_open_class>
        <indent>
        members:member_list
        <unindent>
        <execute on_close_class>
     '}'
   )?
   ';'
   <execute on_stop_class> ;

/* members */

member_visibility <CmmMemberVisibility:CmmDecl, kind=visibilityDecl>:
   ( "private"   <set access = privateAccess> |
     "protected" <set access = protectedAccess> |
     "public"    <set access = publicAccess> )
   <execute on_member_visibility>
   <no_space> ':' ;

member_item <select CmmStat>:

   member_visibility |

   flexible_stat |
   empty_stat |

   compound_stat |
   if_stat |
   while_stat |
   for_stat |

   class_declaration |
   enum_declaration |

   typedef_declaration |
   friend_declaration |

   using_declaration |
   template_declaration |
   stencil_declaration ;

member_list <CmmStatSect>:
   ( <execute on_declaration> <execute on_start_member_item> <add> member_item <new_line> )* ;

/* base specification */

base_specifier_list <CmmBaseSect>:
   <add> base_specifier
   ( ',' <add> base_specifier )* ;

base_specifier <CmmBaseItem>:
   ( "virtual" <set a_virtual = true> )?
   ( "private"   <set access = privateBase> |
     "protected" <set access = protectedBase> |
     "public"    <set access = publicBase> |
                 <set access = unknownBase> )
   from_cls:qualified_name ;

/* constructor initializer */

ctor_initializer <CmmCtorInitializer>:
   <indent>
   <add> member_initializer
   (
      ','
      <new_line>
      <add> member_initializer
   )*
   <unindent> ;

member_initializer <CmmMemberInitializer>:
   simp_name:simple_name // !? qualified_name
   <execute on_member_initializer>
   '('
   params:expr_list
   ')' ;

/* ---------------------------------------------------------------------- */

/* special member functions */

conversion_specifiers <CmmConvSpec>: // !?
   type_spec:type_specifiers
   ptr_spec:ptr_specifier_list ;

special_function <CmmSpecialFuction:CmmName, kind=specialName>:
   "operator"
   (
      conv:conversion_specifiers

   | "new"    <set spec_new=true>    ( '[' ']' <set spec_new_array=true> )?
   | "delete" <set spec_delete=true> ( '[' ']' <set spec_delete_array=true> )?

   | "+" <set spec_add=true>
   | "-" <set spec_sub=true>
   | "*" <set spec_mul=true>
   | "/" <set spec_div=true>
   | "%" <set spec_mod=true>
   | "^" <set spec_xor=true>
   | "&" <set spec_and=true>
   | "|" <set spec_or=true>
   | "~" <set spec_not=true>

   | "!"  <set spec_log_not=true>
   | "="  <set spec_assign=true>
   | "<"  <set spec_lt=true>
   | ">"  <set spec_gt=true>
   | "+=" <set spec_add_assign=true>
   | "-=" <set spec_sub_assign=true>
   | "*=" <set spec_mul_assign=true>
   | "/=" <set spec_div_assign=true>
   | "%=" <set spec_mod_assign=true>

   | "^="  <set spec_xor_assign=true>
   | "&="  <set spec_and_assign=true>
   | "|="  <set spec_or_assign=true>
   | "<<"  <set spec_shl=true>
   | ">>"  <set spec_shr=true>
   | ">>=" <set spec_shl_assign=true>
   | "<<=" <set spec_shr_assign=true>
   | "=="  <set spec_eq=true>
   | "!="  <set spec_ne=true>

   | "<="  <set spec_le=true>
   | ">="  <set spec_ge=true>
   | "&&"  <set spec_log_and=true>
   | "||"  <set spec_log_or=true>
   | "++"  <set spec_inc=true>
   | "--"  <set spec_dec=true>
   | ","   <set spec_comma=true>
   | "->*" <set spec_member_deref=true>
   | "->"  <set spec_deref=true>

   | "(" ")" <set spec_call=true>
   | "[" "]" <set spec_index=true>
   ) ;

/* ---------------------------------------------------------------------- */

/* template declaration */

template_declaration <CmmTemplateDecl:CmmDecl, kind=templateDecl>:
   "template"
   (
      '<'
         params:template_param_list
      '>'
   )?
   inner_declaration:declaration
   <execute on_template_declaration> ;

/* stencil — pojmenovaná šablona s vlastní instantiací.
 * Syntaxe:
 *
 *   stencil access <typename T> {
 *      T value;
 *      void set (T v) { value = v; }
 *      T get ()       { return value; }
 *   }
 *
 *   access <int> numeric;        // instance: vyrobí numeric_value,
 *                                //          numeric_set, numeric_get
 *
 * Klíčové prvky:
 *   - simp_name (povinné): jméno šablony, kterým se v instantiaci
 *     odkazuje
 *   - <execute on_stencil_params> hook PŘED parsováním těla:
 *     registruje typové parametry (T) jako typy do scope, aby se
 *     dal parsovat 'T a' v parametru
 *   - members: deklarace v {} bloku, sdílí typové parametry
 *
 * Mangling instance: jednotlivé členy dostanou jméno
 *     <instance_name>_<member_name>
 *
 * Vnitřní reference mezi členy stencilu se při instantiaci textově
 * přepíšou na mangled jména. */

stencil_declaration <CmmStencilDecl:CmmDecl, kind=stencilDecl>:
   "stencil"
   simp_name:simple_name
   '<' params:template_param_list '>'
   <execute on_stencil_params>
   '{'
   <execute on_open_stencil>
   members:stencil_member_list
   <execute on_close_stencil>
   '}'
   <execute on_stencil_declaration> ;

stencil_member_list <CmmStatSect>:
   ( <execute on_declaration> <add> declaration <new_line> )* ;

template_param_list <CmmTemplateParamSect>:
   (
      <add> template_param
      ( ',' <add> template_param )*
   )? ;

/* template parameter */

template_param <select CmmTemplateParam>:
   template_type_param |
   template_normal_param ;

template_type_param <CmmTemplateTypeParam:CmmTemplateParam, kind=templateTypeParam>:
   (
      "template" '<' params:template_param_list '>'
   )?
   (
      "class" <set a_class = true>
   |
      "typename" <set a_typename = true>
   )
   ( simp_name:simple_name )? ;

template_normal_param <CmmTemplateNormalParam:CmmTemplateParam, kind=templateCommonParam>:
   type_spec:type_specifiers
   declarator:common_declarator
   ( '=' init:shift_expr )? ; // !?

/* template arguments */

template_arg_list <CmmTemplateArgSect>:
   '<'
   (
      <add> template_arg
      ( ',' <add> template_arg )*
   )?
   '>' ;

template_arg <CmmTemplateArg>:
   // value:shift_expr; // !?
   value:parameter_declaration; // !?

/* ---------------------------------------------------------------------- */

/* try statement */

try_stat <CmmTryStat:CmmStat, kind=tryStat>:
   "try"
   <new_line>
   body:compound_stat
   handlers:handler_list ;

handler_list <CmmHandlerSect>:
   <add> handler
   ( <add> handler )* ;

handler <CmmHandlerItem>:
   <new_line>
   "catch"
   '('
   (
      type_spec:type_specifiers
      declarator:common_declarator
   |
      "..." <set dots=true>
   )
   ')'
   <new_line>
   body:compound_stat ;

/* throw expression */

throw_expr <CmmThrowExpr:CmmUnaryExpr, kind=throwExpr >:
   "throw" (inner_expr:assignment_expr)? ;

/* exception specification */

exception_specification <CmmExceptionSect>:
   "throw"
   '('
   (
      <add> exception_specification_item
      ( ',' <add> exception_specification_item )*
   )?
   ')' ;

exception_specification_item <CmmExceptionItem>:
   type:type_id ;

/* ---------------------------------------------------------------------- */

/* kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all */
