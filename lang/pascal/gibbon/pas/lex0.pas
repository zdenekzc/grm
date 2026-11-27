
(**************************************************************************)
(*                                                                        *)
(*                            Lexical Analysis                            *)
(*                                                                        *)
(**************************************************************************)

UNIT Lex0;

INTERFACE

{$DEFINE TYPEINFO}

{.$DEFINE PASCAL}
{.$DEFINE CPP}
{$DEFINE PASCAL_AND_CPP }

Uses {$IFDEF TYPINFO} TypInfo, {$ENDIF}
     SysUtils,
     Fil0, Dir0;

{--------------------------------------------------------------------------}

{$IFDEF PASCAL}

Const pascal = true;
      cpp = false;

Type TSymbol = ( AndSy, ArraySy, AsSy, AsmSy,
                 BeginSy,
                 CaseSy, ClassSy, ConstSy, ConstructorSy,
                 DestructorSy, DispinterfaceSy, DivSy, DoSy, DowntoSy,
                 ElseSy, EndSy, ExceptSy, ExportsSy,
                 FileSy, FinalizationSy, FinallySy, ForSy, FunctionSy,
                 GotoSy,
                 IfSy, ImplementationSy, InSy, InheritedSy,
                 InitializationSy, InlineSy, InterfaceSy, IsSy,
                 LabelSy, LibrarySy,
                 ModSy,
                 NilSy, NotSy,
                 ObjectSy, OfSy, OnSy, OrSy, OutSy,
                 PackedSy, ProcedureSy, ProgramSy, PropertySy,
                 RaiseSy, RecordSy, RepeatSy, ResourcestringSy,
                 SetSy, ShlSy, ShrSy, StringSy,
                 ThenSy, ThreadvarSy, ToSy, TrySy, TypeSy,
                 UnitSy, UntilSy, UsesSy,
                 VarSy,
                 WhileSy, WithSy,
                 XorSy,

                 AbsoluteSy, AbstractSy, AssemblerSy, AtSy, AutomatedSy,
                 CdeclSy,
                 DefaultSy, DispidSy, DynamicSy,
                 ExportSy, ExternalSy,
                 FarSy, ForwardSy, FriendSy,
                 ImplementsSy, IndexSy,
                 MessageSy,
                 NameSy, NearSy, NodefaultSy,
                 OverloadSy, OverrideSy,
                 PascalSy, PrivateSy, ProtectedSy, PublicSy, PublishedSy,
                 ReadSy, ReadonlySy, RegisterSy, ReintroduceSy, ResidentSy,
                 SafecallSy, StdcallSy, StoredSy,
                 VirtualSy,
                 WriteSy, WriteonlySy,

                 PlusSy, MinusSy, AsteriskSy, SlashSy,
                 PeriodSy, CommaSy, ColonSy, SemicolonSy,
                 EqualSy, LessSy, GreaterSy,
                 UnequalSy, LessEqualSy, GreaterEqualSy,
                 ArrowSy, AtSignSy, RangeSy, AssignSy,
                 LParSy, RParSy, LBrackSy, RBrackSy,

                 IdentSy, NumSy, FltSy, StrSy,
                 NoSy);

{$ENDIF}

{--------------------------------------------------------------------------}

{$IFDEF CPP}

Const pascal = false;
      cpp = true;

Type TSymbol = (
        AsmSy,
        AutoSy,
        BreakSy,
        CaseSy,
        CatchSy,
        CharSy,
        ClassSy,
        ConstSy,
        ContinueSy,
        DefaultSy,
        DeleteSy,
        DoSy,
        DoubleSy,
        ElseSy,
        EnumSy,
        ExternSy,
        FloatSy,
        ForSy,
        FriendSy,
        GotoSy,
        IfSy,
        InlineSy,
        IntSy,
        LongSy,
        NewSy,
        OperatorSy,
        PrivateSy,
        ProtectedSy,
        PublicSy,
        RegisterSy,
        ReturnSy,
        ShortSy,
        SignedSy,
        SizeofSy,
        StaticSy,
        StructSy,
        SwitchSy,
        TemplateSy,
        ThisSy,
        ThrowSy,
        TrySy,
        TypedefSy,
        UnionSy,
        UnsignedSy,
        VirtualSy,
        VoidSy,
        VolatileSy,
        WhileSy,

        PlusSy,         { +   }
        MinusSy,        { -   }
        AsteriskSy,     { *   }
        SlashSy,        { /   }
        PeriodSy,       { .   }
        CommaSy,        { ,   }
        ColonSy,        { :   }
        SemicolonSy,    { ;   }

        EqualSy,        { ==  }
        LessSy,         { <   }
        GreaterSy,      { >   }
        UnEqualSy,      { !=  }
        LessEqualSy,    { <=  }
        GreaterEqualSy, { >=  }

        ArrowSy,        { ->  }
        AssignSy,       { =   }

        LParSy,         { (   }
        RParSy,         { )   }
        LBrackSy,       { [   }
        RBrackSy,       { ]   }
        LBraceSy,       (* { *)
        RBraceSy,       (* } *)

        TildaSy,        { ~   }
        PercentSy,      { %   }
        CaretSy,        { ^   }
        AmpersandSy,    { &   }
        BarSy,          { |   }
        QuestionSy,     { ?   }

        DPlusSy,        { ++  }
        DMinusSy,       { --  }
        DColonSy,       { ::  }
        DotsSy,         { ... }
        DotStarSy,      { .*  }
        ArrowStarSy,    { ->* }

        ShlSy,          { <<  }
        ShrSy,          { >>  }
        LogNotSy,       { !   }
        LogAndSy,       { &&  }
        LogOrSy,        { ||  }

        MulAssignSy,    { *=  }
        DivAssignSy,    { /=  }
        ModAssignSy,    { %=  }
        AddAssignSy,    { +=  }
        SubAssignSy,    { -=  }
        ShlAssignSy,    { <<= }
        ShrAssignSy,    { >>= }
        AndAssignSy,    { &=  }
        OrAssignSy,     { |=  }
        XorAssignSy,    { ^=  }


        IdentSy,        { identifier }
        NumSy,          { number }
        FltSy,          { floating point number }
        StrSy,          { string    "" }
        ChrSy,          { character '' }

        EosSy,          { end of source }
        NoSy);

{$ENDIF}

{--------------------------------------------------------------------------}

{$IFDEF PASCAL_AND_CPP}

{$DEFINE PASCAL}
{$DEFINE CPP}

Var   pascal: boolean = true;
      cpp:    boolean = false;

Type TSymbol =
      ( AndSy, ArraySy, AsSy, AsmSy,
        BeginSy,
        CaseSy, ClassSy, ConstSy, ConstructorSy,
        DestructorSy, DispinterfaceSy, DivSy, DoSy, DowntoSy,
        ElseSy, EndSy, ExceptSy, ExportsSy,
        FileSy, FinalizationSy, FinallySy, ForSy, FunctionSy,
        GotoSy,
        IfSy, ImplementationSy, InSy, InheritedSy,
        InitializationSy, InlineSy, InterfaceSy, IsSy,
        LabelSy, LibrarySy,
        ModSy,
        NilSy, NotSy,
        ObjectSy, OfSy, OnSy, OrSy, OutSy,
        PackedSy, ProcedureSy, ProgramSy, PropertySy,
        RaiseSy, RecordSy, RepeatSy, ResourcestringSy,
        SetSy, ShlSy, ShrSy, StringSy,
        ThenSy, ThreadvarSy, ToSy, TrySy, TypeSy,
        UnitSy, UntilSy, UsesSy,
        VarSy,
        WhileSy, WithSy,
        XorSy,

        AbsoluteSy, AbstractSy, AssemblerSy, AtSy, AutomatedSy,
        CdeclSy,
        DefaultSy, DispidSy, DynamicSy,
        ExportSy, ExternalSy,
        FarSy, ForwardSy, FriendSy,
        ImplementsSy, IndexSy,
        MessageSy,
        NameSy, NearSy, NodefaultSy,
        OverloadSy, OverrideSy,
        PascalSy, PrivateSy, ProtectedSy, PublicSy, PublishedSy,
        ReadSy, ReadonlySy, RegisterSy, ReintroduceSy, ResidentSy,
        SafecallSy, StdcallSy, StoredSy,
        VirtualSy,
        WriteSy, WriteonlySy,

        // AsmSy,
        AutoSy,
        BreakSy,
        // CaseSy,
        CatchSy,
        CharSy,
        // ClassSy,
        // ConstSy,
        ContinueSy,
        // DefaultSy,
        DeleteSy,
        // DoSy,
        DoubleSy,
        // ElseSy,
        EnumSy,
        ExternSy,
        FloatSy,
        // ForSy,
        // FriendSy,
        // GotoSy,
        // IfSy,
        // InlineSy,
        IntSy,
        LongSy,
        NewSy,
        OperatorSy,
        // PrivateSy,
        // ProtectedSy,
        // PublicSy,
        // RegisterSy,
        ReturnSy,
        ShortSy,
        SignedSy,
        SizeofSy,
        StaticSy,
        StructSy,
        SwitchSy,
        TemplateSy,
        ThisSy,
        ThrowSy,
        // TrySy,
        TypedefSy,
        UnionSy,
        UnsignedSy,
        // VirtualSy,
        VoidSy,
        VolatileSy,
        // WhileSy,

        PlusSy, MinusSy, AsteriskSy, SlashSy,
        PeriodSy, CommaSy, ColonSy, SemicolonSy,
        EqualSy, LessSy, GreaterSy,
        UnequalSy, LessEqualSy, GreaterEqualSy,
        ArrowSy, AtSignSy, RangeSy, AssignSy,
        LParSy, RParSy, LBrackSy, RBrackSy,

        // PlusSy,         { +   }
        // MinusSy,        { -   }
        // AsteriskSy,     { *   }
        // SlashSy,        { /   }
        // PeriodSy,       { .   }
        // CommaSy,        { ,   }
        // ColonSy,        { :   }
        // SemicolonSy,    { ;   }

        // EqualSy,        { ==  }
        // LessSy,         { <   }
        // GreaterSy,      { >   }
        // UnequalSy,      { !=  }
        // LessEqualSy,    { <=  }
        // GreaterEqualSy, { >=  }

        // ArrowSy,        { ->  }
        // AssignSy,       { =   }

        // LParSy,         { (   }
        // RParSy,         { )   }
        // LBrackSy,       { [   }
        // RBrackSy,       { ]   }
        LBraceSy,       (* { *)
        RBraceSy,       (* } *)

        TildaSy,        { ~   }
        PercentSy,      { %   }
        CaretSy,        { ^   }
        AmpersandSy,    { &   }
        BarSy,          { |   }
        QuestionSy,     { ?   }

        DPlusSy,        { ++  }
        DMinusSy,       { --  }
        DColonSy,       { ::  }
        DotsSy,         { ... }
        DotStarSy,      { .*  }
        ArrowStarSy,    { ->* }

        // ShlSy,          { <<  }
        // ShrSy,          { >>  }
        LogNotSy,       { !   }
        LogAndSy,       { &&  }
        LogOrSy,        { ||  }

        MulAssignSy,    { *=  }
        DivAssignSy,    { /=  }
        ModAssignSy,    { %=  }
        AddAssignSy,    { +=  }
        SubAssignSy,    { -=  }
        ShlAssignSy,    { <<= }
        ShrAssignSy,    { >>= }
        AndAssignSy,    { &=  }
        OrAssignSy,     { |=  }
        XorAssignSy,    { ^=  }

        IdentSy,        { identifier }
        NumSy,          { number }
        FltSy,          { floating point number }
        StrSy,          { string    "" }
        ChrSy,          { character '' }

        EosSy,          { end of source }
        NoSy);

{$ENDIF}

{--------------------------------------------------------------------------}

Const IdentMax  = 255;
      NumberMax = 255;
      StringMax = 255;

Const StoreUpperCase = false;
      CompareUpperCase = true;

Type  TIdent = string;

{--------------------------------------------------------------------------}

Var   sy:         TSymbol;   { current symbol }
      range:      boolean;   { true => next symbol is RangeSy }

      IdentVal:   string [IdentMax];   { identifier }
      NumberVal:  string [NumberMax];  { integer / float number }
      StringVal:  string [StringMax];  { string (without quotes) }
      CharVal:    char;                { character value }

{--------------------------------------------------------------------------}

Procedure GetSymbol;                    { get a symbol to variable 'sy' }

{$IFDEF PASCAL}
Procedure ConvControlCharacters;        { control characters }
Procedure ConvDirective;                { directives }
Procedure ConvClassDirective;           { class directives }
{$ENDIF}

Procedure CheckSymbol (par: TSymbol);   { check sy=par and get next symbol }
Function  SymbolToString: string;       { convert current symbol to string }

{--------------------------------------------------------------------------}

Procedure OpenUnit (p_file_name, p_defines: string); { open source file  }
Procedure CloseUnit;

Procedure OpenString (p_text, p_defines: string);    { read source from string }
Procedure CloseString;

{$IFDEF FPC}
Function CompareStr (const a, b: string): integer;
{$ENDIF}

IMPLEMENTATION

(**************************** COMPARE STRINGS *****************************)

{$IFDEF FPC}
Function CompareStr (const a, b: string): integer;
Begin
     if a < b then result := -1
     else if a > b then result := 1
     else result := 0;
End;
{ CompareStr v FPC obsahuje chybu }
{$ENDIF}

(**************************** LEXICAL ANALYSIS ****************************)

Type  KeyStr = string;
      KeyRec = record t: KeyStr; s: TSymbol; end;

{$IFDEF PASCAL}

Const PasKeyMax = 66;

Const PasKeyTab: array [1..PasKeyMax] of KeyRec =
      (( t:'AND'              ; s:AndSy              ),
       ( t:'ARRAY'            ; s:ArraySy            ),
       ( t:'AS'               ; s:AsSy               ),
       ( t:'ASM'              ; s:AsmSy              ),
       ( t:'BEGIN'            ; s:BeginSy            ),
       ( t:'CASE'             ; s:CaseSy             ),
       ( t:'CLASS'            ; s:ClassSy            ),
       ( t:'CONST'            ; s:ConstSy            ),
       ( t:'CONSTRUCTOR'      ; s:ConstructorSy      ),
       ( t:'DESTRUCTOR'       ; s:DestructorSy       ),
       ( t:'DISPINTERFACE'    ; s:DispinterfaceSy    ),
       ( t:'DIV'              ; s:DivSy              ),
       ( t:'DO'               ; s:DoSy               ),
       ( t:'DOWNTO'           ; s:DowntoSy           ),
       ( t:'ELSE'             ; s:ElseSy             ),
       ( t:'END'              ; s:EndSy              ),
       ( t:'EXCEPT'           ; s:ExceptSy           ),
       ( t:'EXPORTS'          ; s:ExportsSy          ),
       ( t:'FILE'             ; s:FileSy             ),
       ( t:'FINALIZATION'     ; s:FinalizationSy     ),
       ( t:'FINALLY'          ; s:FinallySy          ),
       ( t:'FOR'              ; s:ForSy              ),
       ( t:'FUNCTION'         ; s:FunctionSy         ),
       ( t:'GOTO'             ; s:GotoSy             ),
       ( t:'IF'               ; s:IfSy               ),
       ( t:'IMPLEMENTATION'   ; s:ImplementationSy   ),
       ( t:'IN'               ; s:InSy               ),
       ( t:'INHERITED'        ; s:InheritedSy        ),
       ( t:'INITIALIZATION'   ; s:InitializationSy   ),
       ( t:'INLINE'           ; s:InlineSy           ),
       ( t:'INTERFACE'        ; s:InterfaceSy        ),
       ( t:'IS'               ; s:IsSy               ),
       ( t:'LABEL'            ; s:LabelSy            ),
       ( t:'LIBRARY'          ; s:LibrarySy          ),
       ( t:'MOD'              ; s:ModSy              ),
       ( t:'NIL'              ; s:NilSy              ),
       ( t:'NOT'              ; s:NotSy              ),
       ( t:'OBJECT'           ; s:ObjectSy           ),
       ( t:'OF'               ; s:OfSy               ),
       ( t:'ON'               ; s:OnSy               ),
       ( t:'OR'               ; s:OrSy               ),
       ( t:'OUT'              ; s:OutSy              ),
       ( t:'PACKED'           ; s:PackedSy           ),
       ( t:'PROCEDURE'        ; s:ProcedureSy        ),
       ( t:'PROGRAM'          ; s:ProgramSy          ),
       ( t:'PROPERTY'         ; s:PropertySy         ),
       ( t:'RAISE'            ; s:RaiseSy            ),
       ( t:'RECORD'           ; s:RecordSy           ),
       ( t:'REPEAT'           ; s:RepeatSy           ),
       ( t:'RESOURCESTRING'   ; s:ResourcestringSy   ),
       ( t:'SET'              ; s:SetSy              ),
       ( t:'SHL'              ; s:ShlSy              ),
       ( t:'SHR'              ; s:ShrSy              ),
       ( t:'STRING'           ; s:StringSy           ),
       ( t:'THEN'             ; s:ThenSy             ),
       ( t:'THREADVAR'        ; s:ThreadvarSy        ),
       ( t:'TO'               ; s:ToSy               ),
       ( t:'TRY'              ; s:TrySy              ),
       ( t:'TYPE'             ; s:TypeSy             ),
       ( t:'UNIT'             ; s:UnitSy             ),
       ( t:'UNTIL'            ; s:UntilSy            ),
       ( t:'USES'             ; s:UsesSy             ),
       ( t:'VAR'              ; s:VarSy              ),
       ( t:'WHILE'            ; s:WhileSy            ),
       ( t:'WITH'             ; s:WithSy             ),
       ( t:'XOR'              ; s:XorSy              ));

{$ENDIF}

{$IFDEF CPP}

Const CppKeyMax = 48;

Const CppKeyTab: array [1..CppKeyMax] of KeyRec =
      (( t:'asm'      ; s:AsmSy      ),
       ( t:'auto'     ; s:AutoSy     ),
       ( t:'break'    ; s:BreakSy    ),
       ( t:'case'     ; s:CaseSy     ),
       ( t:'catch'    ; s:CatchSy    ),
       ( t:'char'     ; s:CharSy     ),
       ( t:'class'    ; s:ClassSy    ),
       ( t:'const'    ; s:ConstSy    ),
       ( t:'continue' ; s:ContinueSy ),
       ( t:'default'  ; s:DefaultSy  ),
       ( t:'delete'   ; s:DeleteSy   ),
       ( t:'do'       ; s:DoSy       ),
       ( t:'double'   ; s:DoubleSy   ),
       ( t:'else'     ; s:ElseSy     ),
       ( t:'enum'     ; s:EnumSy     ),
       ( t:'extern'   ; s:ExternSy   ),
       ( t:'float'    ; s:FloatSy    ),
       ( t:'for'      ; s:ForSy      ),
       ( t:'friend'   ; s:FriendSy   ),
       ( t:'goto'     ; s:GotoSy     ),
       ( t:'if'       ; s:IfSy       ),
       ( t:'inline'   ; s:InlineSy   ),
       ( t:'int'      ; s:IntSy      ),
       ( t:'long'     ; s:LongSy     ),
       ( t:'new'      ; s:NewSy      ),
       ( t:'operator' ; s:OperatorSy ),
       ( t:'private'  ; s:PrivateSy  ),
       ( t:'protected'; s:ProtectedSy),
       ( t:'public'   ; s:PublicSy   ),
       ( t:'register' ; s:RegisterSy ),
       ( t:'return'   ; s:ReturnSy   ),
       ( t:'short'    ; s:ShortSy    ),
       ( t:'signed'   ; s:SignedSy   ),
       ( t:'sizeof'   ; s:SizeofSy   ),
       ( t:'static'   ; s:StaticSy   ),
       ( t:'struct'   ; s:StructSy   ),
       ( t:'switch'   ; s:SwitchSy   ),
       ( t:'template' ; s:TemplateSy ),
       ( t:'this'     ; s:ThisSy     ),
       ( t:'throw'    ; s:ThrowSy    ),
       ( t:'try'      ; s:TrySy      ),
       ( t:'typedef'  ; s:TypedefSy  ),
       ( t:'union'    ; s:UnionSy    ),
       ( t:'unsigned' ; s:UnsignedSy ),
       ( t:'virtual'  ; s:VirtualSy  ),
       ( t:'void'     ; s:VoidSy     ),
       ( t:'volatile' ; s:VolatileSy ),
       ( t:'while'    ; s:WhileSy    ));

{$ENDIF}

Procedure GetIdent;
Var   len: integer;
      a, b, c: integer;
      cmp: integer;
      tmp: string;
Begin
     len := 1;
     if StoreUpperCase then IdentVal [len] := UpCase (InpCh)
                       else IdentVal [len] := InpCh;
     GetCh;

     while InpCh in lod do begin
        inc (len);
        if len > IdentMax then Error ('Identifier too long');
        if StoreUpperCase then IdentVal [len] := UpCase (InpCh)
                          else IdentVal [len] := InpCh;
        GetCh;
     end;

     IdentVal [0] := chr (len);
     sy := IdentSy;

     tmp := IdentVal;
     if pascal and CompareUpperCase then tmp := UpperCase (tmp);

     {$IFDEF PASCAL}
     if pascal then begin
        a := 1;                               { RESERWED WORD }
        b := PasKeyMax;
        while a<=b do begin
           c := (a+b) shr 1; { a <= c < b }
           cmp := CompareStr (tmp, PasKeyTab[c].t);
           if cmp < 0 then b := c-1
           else if cmp > 0 then a := c+1
           else begin sy := PasKeyTab[c].s; a := b+1; end;
        end;
     end;
     {$ENDIF}

     {$IFDEF CPP}
     if cpp then begin
        a := 1;                               { RESERWED WORD }
        b := CppKeyMax;
        while a<=b do begin
           c := (a+b) shr 1; { a <= c < b }
           cmp := CompareStr (tmp, CppKeyTab[c].t);
           if cmp < 0 then b := c-1
           else if cmp > 0 then a := c+1
           else begin sy := CppKeyTab[c].s; a := b+1; end;
        end;
     end;
     {$ENDIF}
End;

{--------------------------------- Number ---------------------------------}

Var num_len: integer;
    flt:     boolean;

Procedure Store; { store one character to 'NumberVal' }
Begin
     inc (num_len);
     if num_len > NumberMax then Error ('Number is too long');
     NumberVal [num_len] := UpCase (InpCh);
     GetCh;
End;

Procedure Digits;  { digit <digit> }
Begin
     if not (InpCh in digit) then Error ('Digit expected');
     while InpCh in digit do Store;
End;

{$IFDEF PASCAL}

Procedure GetNumber;
Begin
     flt := false;
     num_len := 0;
     Digits;                                     { digit <digit> }

     if InpCh='.' then begin                     { '.' digit <digit> }
        Store;
        if InpCh='.' then begin                  { number and '..' }
           GetCh;
           dec (num_len);
           range := true;
        end
        else begin
           flt := true;
           Digits;
        end;
     end;

     if not range then                           { 'E' ['+'|'-'] digit <digit>}
        if (InpCh='E') or (InpCh='e') then begin
           flt := true;
           Store;
           if (InpCh='+') or (InpCh='-') then Store;
           Digits;
        end;

     { set length }
     NumberVal [0] := chr (num_len);

     if flt then sy := FltSy                     { floating point number }
            else sy := NumSy;                    { integer number }
End;

Procedure GetHexNumber;
Begin
     num_len := 0;
     Store; { store '$' }
     if not (InpCh in HexDigit) then Error ('Hexadecimal digit expected');
     while InpCh in HexDigit do Store;
     NumberVal [0] := chr (num_len);

     sy := NumSy;
End;

{$ENDIF}

{--------------------------------------------------------------------------}

{$IFDEF CPP}

Procedure Suffix (c1, c2: char);
Begin
     if UpCase (InpCh) = c1 then begin
        Store;
        if UpCase (InpCh) = c2 then Store;
     end
     else if UpCase (InpCh) = c2 then begin
        Store;
        if UpCase (InpCh) = c1 then Store;
     end;
End;

Procedure Remainder;
Begin
     if (InpCh='E') or (InpCh='e') then begin    { 'E' ['+'|'-'] digit <digit>}
        flt := true;
        Store;
        if (InpCh='+') or (InpCh='-') then Store;
        Digits;
     end;

     if flt then Suffix ('F', 'L')
            else Suffix ('L', 'U');

     { set length }
     NumberVal [0] := chr (num_len);

     if flt then sy := FltSy                     { floating point number }
            else sy := NumSy;                    { integer number }
End;

Procedure GetCppNumber;
Begin
     flt := false;
     num_len := 0;

     if InpCh = '0' then begin
        Store;
        if (InpCh='x') or (InpCh='X') then begin
           Store;
           if not (InpCh in HexDigit) then Error ('Hexadecimal digit expected');
           while InpCh in HexDigit do Store;
        end;
     end
     else Digits;                                { digit <digit> }

     if InpCh='.' then begin                     { '.' <digit> }
        Store;
        flt := true;
        while InpCh in Digit do Digits;
     end;

     Remainder;
End;

Procedure GetCppFraction;
Begin
     flt := true;
     NumberVal[1] := '.';
     num_len := 1;

     while InpCh in Digit do Digits;
     Remainder;
End;

{$ENDIF}

{--------------------------------- String ---------------------------------}

Var str_len: integer;

Procedure StoreCh (par: char);
Begin
     inc (str_len);
     if str_len > StringMax then Error ('String too long');
     StringVal[str_len] := par;
End;

{$IFDEF PASCAL}

Procedure GetString;
Var  n: integer;
     t: char;
Begin
     str_len := 0;

     while InpCh in [quote1, '#', '^'] do begin

        if InpCh = quote1 then begin
           repeat
              repeat
                 GetCh;
                 if InpCh = lf then
                    Error ('String exceeds line');
                 StoreCh (InpCh);
              until InpCh = quote1;
              GetCh;
           until InpCh <> quote1;
           dec (str_len);
        end

        else if InpCh = '#' then begin
           GetCh; { skip # }

           if InpCh = '$' then begin
              GetCh; { skip '$' }
              if not (InpCh in HexDigit) then
                 Error ('Hexadecimal digit expected');
              n := 0;
              while InpCh in HexDigit do begin
                 t := UpCase (InpCh);
                 if t >= 'A' then n := n*16 + ord (t) - ord ('A') + 10
                             else n := n*16 + ord (t) - ord ('0');
                 // if n > 255 then Error ('Bad character code');
                 GetCh;
              end;
           end

           else begin
              if not (InpCh in digit) then Error ('Digit expected');
              n := 0;
              while InpCh in digit do begin
                 n := n*10 + ord (InpCh) - ord ('0');
                 // if n > 255 then Error ('Bad character code');
                 GetCh;
              end;
           end;

           StoreCh (chr (n));
        end

        else begin
           GetCh; { skip ^ }
           n := ord (InpCh) - 64;
           if (n < 0) or (n > 31) then Error ('Bad control character');
           GetCh; { skip character }
           StoreCh (chr (n));
        end;

     end; {while}

     { set length }
     StringVal [0] := chr (str_len);

     sy := StrSy;
End;

{$ENDIF}

{--------------------------------------------------------------------------}

{$IFDEF CPP}

Function CppCharacter: char;
{ read one C-style character }
Var  n, d, cnt: integer;
     last: char;
Begin
     if InpCh <> backslash then begin         { simple character }
        result := InpCh;
        GetCh ();
     end
     else begin                               { escape sequence }
        GetCh ();                             { skip backslash }

        if (InpCh >= '0') and (InpCh <= '7') then begin { octal }
           n := 0;
           cnt := 1;
           while (InpCh >= '0') and (InpCh <= '7') and (cnt<=3) do begin
              n := n*8 + ord (InpCh) - ord ('0');
              inc (cnt);
              GetCh ();
           end;
           result := chr (n);
        end

        else if (InpCh ='x') or (InpCh = 'X') then begin { hex }
           GetCh ();
           n := 0;
           while InpCh in HexDigit do begin
               InpCh := UpCase (InpCh);
               if InpCh >= 'A' then d := ord (InpCh) - ord ('A') + 10
                               else d := ord (InpCh) - ord ('0');
              n := n*16 + d;
              GetCh ();
           end;
           result := chr (n);
        end

        else begin
           last := InpCh;
           GetCh ();
           case InpCh of
              'a': result := ^G;
              'b': result := ^H;
              'f': result := ^L;
              'n': result := ^J;
              'r': result := ^M;
              't': result := ^I;
              'v': result := ^K;

              quote1:    result := last;
              quote2:    result := last;
              backslash: result := last;
              '?':       result := last;

              else       result := last;
           end;
        end;
     end;
End;

Procedure GetCppString;
Begin
     GetCh (); { skip quote }
     str_len := 0;

     while InpCh <> quote2 do begin
         if InpCh = lf then Error ('String exceeds line');
         StoreCh (CppCharacter ());
     end;

     GetCh; { skip quote }

     { set length }
     StringVal [0] := chr (str_len);

     sy := StrSy;
End;

Procedure GetCppCharacter;
Begin
     GetCh (); { skip quote }

     if (InpCh = quote1) or (InpCh = lf) then
        Error ('Bad character constant');

     CharVal := CppCharacter ();

     if InpCh <> quote1 then
        Error ('Bad character constant');

     GetCh; { skip quote }

     sy := ChrSy;
End;

{$ENDIF}

{--------------------------------------------------------------------------}

Procedure Select2 (first: TSymbol; key: char; second: TSymbol);
Begin
     if InpCh <> key then sy := first
                  else begin GetCh; sy:=second; end;
End;

Procedure Select3 (first: TSymbol; key2: char; second: TSymbol;
                                   key3: char; third: TSymbol);
Begin
     if InpCh = key2 then begin GetCh; sy := second end
     else if InpCh = key3 then begin GetCh; sy := third end
     else sy := first;
End;

Procedure Select3e (first: TSymbol; key2: char; second: TSymbol;
                                    key3: char; third: TSymbol;
                                    key4: char; fourth: TSymbol);
Begin
     if InpCh = key2 then begin GetCh; sy := second end
     else if InpCh = key3 then begin
        GetCh;
        if InpCh <> key4 then sy := third
                         else begin GetCh; sy := fourth end
     end
     else sy := first;
End;

Procedure Select4e (first: TSymbol; key2: char; second: TSymbol;
                                    key3: char; third: TSymbol;
                                    key4: char; fourth: TSymbol;
                                    key5: char; fifth: TSymbol);
Begin
     if InpCh = key2 then begin GetCh; sy := second end
     else if InpCh = key3 then begin GetCh; sy := third end
     else if InpCh = key4 then begin
        GetCh;
        if InpCh <> key5 then sy := fourth
                         else begin GetCh; sy := fifth end
     end
     else sy := first;
End;

{--------------------------------------------------------------------------}

{$IFDEF PASCAL}

Procedure GetPasSymbol;
Label start, again, stop;
Var   dir: boolean;
      old: char;
Begin
     start:

     { if range already set }
     if range then begin                             { '..' }
        sy := RangeSy;
        range := false;
        SymLoc := Inp.Loc;
        goto stop;
     end;

     again:

     while InpCh <= ' ' do GetCh;
     SymLoc := Inp.Loc;

     if InpCh = '(' then begin
        GetCh;  { skip '(' }
        if InpCh = '.' then begin
           GetCh;                                     { '(.' }
           sy := LBrackSy;
        end
        else if InpCh <> '*' then begin
           sy := LParSy;                              { '(' }
        end
        else begin
           GetCh; { skip '*' }                        { comment }

           dir := (InpCh = '$');
           if dir then InitDirective;

           old := InpCh;
           GetCh;

           while (old <> '*') or (InpCh <> ')') do begin
              if dir then StoreDirectiveCharacter (InpCh);
              old := InpCh;
              GetCh;
           end;
           GetCh; { skip ')' }

           if dir then PascalDirective;
           goto again;
        end;
     end

     else if InpCh = '{' then begin                   { comment }
        GetCh;
        dir := (InpCh = '$');
        if dir then InitDirective;

        while InpCh <> '}' do begin
           if dir then StoreDirectiveCharacter (InpCh);
           GetCh;
        end;
        GetCh;

        if dir then PascalDirective;
        goto again;
     end

     else if InpCh = '/' then begin
        GetCh;
        if InpCh <> '/' then begin                   { / }
           sy := SlashSy;
        end
        else begin
           GetCh; { skip / }
           while InpCh <> lf do GetCh;               { comment }
           GetCh; { skip lf }
           goto again;
        end;
     end

     else if InpCh in letter then GetIdent            { IDENTIFIER }
     else if InpCh in digit then GetNumber            { NUMBER }
     else if InpCh = '$' then GetHexNumber            { HEXADECIMAL NUMBER }
     else if InpCh in [quote1, '#'] then GetString    { STRING }

     else begin                                       { SPECIAL SYMBOLS }
        old := InpCh;
        GetCh;

        case old of
           '@': sy := AtSignSy;
           '+': sy := PlusSy;
           '-': sy := MinusSy;
           '*': sy := AsteriskSy;
           '/': sy := SlashSy;
           ',': sy := CommaSy;
           ';': sy := SemicolonSy;
           '[': sy := LBrackSy;
           ')': sy := RParSy;
           ']': sy := RBrackSy;
           '^': sy := ArrowSy;
           '=': sy := EqualSy;

           '.': select3 (PeriodSy,  '.', RangeSy, ')', RBrackSy);
           ':': select2 (ColonSy,   '=', AssignSy);
           '(': select2 (LParSy,    '.', LBrackSy);
           '>': select2 (GreaterSy, '=', GreaterEqualSy);
           '<': select3 (LessSy,    '=', LessEqualSy, '>', UnequalSy);

           else Error ('Unknown symbol');
        end;
     end;

     stop:
     if (Cond <> nil) and not Cond.CondInp then goto start;
End;

{$ENDIF}

{--------------------------------------------------------------------------}

{$IFDEF CPP}

Procedure GetCppSymbol;
Label start, stop;
Var   old: char;
Begin
     start:

     while InpCh <= ' ' do GetCh;                     { directive }
     SymLoc := Inp.Loc;

     if InpCh = '#' then begin
        InitDirective;
        GetCh; { skip # }

        while InpCh <> lf do begin
           StoreDirectiveCharacter (InpCh);
           old := InpCh;
           GetCh;
        end;

        GetCh; { skip lf }
        CppDirective;
        goto start;
     end

     else if InpCh = '/' then begin                   { '/' }
        GetCh;  { skip '/' }

        if InpCh = '/' then begin
           GetCh; { skip / }
           while InpCh <> lf do GetCh;                { comment }
           GetCh; { skip lf }
           goto start;
        end

        else if InpCh = '*' then begin
           GetCh; { skip '*' }                        { comment }

           old := InpCh;
           GetCh;

           while (old <> '*') or (InpCh <> '/') do begin
              old := InpCh;
              GetCh;
           end;
           GetCh; { skip '/' }

           goto start;
        end

        else sy := SlashSy;                           { only '/' }
     end

     else if InpCh = '.' then begin                   { '.' }
        GetCh;
        if InpCh in Digit then                        { '.' digit }
           GetCppFraction
        else if InpCh = '.' then begin                { '.' '.' }
           GetCh;
           if InpCh <> '.' then Error ('Unknown symbol');
           GetCh;
           sy := DotsSy;
        end
        else if InpCh = '*' then begin                { '.' '*' }
           GetCh;
           sy := DotStarSy;
        end
        else sy := PeriodSy                           { only '.' }
     end

     else if InpCh in letter then GetIdent            { IDENTIFIER }
     else if InpCh in digit  then GetCppNumber        { NUMBER }
     else if InpCh = quote1  then GetCppCharacter     { CHARACTER }
     else if InpCh = quote2  then GetCppString        { STRING }

     else begin                                       { SPECIAL SYMBOLS }
        old := InpCh;
        GetCh;

        case old of
          '+': Select3 (PlusSy, '+', DPlusSy, '=', AddAssignSy);
          '-': Select4e (MinusSy, '-', DMinusSy, '=', SubAssignSy,
                         '>', ArrowSy, '*', ArrowStarSy);

          '*': Select2 (AsteriskSy, '=', MulAssignSy);
          '/': Select2 (SlashSy, '=', DivAssignSy);
          { '.': Select2 (PeriodSy, '*', DotStarSy); }
          ',': sy := CommaSy;
          ':': Select2 (ColonSy, ':', DColonSy);
          ';': sy := SemicolonSy;
          '(': sy := LParSy;
          ')': sy := RParSy;
          '[': sy := LBrackSy;
          ']': sy := RBrackSy;
          '{': sy := LBraceSy;
          '}': sy := RBraceSy;
          '^': Select2 (BarSy, '=', XorAssignSy);
          '=': Select2 (AssignSy, '=', EqualSy);
          '!': Select2 (LogNotSy, '=', UnequalSy);
          '%': Select2 (PercentSy, '=', ModAssignSy);
          '&': Select3 (AmpersandSy, '&', LogAndSy, '=', AndAssignSy);
          '|': Select3 (BarSy, '|', LogOrSy, '=', OrAssignSy);
          '~': sy := TildaSy;
          '?': sy := QuestionSy;
          '<': Select3e (LessSy, '=', LessEqualSy, '<', ShlSy, '=', ShlAssignSy);
          '>': Select3e (GreaterSy, '=', GreaterEqualSy, '>', ShrSy, '=', ShrAssignSy);

           else Error ('Unknown symbol');
        end;
     end;

     stop:
     if (Cond <> nil) and not Cond.CondInp then goto start;
End;

{$ENDIF}

{--------------------------------------------------------------------------}


Procedure GetSymbol;
Begin
     {$IFDEF PASCAL}
     if pascal then GetPasSymbol;
     {$ENDIF}

     {$IFDEF CPP}
     if cpp then GetCppSymbol;
     {$ENDIF}
End;

(*************************** CONTROL CHARACTERS ***************************)

{$IFDEF PASCAL}

Procedure ConvControlCharacters;
Var  n: integer;
Begin
     if sy = ArrowSy then begin
        n := ord (InpCh) - 64;
        if (n >= 0) and (n <= 31) then begin
           GetCh;
           if InpCh in [quote1, '#', '^'] then begin
              GetSymbol;
              if length (StringVal) = StringMax then
                 Error ('String too long');
              StringVal := chr (n) + StringVal;
           end
           else begin
              sy := StrSy;
              StringVal := chr (n);
           end;
        end;
     end;
End;

{$ENDIF}

(******************************* DIRECTIVES *******************************)

{$IFDEF PASCAL}

Const DirMax = 38;

Const DirTab: array [1..DirMax] of KeyRec =
      (( t:'ABSOLUTE'         ; s:AbsoluteSy         ),
       ( t:'ABSTRACT'         ; s:AbstractSy         ),
       ( t:'ASSEMBLER'        ; s:AssemblerSy        ),
       ( t:'AT'               ; s:AtSy               ),
       ( t:'AUTOMATED'        ; s:AutomatedSy        ),
       ( t:'CDECL'            ; s:CdeclSy            ),
       ( t:'DEFAULT'          ; s:DefaultSy          ),
       ( t:'DISPID'           ; s:DispidSy           ),
       ( t:'DYNAMIC'          ; s:DynamicSy          ),
       ( t:'EXPORT'           ; s:ExportSy           ),
       ( t:'EXTERNAL'         ; s:ExternalSy         ),
       ( t:'FAR'              ; s:FarSy              ),
       ( t:'FORWARD'          ; s:ForwardSy          ),
       ( t:'FRIEND'           ; s:FriendSy           ),
       ( t:'IMPLEMENTS'       ; s:ImplementsSy       ),
       ( t:'INDEX'            ; s:IndexSy            ),
       ( t:'MESSAGE'          ; s:MessageSy          ),
       ( t:'NAME'             ; s:NameSy             ),
       ( t:'NEAR'             ; s:NearSy             ),
       ( t:'NODEFAULT'        ; s:NodefaultSy        ),
       ( t:'OVERLOAD'         ; s:OverloadSy         ),
       ( t:'OVERRIDE'         ; s:OverrideSy         ),
       ( t:'PASCAL'           ; s:PascalSy           ),
       ( t:'PRIVATE'          ; s:PrivateSy          ),
       ( t:'PROTECTED'        ; s:ProtectedSy        ),
       ( t:'PUBLIC'           ; s:PublicSy           ),
       ( t:'PUBLISHED'        ; s:PublishedSy        ),
       ( t:'READ'             ; s:ReadSy             ),
       ( t:'READONLY'         ; s:ReadonlySy         ),
       ( t:'REGISTER'         ; s:RegisterSy         ),
       ( t:'REINTRODUCE'      ; s:ReintroduceSy      ),
       ( t:'RESIDENT'         ; s:ResidentSy         ),
       ( t:'SAFECALL'         ; s:SafecallSy         ),
       ( t:'STDCALL'          ; s:StdcallSy          ),
       ( t:'STORED'           ; s:StoredSy           ),
       ( t:'VIRTUAL'          ; s:VirtualSy          ),
       ( t:'WRITE'            ; s:WriteSy            ),
       ( t:'WRITEONLY'        ; s:WriteonlySy        ));

Function FindDirective: TSymbol;
Var  a, b, c: integer;
     cmp: integer;
     tmp: string;
Begin
     tmp := IdentVal;
     if CompareUpperCase then tmp := UpperCase (tmp);

     a := 1;
     b := DirMax;
     FindDirective := IdentSy;

     while a<=b do begin
        c := (a+b) shr 1; { a <= c < b }
        cmp := CompareStr (tmp, DirTab[c].t);
        if cmp < 0 then b := c-1
        else if cmp > 0 then a := c+1
        else begin FindDirective := DirTab[c].s; a:=b+1; end;
     end;
End;

Procedure ConvDirective;
Begin
     if sy = IdentSy then
        sy := FindDirective;
End;

Procedure ConvClassDirective;
Var  tmp: TSymbol;
Begin
     if sy = IdentSy then begin
        tmp := FindDirective;
        if tmp in [AutomatedSy, PrivateSy,
                   ProtectedSy, PublicSy, PublishedSy,
                   FriendSy]
           then sy := tmp;
     end;
End;

{$ENDIF}

(************************** CHECK CURRENT SYMBOL **************************)

Type  SpecStr = string [3];
      SpecRec = record t: SpecStr; s: TSymbol; end;

{$IFDEF PASCAL}

Const PasSpecMax = 22;

Const PasSpecTab: array [1..PasSpecMax] of SpecRec =
      (( t: '@' ; s: AtSignSy       ),
       ( t: '+' ; s: PlusSy         ),
       ( t: '-' ; s: MinusSy        ),
       ( t: '*' ; s: AsteriskSy     ),
       ( t: '/' ; s: SlashSy        ),
       ( t: '.' ; s: PeriodSy       ),
       ( t: ',' ; s: CommaSy        ),
       ( t: ':' ; s: ColonSy        ),
       ( t: ';' ; s: SemicolonSy    ),
       ( t: '=' ; s: EqualSy        ),
       ( t: '<' ; s: LessSy         ),
       ( t: '>' ; s: GreaterSy      ),
       ( t: '<>'; s: UnequalSy      ),
       ( t: '<='; s: LessEqualSy    ),
       ( t: '>='; s: GreaterEqualSy ),
       ( t: '^' ; s: ArrowSy        ),
       ( t: '..'; s: RangeSy        ),
       ( t: ':='; s: AssignSy       ),
       ( t: '(' ; s: LParSy         ),
       ( t: ')' ; s: RParSy         ),
       ( t: '[' ; s: LBrackSy       ),
       ( t: ']' ; s: RBrackSy       ));

{$ENDIF}

{$IFDEF CPP}

Const CppSpecMax = 49;

Const CppSpecTab: array [1..CppSpecMax] of SpecRec =
(( t: '+'   ; s: PlusSy         ),
 ( t: '-'   ; s: MinusSy        ),
 ( t: '*'   ; s: AsteriskSy     ),
 ( t: '/'   ; s: SlashSy        ),
 ( t: '.'   ; s: PeriodSy       ),
 ( t: ','   ; s: CommaSy        ),
 ( t: ':'   ; s: ColonSy        ),
 ( t: ';'   ; s: SemicolonSy    ),
 ( t: '=='  ; s: EqualSy        ),
 ( t: '<'   ; s: LessSy         ),
 ( t: '>'   ; s: GreaterSy      ),
 ( t: '!='  ; s: UnEqualSy      ),
 ( t: '<='  ; s: LessEqualSy    ),
 ( t: '>='  ; s: GreaterEqualSy ),
 ( t: '->'  ; s: ArrowSy        ),
 ( t: '='   ; s: AssignSy       ),
 ( t: '('   ; s: LParSy         ),
 ( t: ')'   ; s: RParSy         ),
 ( t: '['   ; s: LBrackSy       ),
 ( t: ']'   ; s: RBrackSy       ),
 ( t: '{'   ; s: LBraceSy       ),
 ( t: '}'   ; s: RBraceSy       ),
 ( t: '~'   ; s: TildaSy        ),
 ( t: '%'   ; s: PercentSy      ),
 ( t: '^'   ; s: CaretSy        ),
 ( t: '&'   ; s: AmpersandSy    ),
 ( t: '|'   ; s: BarSy          ),
 ( t: '?'   ; s: QuestionSy     ),
 ( t: '++'  ; s: DPlusSy        ),
 ( t: '--'  ; s: DMinusSy       ),
 ( t: '::'  ; s: DColonSy       ),
 ( t: '...' ; s: DotsSy         ),
 ( t: '.*'  ; s: DotStarSy      ),
 ( t: '->*' ; s: ArrowStarSy    ),
 ( t: '<<'  ; s: ShlSy          ),
 ( t: '>>'  ; s: ShrSy          ),
 ( t: '!'   ; s: LogNotSy       ),
 ( t: '&&'  ; s: LogAndSy       ),
 ( t: '||'  ; s: LogOrSy        ),
 ( t: '*='  ; s: MulAssignSy    ),
 ( t: '/='  ; s: DivAssignSy    ),
 ( t: '%='  ; s: ModAssignSy    ),
 ( t: '+='  ; s: AddAssignSy    ),
 ( t: '-='  ; s: SubAssignSy    ),
 ( t: '<<=' ; s: ShlAssignSy    ),
 ( t: '>>=' ; s: ShrAssignSy    ),
 ( t: '&='  ; s: AndAssignSy    ),
 ( t: '|='  ; s: OrAssignSy     ),
 ( t: '^='  ; s: XorAssignSy    ));

{$ENDIF}

Procedure MissingSymbol (par: TSymbol);
Var  i:   integer;
     msg: string;
Begin
     { vyhledej textovou reprezentaci ocekavaneho symbolu }
     msg := '';

     {$IFDEF PASCAL}
     if pascal then begin
        for i := 1 to PasKeyMax do
           if PasKeyTab[i].s = par then msg := PasKeyTab[i].t;

        for i := 1 to DirMax do
           if DirTab[i].s = par then msg := DirTab[i].t;

        for i := 1 to PasSpecMax do
           if PasSpecTab[i].s = par then msg := '"' + PasSpecTab[i].t + '"';
     end;
     {$ENDIF}

     {$IFDEF CPP}
     if cpp then begin
        for i := 1 to CppKeyMax do
           if CppKeyTab[i].s = par then msg := CppKeyTab[i].t;

        for i := 1 to CppSpecMax do
           if CppSpecTab[i].s = par then msg := '"' + CppSpecTab[i].t + '"';
     end;
     {$ENDIF}

     Error (msg + ' expected');
End;

Procedure VerifySymbol (par: TSymbol);
Begin
     { ohlaseni chyby pokud sy <> par }
     if sy <> par then MissingSymbol (par);
End;

Procedure CheckSymbol (par: TSymbol);
Begin
     if sy <> par then MissingSymbol (par);
     GetSymbol; { skip symbol }
End;

(**************************** SYMBOL TO STRING ****************************)

Function SymbolToString: string;
{ Prevod symbolu na retezec znaku - pouze pro ladeni }
Begin
     {$IFDEF TYPINFO}
        result := TypInfo.GetEnumName (typeinfo (TSymbol), ord (sy));
     {$ELSE}
        result := 'TSymbol (' + IntToStr (ord (sy)) + ')';
     {$ENDIF}

     case sy of
        IdentSy: result := result + ' (' + IdentVal  + ')';
        NumSy:   result := result + ' (' + NumberVal + ')';
        FltSy:   result := result + ' (' + NumberVal + ')';
        StrSy:   result := result + ' (' + StringVal + ')';
     end;
End;

(****************************** CHECK TABLES ******************************)

{$IFNDEF CONV}
Procedure CheckTables;
Var  i: integer;
     tmp: set of TSymbol;

     procedure check (s: TSymbol);
     begin
          {$IFNDEF PASCAL_AND_CPP}
             Assert (not (s in tmp));
          {$ENDIF}
          Include (tmp, s);
     end;

// Var  k: TSymbol;
Begin
     { kontrola usporadani tabulek }
     {$IFDEF PASCAL}
     for i := 1 to PasKeyMax-1 do
        Assert (PasKeyTab[i].t < PasKeyTab[i+1].t);

     for i := 1 to DirMax-1 do
        Assert (DirTab[i].t < DirTab[i+1].t);
     {$ENDIF}

     {$IFDEF CPP}
     for i := 1 to CppKeyMax-1 do
        Assert (CppKeyTab[i].t < CppKeyTab[i+1].t);
     {$ENDIF}


     { kontrola uplnosti tabulek }
     tmp := [];

     {$IFDEF PASCAL}
     for i := 1 to PasKeyMax  do check (PasKeyTab[i].s);
     for i := 1 to DirMax     do check (DirTab[i].s);
     for i := 1 to PasSpecMax do check (PasSpecTab[i].s);
     check (IdentSy);
     check (NumSy);
     check (FltSy);
     check (StrSy);
     check (NoSy);
     {$ENDIF}

     {$IFDEF CPP}
     for i := 1 to CppKeyMax  do check (CppKeyTab[i].s);
     for i := 1 to CppSpecMax do check (CppSpecTab[i].s);
     check (IdentSy);
     check (NumSy);
     check (FltSy);
     check (StrSy);
     check (ChrSy);
     check (EosSy);
     check (NoSy);
     {$ENDIF}

     (*
     for k := low (TSymbol) to high (TSymbol) do
        if not (k in tmp) then
           write (ord (k), ' not in table');
     *)

     Assert (tmp = [low (TSymbol) .. high (TSymbol)], 'Invalid tables');
End;
{$ENDIF}

(*************************** OPEN / CLOSE FILES ***************************)

Procedure OpenUnit (p_file_name, p_defines: string);
Begin
     StartDir (p_defines);
     OpenSrc (p_file_name);
End;

Procedure CloseUnit;
Begin
     CloseSrc;
End;

Procedure OpenString (p_text, p_defines: string);
Begin
     StartDir (p_defines);
     OpenStr (p_text);
End;

Procedure CloseString;
Begin
     CloseStr;
End;

(********************************* CLEAR **********************************)

Procedure StartLex;
{ Start new unit }
Begin
     sy := NoSy;      { important }
     range := false;  { important }

     IdentVal := '';  { not necessary }
     NumberVal := ''; { not necessary }
     StringVal := ''; { not necessary }

     num_len := 0;     { not necessary }
     str_len := 0;     { not necessary }
End;

{$IFNDEF CONV}
BEGIN
     CheckTables;
{$ENDIF}
END.

