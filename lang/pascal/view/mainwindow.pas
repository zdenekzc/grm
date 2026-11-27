unit MainWindow;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Forms, Controls, Graphics, Dialogs, StdCtrls, ExtCtrls,
  Buttons, ComCtrls, Menus, RTTIGrids, RTTICtrls,
  SynHighlighterPas, SynEdit, uPSComponent;

type

  { TMainForm }

  TMainForm = class(TForm)
    MainMenu: TMainMenu;
    FileMenu: TMenuItem;
    EditMenu: TMenuItem;
    CompileMenu: TMenuItem;
    Info: TMemo;
    RunMenuItem: TMenuItem;
    MenuSeparator: TMenuItem;
    OpenMenuItem: TMenuItem;
    CentralPanel: TPanel;
    Edit: TSynEdit;
    PascalSyntax: TSynPasSyn;
    HorizontalSplitter: TSplitter;
    TabControl: TPageControl;
    Script: TPSScript;
    SaveMenuItem: TMenuItem;
    QuitMenuItem: TMenuItem;
    OpenDialog: TOpenDialog;
    SaveDialog: TSaveDialog;
    LeftSplitter: TSplitter;
    RightSplitter: TSplitter;
    StatusBar: TStatusBar;
    EditPage: TTabSheet;
    PropertyGrid: TTIPropertyGrid;
    TreeView: TTreeView;

    procedure OpenMenuItemClick(Sender: TObject);
    procedure QuitMenuItemClick(Sender: TObject);
    procedure RunMenuItemClick(Sender: TObject);
    procedure SaveMenuItemClick(Sender: TObject);

  private
    procedure AddPage (title: string; control: TControl);

  public

  end;

var
  MainForm: TMainForm;

implementation

{$R *.lfm}

uses
uPSCompiler,
uPSR_std,
uPSC_std,
uPSR_classes,
uPSC_classes,
uPSC_controls,
uPSR_controls,
uPSC_forms,
uPSR_forms,
uPSRuntime,
uPSDisassembly,
uPSR_dateutils,
uPSC_dateutils,
uPSR_dll,
uPSC_dll;

// http://wiki.freepascal.org/Pascal_Script_Examples

{ TMainForm }

procedure TMainForm.AddPage(title: string; control: TControl);
var  page: TTabSheet;
begin
     page := TabControl.AddTabSheet;
     page.Caption := title;
     page.InsertControl (control);
     control.Align := alClient;
     TabControl.ActivePage := page;
end;

procedure TMainForm.OpenMenuItemClick(Sender: TObject);
var  fileName: string;
     editor : TSynEdit;
begin
  if OpenDialog.Execute then begin
     fileName := OpenDialog.FileName;
     editor := TSynEdit.Create (self);
     editor.Lines.LoadFromFile (fileName);
     addPage (fileNAme, editor);
  end;
end;

procedure TMainForm.SaveMenuItemClick(Sender: TObject);
begin
  if SaveDialog.Execute then begin

  end;
end;


procedure TMainForm.QuitMenuItemClick(Sender: TObject);
begin
     close;
end;


procedure ShowInfo (txt: string);
begin
     MainForm.Info.Append (txt);
end;

procedure TMainForm.RunMenuItemClick(Sender: TObject);
var  ok : boolean;
     i: integer;
     data : string;
     txt: string;
     memo: TMemo;
begin
     Script.Script := Edit.Lines;
     ShowInfo (Edit.Lines.Text);
     // Script.AddFunction (@ShowInfo, 'procedure ShowInfo (txt: string)');
     ok := Script.Compile;
     for i := 0 to Script.CompilerMessageCount -1 do
         info.Append (Script.CompilerErrorToStr(i) );

     if ok then begin
        Script.GetCompiled(data);
        IFPS3DataToText (data, txt);
        memo := TMemo.Create (self);
        memo.Append(txt);
        AddPage ('instructions', memo);
        if Script.Execute then
           info.Append ('O.K.');
     end;
end;

end.
