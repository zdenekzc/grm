namespace SharpView
{
    partial class MainWindow
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainWindow));
            this.mainMenu = new System.Windows.Forms.MenuStrip();
            this.fileMenu = new System.Windows.Forms.ToolStripMenuItem();
            this.openMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.separator1 = new System.Windows.Forms.ToolStripSeparator();
            this.quitMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.viewMenu = new System.Windows.Forms.ToolStripMenuItem();
            this.compileMenu = new System.Windows.Forms.ToolStripMenuItem();
            this.compileMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.statusBar = new System.Windows.Forms.StatusStrip();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.splitContainer2 = new System.Windows.Forms.SplitContainer();
            this.treeView = new System.Windows.Forms.TreeView();
            this.splitContainer3 = new System.Windows.Forms.SplitContainer();
            this.centralTabs = new System.Windows.Forms.TabControl();
            this.editorTab = new System.Windows.Forms.TabPage();
            this.editor = new System.Windows.Forms.TextBox();
            this.propGrid = new System.Windows.Forms.PropertyGrid();
            this.info = new System.Windows.Forms.TextBox();
            this.openDialog = new System.Windows.Forms.OpenFileDialog();
            this.saveDialog = new System.Windows.Forms.SaveFileDialog();
            this.mainMenu.SuspendLayout();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.splitContainer2.Panel1.SuspendLayout();
            this.splitContainer2.Panel2.SuspendLayout();
            this.splitContainer2.SuspendLayout();
            this.splitContainer3.Panel1.SuspendLayout();
            this.splitContainer3.Panel2.SuspendLayout();
            this.splitContainer3.SuspendLayout();
            this.centralTabs.SuspendLayout();
            this.editorTab.SuspendLayout();
            this.SuspendLayout();
            // 
            // mainMenu
            // 
            this.mainMenu.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileMenu,
            this.viewMenu,
            this.compileMenu});
            this.mainMenu.Location = new System.Drawing.Point(0, 0);
            this.mainMenu.Name = "mainMenu";
            this.mainMenu.Size = new System.Drawing.Size(1008, 24);
            this.mainMenu.TabIndex = 0;
            this.mainMenu.Text = "menuStrip1";
            // 
            // fileMenu
            // 
            this.fileMenu.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.openMenuItem,
            this.saveMenuItem,
            this.separator1,
            this.quitMenuItem});
            this.fileMenu.Name = "fileMenu";
            this.fileMenu.Size = new System.Drawing.Size(37, 20);
            this.fileMenu.Text = "&File";
            // 
            // openMenuItem
            // 
            this.openMenuItem.Name = "openMenuItem";
            this.openMenuItem.Size = new System.Drawing.Size(103, 22);
            this.openMenuItem.Text = "&Open";
            this.openMenuItem.Click += new System.EventHandler(this.open_Click);
            // 
            // saveMenuItem
            // 
            this.saveMenuItem.Name = "saveMenuItem";
            this.saveMenuItem.Size = new System.Drawing.Size(103, 22);
            this.saveMenuItem.Text = "&Save";
            this.saveMenuItem.Click += new System.EventHandler(this.save_Click);
            // 
            // separator1
            // 
            this.separator1.Name = "separator1";
            this.separator1.Size = new System.Drawing.Size(100, 6);
            // 
            // quitMenuItem
            // 
            this.quitMenuItem.Name = "quitMenuItem";
            this.quitMenuItem.Size = new System.Drawing.Size(103, 22);
            this.quitMenuItem.Text = "&Quit";
            this.quitMenuItem.Click += new System.EventHandler(this.quit_Click);
            // 
            // viewMenu
            // 
            this.viewMenu.Name = "viewMenu";
            this.viewMenu.Size = new System.Drawing.Size(44, 20);
            this.viewMenu.Text = "View";
            // 
            // compileMenu
            // 
            this.compileMenu.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.compileMenuItem});
            this.compileMenu.Name = "compileMenu";
            this.compileMenu.Size = new System.Drawing.Size(64, 20);
            this.compileMenu.Text = "Compile";
            // 
            // compileMenuItem
            // 
            this.compileMenuItem.Name = "compileMenuItem";
            this.compileMenuItem.ShortcutKeys = System.Windows.Forms.Keys.F9;
            this.compileMenuItem.Size = new System.Drawing.Size(138, 22);
            this.compileMenuItem.Text = "&Compile";
            this.compileMenuItem.Click += new System.EventHandler(this.compile_Click);
            // 
            // statusBar
            // 
            this.statusBar.Location = new System.Drawing.Point(0, 739);
            this.statusBar.Name = "statusBar";
            this.statusBar.Size = new System.Drawing.Size(1008, 22);
            this.statusBar.TabIndex = 1;
            this.statusBar.Text = "statusStrip1";
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.Location = new System.Drawing.Point(0, 24);
            this.splitContainer1.Name = "splitContainer1";
            this.splitContainer1.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.splitContainer2);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.info);
            this.splitContainer1.Size = new System.Drawing.Size(1008, 715);
            this.splitContainer1.SplitterDistance = 569;
            this.splitContainer1.TabIndex = 6;
            // 
            // splitContainer2
            // 
            this.splitContainer2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer2.Location = new System.Drawing.Point(0, 0);
            this.splitContainer2.Name = "splitContainer2";
            // 
            // splitContainer2.Panel1
            // 
            this.splitContainer2.Panel1.Controls.Add(this.treeView);
            // 
            // splitContainer2.Panel2
            // 
            this.splitContainer2.Panel2.Controls.Add(this.splitContainer3);
            this.splitContainer2.Size = new System.Drawing.Size(1008, 569);
            this.splitContainer2.SplitterDistance = 165;
            this.splitContainer2.TabIndex = 5;
            // 
            // treeView
            // 
            this.treeView.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.treeView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.treeView.Location = new System.Drawing.Point(0, 0);
            this.treeView.Name = "treeView";
            this.treeView.Size = new System.Drawing.Size(165, 569);
            this.treeView.TabIndex = 6;
            this.treeView.NodeMouseClick += new System.Windows.Forms.TreeNodeMouseClickEventHandler(this.treeView_NodeMouseClick);
            // 
            // splitContainer3
            // 
            this.splitContainer3.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer3.Location = new System.Drawing.Point(0, 0);
            this.splitContainer3.Name = "splitContainer3";
            // 
            // splitContainer3.Panel1
            // 
            this.splitContainer3.Panel1.Controls.Add(this.centralTabs);
            // 
            // splitContainer3.Panel2
            // 
            this.splitContainer3.Panel2.Controls.Add(this.propGrid);
            this.splitContainer3.Size = new System.Drawing.Size(839, 569);
            this.splitContainer3.SplitterDistance = 664;
            this.splitContainer3.TabIndex = 0;
            // 
            // centralTabs
            // 
            this.centralTabs.Controls.Add(this.editorTab);
            this.centralTabs.Dock = System.Windows.Forms.DockStyle.Fill;
            this.centralTabs.Location = new System.Drawing.Point(0, 0);
            this.centralTabs.Name = "centralTabs";
            this.centralTabs.SelectedIndex = 0;
            this.centralTabs.Size = new System.Drawing.Size(664, 569);
            this.centralTabs.TabIndex = 1;
            // 
            // editorTab
            // 
            this.editorTab.Controls.Add(this.editor);
            this.editorTab.Location = new System.Drawing.Point(4, 22);
            this.editorTab.Name = "editorTab";
            this.editorTab.Padding = new System.Windows.Forms.Padding(3);
            this.editorTab.Size = new System.Drawing.Size(656, 543);
            this.editorTab.TabIndex = 1;
            this.editorTab.Text = "Editor";
            this.editorTab.UseVisualStyleBackColor = true;
            // 
            // editor
            // 
            this.editor.Dock = System.Windows.Forms.DockStyle.Fill;
            this.editor.Location = new System.Drawing.Point(3, 3);
            this.editor.Multiline = true;
            this.editor.Name = "editor";
            this.editor.Size = new System.Drawing.Size(650, 537);
            this.editor.TabIndex = 0;
            this.editor.Text = resources.GetString("editor.Text");
            // 
            // propGrid
            // 
            this.propGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.propGrid.LineColor = System.Drawing.SystemColors.ControlDark;
            this.propGrid.Location = new System.Drawing.Point(0, 0);
            this.propGrid.Name = "propGrid";
            this.propGrid.Size = new System.Drawing.Size(171, 569);
            this.propGrid.TabIndex = 6;
            // 
            // info
            // 
            this.info.Dock = System.Windows.Forms.DockStyle.Fill;
            this.info.Location = new System.Drawing.Point(0, 0);
            this.info.Multiline = true;
            this.info.Name = "info";
            this.info.Size = new System.Drawing.Size(1008, 142);
            this.info.TabIndex = 0;
            // 
            // openDialog
            // 
            this.openDialog.FileName = "openFileDialog1";
            // 
            // MainWindow
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1008, 761);
            this.Controls.Add(this.splitContainer1);
            this.Controls.Add(this.statusBar);
            this.Controls.Add(this.mainMenu);
            this.MainMenuStrip = this.mainMenu;
            this.Name = "MainWindow";
            this.Text = "Sharp View";
            this.mainMenu.ResumeLayout(false);
            this.mainMenu.PerformLayout();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            this.splitContainer1.ResumeLayout(false);
            this.splitContainer2.Panel1.ResumeLayout(false);
            this.splitContainer2.Panel2.ResumeLayout(false);
            this.splitContainer2.ResumeLayout(false);
            this.splitContainer3.Panel1.ResumeLayout(false);
            this.splitContainer3.Panel2.ResumeLayout(false);
            this.splitContainer3.ResumeLayout(false);
            this.centralTabs.ResumeLayout(false);
            this.editorTab.ResumeLayout(false);
            this.editorTab.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }
        #endregion

        private System.Windows.Forms.MenuStrip mainMenu;
        private System.Windows.Forms.ToolStripMenuItem fileMenu;
        private System.Windows.Forms.ToolStripMenuItem quitMenuItem;
        private System.Windows.Forms.StatusStrip statusBar;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.SplitContainer splitContainer2;
        private System.Windows.Forms.TreeView treeView;
        private System.Windows.Forms.SplitContainer splitContainer3;
        private System.Windows.Forms.PropertyGrid propGrid;
        private System.Windows.Forms.TextBox info;
        private System.Windows.Forms.ToolStripMenuItem openMenuItem;
        private System.Windows.Forms.ToolStripMenuItem saveMenuItem;
        private System.Windows.Forms.OpenFileDialog openDialog;
        private System.Windows.Forms.SaveFileDialog saveDialog;
        private System.Windows.Forms.ToolStripMenuItem viewMenu;
        private System.Windows.Forms.TabControl centralTabs;
        private System.Windows.Forms.TabPage editorTab;
        private System.Windows.Forms.TextBox editor;
        private System.Windows.Forms.ToolStripMenuItem compileMenu;
        private System.Windows.Forms.ToolStripMenuItem compileMenuItem;
        private System.Windows.Forms.ToolStripSeparator separator1;
    }
}

