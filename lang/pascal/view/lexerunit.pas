unit LexerUnit;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils;

type

{ Lexer }

 Lexer = class
     public
        procedure nextToken;

        function readIdentifier: string;
        function readNumber: string;
        function readChar: string;
        function readString: string;

        function mark: integer;
        procedure rewind (pos: integer);

        function testSymbols (a: array of byte): boolean;

     end;

type Output = class
     public
     end;

implementation

{ Lexer }

procedure Lexer.nextToken;
begin

end;

function Lexer.readIdentifier: string;
begin
     result := '';
end;

function Lexer.readNumber: string;
begin
     result := '';
end;

function Lexer.readChar: string;
begin
     result := '';
end;

function Lexer.readString: string;
begin
     result := '';
end;

function Lexer.mark: integer;
begin
     result := 0;
end;

procedure Lexer.rewind(pos: integer);
begin

end;

function Lexer.testSymbols(a: array of byte): boolean;
begin
     result := false;
end;

end.

