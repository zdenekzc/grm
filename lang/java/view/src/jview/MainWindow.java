package jview;

import java.lang.reflect.*;
import java.beans.*;

import java.io.*;
import java.util.*;

import java.net.*;
import javax.tools.*; // Compilation

import java.awt.*;
import java.awt.event.*;
import java.awt.datatransfer.*;
import java.awt.dnd.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.tree.*;
import javax.swing.table.*;

// import org.netbeans.lib.awtextra.*;

/*
import javax.media.j3d.*;
import javax.vecmath.*;
import com.sun.j3d.utils.geometry.*;
import com.sun.j3d.utils.universe.*;
import com.sun.j3d.utils.behaviors.mouse.*;
*/

import javax.swing.plaf.metal.MetalLookAndFeel;

// Windows: http://kmlinux.fjfi.cvut.cz/~culikzde/j3d/j3d-1_5_2-windows-amd64.zip

// Fedora: https://github.com/rpmsphere/x86_64/raw/master/j/java3d-1.5.2-15.x86_64.rpm
// dnf install vecmath
// Tools/Libraries ... Java 3D ... /usr/share/java ... vecmath.jar, java3d/j3dcore.jar, java3d/j3dutils.jar
// Project / Libraries / Add Library

public class MainWindow extends JFrame {

    DefaultTreeModel model;

    DefaultMutableTreeNode root;
    DefaultMutableTreeNode sceneBranch;
    DefaultMutableTreeNode designBranch;
    
    public MainWindow() {
        initComponents();

        // displayComponents();
        addTools ();
        addComponents ();
        addColors ();
        
        root = new DefaultMutableTreeNode ("Tree");
        sceneBranch = new DefaultMutableTreeNode ("3D Scene");
        designBranch = new DefaultMutableTreeNode ("2D Designer");
        root.add (sceneBranch);
        root.add (designBranch);
        model = new DefaultTreeModel (root);
        tree.setModel (model);
        tree.setTransferHandler (new TreeTransferHandler());

        DesignerDropListener listener = new DesignerDropListener ();
        DropTarget target = new DropTarget (designer, listener);
        designer.setDropTarget (target);

        /*        
        tree.setDragEnabled (true);
        tree.setDropMode (DropMode.ON_OR_INSERT);
        tree.setTransferHandler (new TreeTransferHandler());
        tree.getSelectionModel().setSelectionMode (TreeSelectionModel.CONTIGUOUS_TREE_SELECTION);
        expandTree (tree);
        */

        // compile ();
        // setupScene ();
    }

    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents()
    {

        jSplitPane1 = new javax.swing.JSplitPane();
        jSplitPane2 = new javax.swing.JSplitPane();
        jScrollPane2 = new javax.swing.JScrollPane();
        propTable = new javax.swing.JTable();
        centralTabs = new javax.swing.JTabbedPane();
        scene = new javax.swing.JPanel();
        designer = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        editor = new javax.swing.JTextArea();
        jScrollPane1 = new javax.swing.JScrollPane();
        tree = new javax.swing.JTree();
        toollBarTabs = new javax.swing.JTabbedPane();
        shapeToolBar = new javax.swing.JToolBar();
        componentToolBar = new javax.swing.JToolBar();
        colorToolBar = new javax.swing.JToolBar();
        mainMenu = new javax.swing.JMenuBar();
        fileMenu = new javax.swing.JMenu();
        quitMenu = new javax.swing.JMenuItem();
        editMenu = new javax.swing.JMenu();
        compileMenu = new javax.swing.JMenuItem();
        viewMenu = new javax.swing.JMenu();
        reflectionMenu = new javax.swing.JMenuItem();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);

        jSplitPane1.setDividerLocation(200);

        jSplitPane2.setDividerLocation(400);

        propTable.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][]
            {
                {null, null, null, null},
                {null, null, null, null},
                {null, null, null, null},
                {null, null, null, null}
            },
            new String []
            {
                "Title 1", "Title 2", "Title 3", "Title 4"
            }
        ));
        jScrollPane2.setViewportView(propTable);

        jSplitPane2.setRightComponent(jScrollPane2);

        javax.swing.GroupLayout sceneLayout = new javax.swing.GroupLayout(scene);
        scene.setLayout(sceneLayout);
        sceneLayout.setHorizontalGroup(
            sceneLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 394, Short.MAX_VALUE)
        );
        sceneLayout.setVerticalGroup(
            sceneLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 437, Short.MAX_VALUE)
        );

        /*
        centralTabs.addTab("3D Scene", scene);

        /designer.setLayout(new org.netbeans.lib.awtextra.AbsoluteLayout());
        centralTabs.addTab("2D Designer", designer);
        */

        editor.setColumns(20);
        editor.setRows(5);
        editor.setText("package testcompile;\n\npublic class HelloWorld \n{\n     public void doStuff () \n     {\n          System.out.println (\"Hello from editor\");\n      }\n}\n\n  "); // NOI18N
        jScrollPane3.setViewportView(editor);

        centralTabs.addTab("Editor", jScrollPane3);

        jSplitPane2.setLeftComponent(centralTabs);

        jSplitPane1.setRightComponent(jSplitPane2);

        tree.addTreeSelectionListener(new javax.swing.event.TreeSelectionListener()
        {
            public void valueChanged(javax.swing.event.TreeSelectionEvent evt)
            {
                treeValueChanged(evt);
            }
        });
        jScrollPane1.setViewportView(tree);

        jSplitPane1.setLeftComponent(jScrollPane1);

        shapeToolBar.setRollover(true);
        toollBarTabs.addTab("3D", shapeToolBar);

        componentToolBar.setRollover(true);
        toollBarTabs.addTab("2D", componentToolBar);

        colorToolBar.setRollover(true);
        toollBarTabs.addTab("Colors", colorToolBar);

        fileMenu.setMnemonic('F');
        fileMenu.setText("File");

        quitMenu.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_Q, java.awt.event.InputEvent.CTRL_DOWN_MASK));
        quitMenu.setMnemonic('Q');
        quitMenu.setText("Quit");
        quitMenu.addActionListener(new java.awt.event.ActionListener()
        {
            public void actionPerformed(java.awt.event.ActionEvent evt)
            {
                quitClick(evt);
            }
        });
        fileMenu.add(quitMenu);

        mainMenu.add(fileMenu);

        editMenu.setMnemonic('E');
        editMenu.setText("Edit");

        compileMenu.setMnemonic('C');
        compileMenu.setText("Compile");
        compileMenu.addActionListener(new java.awt.event.ActionListener()
        {
            public void actionPerformed(java.awt.event.ActionEvent evt)
            {
                compileClick(evt);
            }
        });
        editMenu.add(compileMenu);

        mainMenu.add(editMenu);

        viewMenu.setMnemonic('V');
        viewMenu.setText("View");

        reflectionMenu.setMnemonic('R');
        reflectionMenu.setText("Reflection");
        reflectionMenu.addActionListener(new java.awt.event.ActionListener()
        {
            public void actionPerformed(java.awt.event.ActionEvent evt)
            {
                reflectionClick(evt);
            }
        });
        viewMenu.add(reflectionMenu);

        mainMenu.add(viewMenu);

        setJMenuBar(mainMenu);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(toollBarTabs, javax.swing.GroupLayout.Alignment.TRAILING)
            .addComponent(jSplitPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 940, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addComponent(toollBarTabs, javax.swing.GroupLayout.PREFERRED_SIZE, 54, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(jSplitPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 468, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(25, 25, 25))
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    /* Tooolbar */
    
    class LocalMouseMotion extends MouseMotionAdapter
    {
        public void mouseDragged (java.awt.event.MouseEvent evt)
        {
            JButton button = (JButton) evt.getSource ();
            TransferHandler handle = button.getTransferHandler ();
            handle.exportAsDrag (button, evt, TransferHandler.COPY);
        }
    }
    
    private void addTool (String name)
    {
        JButton btn = new JButton ();
        btn.setText (name);
        btn.setTransferHandler (new TransferHandler ("text"));
        btn.addMouseMotionListener (new LocalMouseMotion ());
        shapeToolBar.add (btn);
    }
    
    private void addTools ()
    {
       addTool ("cube");
       addTool ("cone");
       addTool ("cyllinder");
       addTool ("sphere");
    }
    
    private void addComponent (String name)
    {
        JButton btn = new JButton ();
        btn.setText (name);
        btn.setTransferHandler (new TransferHandler ("text"));
        btn.addMouseMotionListener (new LocalMouseMotion ());
        componentToolBar.add (btn);
    }
    
    private void addComponents ()
    {
       addComponent ("JButton");
       addComponent ("JTree");
       addComponent ("JTable");
       addComponent ("JTextArea");
    }
    
    private void addColor (Color c)
    {
        JButton btn = new JButton ();
        btn.setText ("   ");
        btn.setBackground (c);
        btn.setTransferHandler (new TransferHandler ("background"));
        
        btn.addMouseMotionListener 
        (new java.awt.event.MouseMotionAdapter () 
         {
            public void mouseDragged(java.awt.event.MouseEvent evt) 
            {
                JButton button = (JButton) evt.getSource();
                TransferHandler handle = button.getTransferHandler();
                handle.exportAsDrag (button, evt, TransferHandler.COPY);
            }
         }
        );
        colorToolBar.add (btn);
    }
    
    private void addColors ()
    {
       addColor (new Color (255, 0, 0));
       addColor (new Color (0, 255, 0))    ;
       addColor (new Color (0, 0, 255))    ;
       addColor (new Color (255, 255, 0))    ;
    }
    
    /* Tree */
    
    class TreeTransferHandler extends TransferHandler
    {
        public boolean canImport (TransferHandler.TransferSupport support) 
        {
            boolean  result = false;
            System.out.println ("canImport (1)");
            if (support.isDrop()) 
            {
                JTree.DropLocation dropLocation = (JTree.DropLocation) support.getDropLocation();
                TreePath path = dropLocation.getPath();
                if (path != null)
                {
                    DataFlavor [] flavors = support.getDataFlavors ();
                    if (flavors.length == 1)
                    {
                        DataFlavor flavor = flavors[0];
                        Class cls = flavor.getRepresentationClass ();
                        System.out.println ("canImport (2) " + cls);
                        if (cls == String.class)
                        {
                           System.out.println ("canImport (3)");
                           result = true;
                        }
                        if (cls == Color.class)
                        {
                           System.out.println ("canImport (4)");
                           result = true;
                        }
                    }
                }
            }
            return result;
        }

        public boolean importData (TransferHandler.TransferSupport support) 
        {
            boolean  result = false;
            if (canImport (support))
            {
                JTree.DropLocation dropLocation = (JTree.DropLocation) support.getDropLocation();
                TreePath path = dropLocation.getPath();
 
                DataFlavor flavor = support.getDataFlavors () [0];
                Class cls = flavor.getRepresentationClass ();
               
                Transferable transfer = support.getTransferable();
                Object data = null;
                
                try
                {
                   data = transfer.getTransferData (flavor);
                }
                catch (UnsupportedFlavorException ex) { System.out.println (ex); }
                catch (IOException ex) {  System.out.println (ex); }

                if (data != null)
                {
                    if (cls == String.class)
                    {
                        String transferData = data.toString ();

                        int childIndex = dropLocation.getChildIndex();
                        if (childIndex == -1) 
                           childIndex = model.getChildCount (path.getLastPathComponent());

                        DefaultMutableTreeNode newNode = new DefaultMutableTreeNode (transferData);
                        DefaultMutableTreeNode parentNode = (DefaultMutableTreeNode) path.getLastPathComponent ();
                        model.insertNodeInto (newNode, parentNode, childIndex);   

                        TreePath newPath = path.pathByAddingChild (newNode);
                        tree.makeVisible(newPath);
                        tree.scrollRectToVisible (tree.getPathBounds (newPath));

                        result = true;
                    }

                    if (cls == Color.class)
                    {
                        Color color = (Color) data;
                        DefaultMutableTreeNode node = (DefaultMutableTreeNode) path.getLastPathComponent();
                        Object obj = node.getUserObject ();
                        if (obj instanceof Component)
                        {
                           Component comp = (Component) obj;
                           comp.setBackground (color);
                        }
                        else
                        {
                           node.setUserObject ("" + color);
                        }
                        result = true;
                    }
                }
            }
            return result;
        }
        // https://www.infoworld.com/article/2071334/adding-drop-support-to-jtree.html
    }
    
    /* Designer */

    class DesignerDropListener implements DropTargetListener 
    {
        public void drop (DropTargetDropEvent evt)
        {
            // System.out.println ("drop");
            Transferable transfer = evt.getTransferable();
            DataFlavor [] flavors = transfer.getTransferDataFlavors ();
            
            /*
            for (DataFlavor f : flavors)
            {
               System.out.println ("flavor " + f);
               System.out.println ("class " + f.getRepresentationClass ());
            }
            */
            
            if (flavors.length == 1)
            {
                DataFlavor flavor = flavors[0];
                Class cls = flavor.getRepresentationClass ();
                Object data = null;
                try
                {
                    data = transfer.getTransferData (flavor);
                } 
                catch (UnsupportedFlavorException ex) { System.out.println (ex); }
                catch (IOException ex) { System.out.println (ex); }
                    
                if (data != null)
                {
                    Point point = evt.getLocation ();
                    if (cls == String.class)
                    {
                        // addDesignerObject (point, data.toString ());
                    }
                    if (cls == Color.class)
                    {
                        Color color = (Color) data;
                        Component comp = designer.getComponentAt (point);
                        comp.setBackground (color);
                    }
                }
            } 
        };

        public void dragEnter(DropTargetDragEvent dtde) { }
        public void dragOver(DropTargetDragEvent dtde) { }
        public void dropActionChanged(DropTargetDragEvent dtde) { }
        public void dragExit(DropTargetEvent dte) { }
    };
    
    /*
    private void addDesignerObject (Point point, String toolName)
    {
        Object obj = null;
        try 
        {
            toolName = "javax.swing." + toolName;
            Class cls = Class.forName (toolName);
            obj = cls.newInstance();
            // System.out.println ("new object " + obj);
        } 
        catch (ClassNotFoundException ex) { System.out.println (ex); } 
        catch (InstantiationException ex) { System.out.println (ex); }
        catch (IllegalAccessException ex) { System.out.println (ex); }
        
        if (obj instanceof Component)
        {
            Component comp = (Component) obj;
            designer.add (comp, new AbsoluteConstraints (point.x, point.y, 100, 100));
            
            if (comp instanceof JButton)
            {
               ((JButton)comp).setText ("text");
               System.out.println ("text");
            }
            if (comp instanceof JTree)
            {
               ((JTree)comp).setMinimumSize(new Dimension (100, 100));
               System.out.println ("tree");
            }
            
            comp.setVisible(true);
            // System.out.println ("add " + comp);
            designer.setVisible (false);
            designer.setVisible (true);
        }
    }
    */
    
    
    /* Compilation */
    
    /*https://stackoverflow.com/questions/21544446/how-do-you-dynamically-compile-and-load-external-java-classes */
    
    private void compile ()
    {
        /*
        StringBuilder sb = new StringBuilder (64);
        sb.append ("package testcompile;\n");
        sb.append ("public class HelloWorld {\n");
        sb.append ("    public void doStuff() {\n");
        sb.append ("        System.out.println(\"Hello world\");\n");
        sb.append ("    }\n");
        sb.append ("}\n");
        */

        String source = editor.getText ();
        File helloWorldJava = new File ("testcompile/HelloWorld.java");
        if (helloWorldJava.getParentFile ().exists () || helloWorldJava.getParentFile ().mkdirs ())
        {

            try
            {
                Writer writer = null;
                try
                {
                    writer = new FileWriter (helloWorldJava);
                    // writer.write (sb.toString ());
                    writer.write (source);
                    writer.flush ();
                } 
                finally
                {
                    try
                    {
                       writer.close ();
                    } 
                    catch (Exception e) 
                    {
                    }
                }

                DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<JavaFileObject> ();
                JavaCompiler compiler = ToolProvider.getSystemJavaCompiler ();
                StandardJavaFileManager fileManager = compiler.getStandardFileManager (diagnostics, null, null);

                // This sets up the class path that the compiler will use.
                // I've added the .jar file that contains the DoStuff interface within in it...
                ArrayList<String> optionList = new ArrayList<String> ();
                // optionList.add("-classpath");
                // optionList.add(System.getProperty("java.class.path") + File.pathSeparator + "dist/InlineCompiler.jar");

                Iterable<? extends JavaFileObject> compilationUnit =
                        fileManager.getJavaFileObjectsFromFiles (Arrays.asList (helloWorldJava));

                JavaCompiler.CompilationTask task = compiler.getTask (
                        null,
                        fileManager,
                        diagnostics,
                        optionList,
                        null,
                        compilationUnit);
                /**
                 * *******************************************************************************************
                 * Compilation Requirements *
                 */
                if (task.call ())
                {
                    // Create a new custom class loader, pointing to the directory that contains the compiled
                    // classes, this should point to the top of the package structure!
                    URLClassLoader classLoader = new URLClassLoader (new URL[]
                    {
                        new File ("./").toURI ().toURL ()
                    });
                    // Load the class from the classloader by name....
                    Class loadedClass = classLoader.loadClass ("testcompile.HelloWorld");

                    Object obj = loadedClass.newInstance ();
                    try
                    {
                        Method m = loadedClass.getMethod ("doStuff");
                        m.invoke (obj);
                    } 
                    catch (NoSuchMethodException ex) { }
                    catch (SecurityException ex) { } 
                    catch (IllegalArgumentException ex) { } 
                    catch (InvocationTargetException ex) { }
                }
                else
                {
                    for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics.getDiagnostics ())
                    {
                        System.out.format ("Error on line %d in %s%n",
                                diagnostic.getLineNumber (),
                                diagnostic.getSource ().toUri ());
                    }
                }
                fileManager.close ();
            } catch (IOException | ClassNotFoundException | InstantiationException | IllegalAccessException exp)
            {
                exp.printStackTrace ();
            }
        }
    }
    
    /* Reflection */
    
    private void addComponents (DefaultMutableTreeNode target, Container container)
    {
        for (Component c : container.getComponents())
        {
           DefaultMutableTreeNode node = new DefaultMutableTreeNode (c);
           if (c instanceof Container)
              addComponents (node, (Container) c);
           target.add (node);
        }
    }
    
    private void displayReflection ()
    {
        DefaultMutableTreeNode branch = new DefaultMutableTreeNode ("Reflection");
        addComponents (branch, this);
        root.add (branch);
        model.nodesWereInserted (root, new int [] { root.getIndex (branch) });
    }
    
    /* Java 3D */
    
    // http://www.java2s.com/Code/Java/3D/Catalog3D.htm
    // http://www.java2s.com/Code/Java/3D/BasicConstruct.htm
    // http://www.java2s.com/Code/Java/3D/TransformExplorer.htm
    
    /*
    private SimpleUniverse simpleU;
    private BranchGroup rootBranchGroup;

    protected void initial_setup ()
    {
        scene.setLayout (new BorderLayout ());
        GraphicsConfiguration config = SimpleUniverse.getPreferredConfiguration ();
        Canvas3D canvas3D = new Canvas3D (config);
        scene.add ("Center", canvas3D);
        simpleU = new SimpleUniverse (canvas3D);
        rootBranchGroup = new BranchGroup ();
    }

    public void addDirectionalLight (Vector3f direction, Color3f color)
    {
        BoundingSphere bounds = new BoundingSphere ();
        bounds.setRadius (1000d);

        DirectionalLight lightD = new DirectionalLight (color, direction);
        lightD.setInfluencingBounds (bounds);

        rootBranchGroup.addChild (lightD);
    }

    public void addBox (float x, float y, float z, Color3f diffuse, Color3f spec)
    {
        
        Material mat = new Material ();
        mat.setDiffuseColor (diffuse);
        mat.setSpecularColor (spec);
        mat.setShininess (5.0f);

        Appearance app = new Appearance ();
        app.setMaterial (mat);
        
        Box box = new Box (x, y, z, app);

        TransformGroup tg = new TransformGroup ();
        tg.addChild (box);

        rootBranchGroup.addChild (tg);

        tg.setCapability (TransformGroup.ALLOW_TRANSFORM_WRITE);
        tg.setCapability (TransformGroup.ALLOW_TRANSFORM_READ);

        MouseRotate myMouseRotate = new MouseRotate ();
        myMouseRotate.setTransformGroup (tg);
        myMouseRotate.setSchedulingBounds (new BoundingSphere ());
        rootBranchGroup.addChild (myMouseRotate);

        MouseTranslate myMouseTranslate = new MouseTranslate ();
        myMouseTranslate.setTransformGroup (tg);
        myMouseTranslate.setSchedulingBounds (new BoundingSphere ());
        rootBranchGroup.addChild (myMouseTranslate);

        MouseZoom myMouseZoom = new MouseZoom ();
        myMouseZoom.setTransformGroup (tg);
        myMouseZoom.setSchedulingBounds (new BoundingSphere ());
        rootBranchGroup.addChild (myMouseZoom);
    }

    public void finalise_setup ()
    {
        // Then add the branch group into the Universe
        simpleU.addBranchGraph (rootBranchGroup);

        // And set up the camera position
        simpleU.getViewingPlatform ().setNominalViewingTransform ();
    }

    public void setupScene ()
    {
        initial_setup ();
        addBox (0.4f, 0.5f, 0.6f, new Color3f (1, 0, 0), new Color3f (1, 0, 0));
        addDirectionalLight (new Vector3f (0f, 0f, -1), new Color3f (1f, 1f, 0f));
        finalise_setup ();
    }
    
    */

    /* Property Table */
    
    Object propObject;
    
    DefaultTreeCellRenderer treeRenderer = new DefaultTreeCellRenderer ();

    private class LocalTableModel extends DefaultTableModel
    {
            /*
            public Class getColumnClass (int column)
            {
                if (column == 0)
                    return Icon.class;
                else
                    return String.class;
            }
            */
        
        Object obj;
        Vector <Object> data = new Vector <Object> ();
    }
    
    private class LocalRenderer extends DefaultTableCellRenderer
    {
        @Override
        public Component getTableCellRendererComponent (JTable table, Object value,
                                                        boolean isSelected, boolean hasFocus,
                                                        int row, int column) 
        {
            
              Component comp = super.getTableCellRendererComponent (table, value, isSelected, hasFocus, row, column);
              Component result = comp;
              
              if (column == 0)
              {
                  if (comp instanceof JLabel)
                  {
                     JLabel label = (JLabel) comp;
                     if (row == 0)
                        label.setIcon (treeRenderer.getOpenIcon ());
                     else if (row == 1)
                        label.setIcon (treeRenderer.getLeafIcon ());
                     else if (row == 2)
                        label.setIcon (treeRenderer.getClosedIcon ());
                     else if (row == 3)
                        label.setIcon (treeRenderer.getDefaultOpenIcon ());
                     else if (row == 4)
                        label.setIcon (treeRenderer.getDefaultLeafIcon ());
                     else if (row == 5)
                        label.setIcon (treeRenderer.getDefaultClosedIcon ());
                     else if (row == 6 || row == 7)
                     {
                         try {
                             label.setIcon (treeRenderer.getDefaultClosedIcon ());
                             LookAndFeel save = UIManager.getLookAndFeel();
                             LookAndFeel laf = new MetalLookAndFeel();
                             UIManager.setLookAndFeel(laf);
                             final String COLLAPSED_ICON = "Tree.collapsedIcon";
                             final String EXPANDED_ICON = "Tree.expandedIcon";
                             Icon collapsed = (Icon) UIManager.get(COLLAPSED_ICON);
                             Icon expanded = (Icon) UIManager.get(EXPANDED_ICON);
                             UIManager.setLookAndFeel(save);
                             if (row == 6)
                                 label.setIcon (expanded);
                             else
                                 label.setIcon (collapsed);
                         } 
                         catch (UnsupportedLookAndFeelException ex) { }
                     }
                  }
              }
              if (column == 1)
              {
                  LocalTableModel model = (LocalTableModel) table.getModel ();

                  javax.swing.Box box = javax.swing.Box.createHorizontalBox ();
                  box.add (comp);

                  JButton button = new JButton ();
                  button.setText ("...");
                  box.add (button);
                  
                  result = box;
              }
              
              /*
              if (comp instanceof JLabel)
              {
                 JLabel label = (JLabel) comp;
                 if (value instanceof String)
                    label.setIcon (treeRenderer.getLeafIcon());
                 else 
                    label.setIcon (treeRenderer.getOpenIcon());
              }
              */
              // return comp;
              return result;
          }
     }
   
    private void displayProperties (Object obj)
    {
        propTable.setDefaultRenderer (Object.class, new LocalRenderer ());
   
        try 
        {
            LocalTableModel model = new LocalTableModel ();
            model.addColumn ("name");
            model.addColumn ("value");
        
            model.obj = obj; // remember, needed in propTableChanged
            Class cls = obj.getClass ();
            BeanInfo info = Introspector.getBeanInfo (cls);
            PropertyDescriptor [] properties = info.getPropertyDescriptors ();
            for (PropertyDescriptor p : properties)
            {
                String name = p.getName ();
                Object value = null;
                try 
                {
                    
                    Method read = p.getReadMethod();
                    if (read != null)
                       value = read.invoke (obj);
                } 
                catch (IllegalAccessException ex) { } 
                catch (IllegalArgumentException ex) { } 
                catch (InvocationTargetException ex) { }
                Object [] line = {name, value};
                model.addRow (line);
                model.data.add (value);
            }
            propTable.setModel (model);
            model.addTableModelListener (new LocalTableModelListener ());
        } 
        catch (IntrospectionException ex) 
        {
        }
    }    
    
    class LocalTableModelListener implements TableModelListener    
    {
        @Override
        public void tableChanged (TableModelEvent evt) 
        {
            propTableChanged (evt);
        }
    }
   
    private void propTableChanged (TableModelEvent evt)
    {
        int line = evt.getFirstRow ();
        int col = evt.getColumn ();
        
        if (col == 1)
        {
            LocalTableModel model = (LocalTableModel) evt.getSource();
            String name = (String) model.getValueAt (line, 0);
            String value = (String) model.getValueAt (line, 1);

            Object obj = model.obj;
            Class cls = obj.getClass ();
            BeanInfo info;
            try 
            {
                info = Introspector.getBeanInfo (cls);
                for (PropertyDescriptor prop : info.getPropertyDescriptors ())
                if (prop.getName() == name)
                {
                    Method write = prop.getWriteMethod();
                    if (write != null)
                        try 
                        {
                            write.invoke (obj, new Object [] { value });
                        } 
                        catch (IllegalAccessException ex) { } 
                        catch (IllegalArgumentException ex) { }
                        catch (InvocationTargetException ex) { }
                }
            } 
            catch (IntrospectionException ex) {  }
        }
    }
   
    /* Tree selection */
    
    private void treeValueChanged(javax.swing.event.TreeSelectionEvent evt) {//GEN-FIRST:event_treeValueChanged
       DefaultMutableTreeNode node = (DefaultMutableTreeNode) tree.getLastSelectedPathComponent();
       if (node != null)
       {
          displayProperties (node.getUserObject());
       }
    }//GEN-LAST:event_treeValueChanged

    /* Menu */
    
    private void reflectionClick(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_reflectionClick
        displayReflection ();
    }//GEN-LAST:event_reflectionClick

    private void compileClick(java.awt.event.ActionEvent evt)//GEN-FIRST:event_compileClick
    {//GEN-HEADEREND:event_compileClick
        compile ();
    }//GEN-LAST:event_compileClick

    private void quitClick(java.awt.event.ActionEvent evt)//GEN-FIRST:event_quitClick
    {//GEN-HEADEREND:event_quitClick
        // dispose ();
        System.exit (0);
    }//GEN-LAST:event_quitClick

    public static void main(String args[]) {

        /*        
        int [][][][]a = new int [3][2][][];
        System.out.println (a.length);
        System.out.println (a[0].length);
        System.out.println (a[0] == null ? "null" : "array");
        System.out.println (a[0][0] == null ? "null" : "array");
        
        int [] [] c = new int [3] [ ];
        c[0] = new int [] { };         // c[0] má nula prvků
        c[1] = new int [] { 10 };      // c[1] má jeden prvek
        c[2] = new int [] { 100, 200 };
        */

        /* Set the Nimbus look and feel */
        //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
        /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
         * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html 
         */
        if (false)
        {
            try {
                for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
                    if ("Nimbus".equals(info.getName())) {
                        javax.swing.UIManager.setLookAndFeel(info.getClassName());
                        break;
                    }
                }
            } 
            catch (ClassNotFoundException ex) { }
            catch (InstantiationException ex) { }
            catch (IllegalAccessException ex) { }
            catch (javax.swing.UnsupportedLookAndFeelException ex) { }
        }
        //</editor-fold>
        
       /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new MainWindow().setVisible(true);
            }
        });
    }

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JTabbedPane centralTabs;
    private javax.swing.JToolBar colorToolBar;
    private javax.swing.JMenuItem compileMenu;
    private javax.swing.JToolBar componentToolBar;
    private javax.swing.JPanel designer;
    private javax.swing.JMenu editMenu;
    private javax.swing.JTextArea editor;
    private javax.swing.JMenu fileMenu;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JSplitPane jSplitPane1;
    private javax.swing.JSplitPane jSplitPane2;
    private javax.swing.JMenuBar mainMenu;
    private javax.swing.JTable propTable;
    private javax.swing.JMenuItem quitMenu;
    private javax.swing.JMenuItem reflectionMenu;
    private javax.swing.JPanel scene;
    private javax.swing.JToolBar shapeToolBar;
    private javax.swing.JTabbedPane toollBarTabs;
    private javax.swing.JTree tree;
    private javax.swing.JMenu viewMenu;
    // End of variables declaration//GEN-END:variables
}

/*

    http://stackoverflow.com/questions/54272217/cannot-programatically-compile-java-source-from-string-on-linux

    public static final JavaCompiler JAVAC;

    static {
        String h = System.getProperty("java.home");
        if (!h.endsWith("jre")) {
            h = h.replace("jre", "jdk") + File.separator + "jre";
            System.setProperty("java.home", h);
        }
        System.out.println(System.getProperty("java.home"));
        JAVAC = ToolProvider.getSystemJavaCompiler();
    }

    static {
        if (System.getProperty("os.name").toLowerCase().contains("windows")) { //Added this check
            String h = System.getProperty("java.home");
            if (!h.endsWith("jre")) {
                h = h.replace("jre", "jdk") + File.separator + "jre";
                System.setProperty("java.home", h);
            }
        }
        JAVAC = ToolProvider.getSystemJavaCompiler();
    }

    public static class JavaClass extends SimpleJavaFileObject {

        private ByteArrayOutputStream baos = new ByteArrayOutputStream();

        public JavaClass(String className) {
            super(getUri(className), Kind.CLASS);
        }

        private static final URI getUri(String className) {
            try {
                return new URI(className);
            } catch (URISyntaxException e) {
                throw new RuntimeException("Could not parse URI", e);
            }
        }

        @Override
        public OutputStream openOutputStream() throws IOException {
            return baos;
        }

        public byte[] getByteCode() {
            return baos.toByteArray();
        }

    }

    public static class JavaClassLoader extends ClassLoader {

        private final Map<String, JavaClass> classes = new HashMap<>();

        public JavaClassLoader(ClassLoader classLoader) {
            super(classLoader);
        }

        public JavaClass getClass(String name) {
            return classes.get(name);
        }

        public JavaClassLoader addClass(JavaClass cc) {
            classes.put(cc.getName(), cc);
            return this;
        }

        @Override
        protected Class<?> findClass(String name) throws ClassNotFoundException {
            JavaClass cc = classes.get(name);
            if (cc == null) {
                return super.findClass(name);
            }
            byte[] byteCode = cc.getByteCode();
            return defineClass(name, byteCode, 0, byteCode.length);
        }

    }

    public static class FileManager extends ForwardingJavaFileManager<JavaFileManager> {

        private static final StandardJavaFileManager STANDARD_JAVA_FILE_MANAGER = JAVAC.getStandardFileManager(null, null, null);

        private JavaClassLoader classLoader = new JavaClassLoader(Test.class.getClassLoader());

        public FileManager(String className) {
            super(STANDARD_JAVA_FILE_MANAGER);
            this.classLoader.addClass(new JavaClass(className));
        }

        public JavaClassLoader getClassLoader() {
            return classLoader;
        }

        @Override
        public JavaFileObject getJavaFileForOutput(Location location, String className, Kind kind, FileObject sibling) throws IOException {
            return classLoader.getClass(className);
        }

        public byte[] getBytecode(String className) {
            return classLoader.getClass(className).getByteCode();
        }

        public Class<?> loadClass(String className) throws ClassNotFoundException {
            return classLoader.loadClass(className);
        }

    }

    public static class JavaSource extends SimpleJavaFileObject {

        private final String code;

        public JavaSource(String name, String code) {
            super(URI.create("string:///" + name.replace('.', '/') + Kind.SOURCE.extension), Kind.SOURCE);
            this.code = code;
        }

        @Override
        public CharSequence getCharContent(boolean ignoreEncodingErrors) {
            return code;
        }

    }


    public static void main(String[] args) throws Exception {
        String className = //Class name
        String code = //Code

        JavaSource sourceCode = new JavaSource(className, code);
        FileManager fileManager = new FileManager(className);
        JAVAC.getTask(null, fileManager, null, null, null, Arrays.asList(sourceCode)).call();
    }

*/