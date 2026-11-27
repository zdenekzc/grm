using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

using System.CodeDom.Compiler;

namespace SharpView
{
    public partial class MainWindow : Form
    {
        
        public MainWindow ()
        {
            InitializeComponent ();
        }
        
        private void treeView_NodeMouseClick (object sender, TreeNodeMouseClickEventArgs e)
        {
            SelectObject (e.Node.Tag);
        }

        public void SelectObject (object obj)
        {
            propGrid.SelectedObject = obj;
        }


        private void open_Click (object sender, EventArgs e)
        {
            if (openDialog.ShowDialog () == DialogResult.OK)
            {
                StreamReader stream = new StreamReader (openDialog.FileName);
                // XmlSerializer reader = new XmlSerializer (typeof (MyObject));
                // obj = (MyObject)reader.Deserialize (stream);
                stream.Close ();

                // AddObject (obj);
            }
        }

        private void save_Click (object sender, EventArgs e)
        {
            if (saveDialog.ShowDialog () == DialogResult.OK)
            {
                StreamWriter stream = new StreamWriter (saveDialog.FileName);
                // XmlSerializer writer = new XmlSerializer (typeof (MyObject));
                // writer.Serialize (stream, obj);
                // writeData (stream);
                stream.Close ();
            }
        } 

        private void quit_Click(object sender , EventArgs e)
        {
            Close ();
        }
        
        /* Compilation */
        
        void compile_Click (object sender, EventArgs e)
        {
            info.Clear ();

            /*
            string[] code = { editor.Text };
            
            string[] code0 = {
                                "using System; using System.Data;",
                                "namespace CodeFromFile"+
                                "{"+
                                "   public class CodeFromFile"+
                                "   {"+
                                "       static public int Add(int a ,int b)"+
                                "       {"+
                                "           return a+b;"+
                                "       }"+
                                "   }"+
                                "}"
                         };

            CompilerParameters CompilerParams = new CompilerParameters ();

            CompilerParams.GenerateInMemory = true;
            CompilerParams.TreatWarningsAsErrors = false;
            CompilerParams.GenerateExecutable = false;
            CompilerParams.CompilerOptions = "/optimize";
      
            string[] references = { "System.dll", "System.Data.dll" };
            CompilerParams.ReferencedAssemblies.AddRange (references);
      
            CSharpCodeProvider provider = new CSharpCodeProvider ();
            CompilerResults compile = provider.CompileAssemblyFromSource (CompilerParams, code);
      
            if (compile.Errors.HasErrors)
            {
                string text = "Compile error: ";
                foreach (CompilerError ce in compile.Errors)
                {
                    info.AppendText (ce.ToString () + "\r\n");
                    text += "\r\n" + ce.ToString ();
                }
                // throw new Exception (text);
            }
            else
            {
                displayAssembly (compile.CompiledAssembly);
                
                Module module = compile.CompiledAssembly.GetModules ()[0];
                Type mt = null;
                MethodInfo meth = null;
      
                if (module != null)
                    mt = module.GetType ("CodeFromFile.CodeFromFile");
      
                if (mt != null)
                    meth = mt.GetMethod ("Add");
            
                if (meth != null)
                {
                    int result = (int)meth.Invoke (null, new object[] { 5, 10 });
                    info.AppendText ("result = " + result);
                }
            }
             
            */
        }


		/*
		http://stackoverflow.com/questions/32769630/how-to-compile-a-c-sharp-file-with-roslyn-programmatically

        private static readonly IEnumerable<string> DefaultNamespaces =
            new[]
            {
                "System", 
                "System.IO", 
                "System.Net", 
                "System.Linq", 
                "System.Text", 
                "System.Text.RegularExpressions", 
                "System.Collections.Generic"
            };

        private static string runtimePath = @"C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.5.1\{0}.dll";

        private static readonly IEnumerable<MetadataReference> DefaultReferences =
            new[]
            {
                MetadataReference.CreateFromFile(string.Format(runtimePath, "mscorlib")),
                MetadataReference.CreateFromFile(string.Format(runtimePath, "System")),
                MetadataReference.CreateFromFile(string.Format(runtimePath, "System.Core"))
            };

        private static readonly CSharpCompilationOptions DefaultCompilationOptions =
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary)
                    .WithOverflowChecks(true).WithOptimizationLevel(OptimizationLevel.Release)
                    .WithUsings(DefaultNamespaces);

        public static SyntaxTree Parse(string text, string filename = "", CSharpParseOptions options = null)
        {
            var stringText = SourceText.From(text, Encoding.UTF8);
            return SyntaxFactory.ParseSyntaxTree(stringText, options, filename);
        }

        static void Main(string[] args)
        {
            var fileToCompile = @"C:\Users\DesktopHome\Documents\Visual Studio 2013\Projects\ConsoleForEverything\SignalR_Everything\Program.cs";
            var source = File.ReadAllText(fileToCompile);
            var parsedSyntaxTree = Parse(source, "", CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.CSharp5));

            var compilation
                = CSharpCompilation.Create("Test.dll", new SyntaxTree[] { parsedSyntaxTree }, DefaultReferences, DefaultCompilationOptions);
            try
            {
                var result = compilation.Emit(@"c:\temp\Test.dll");

                Console.WriteLine(result.Success ? "Sucess!!" : "Failed");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            Console.Read();
        }

		*/
        
    } // end of class
} // end of namespace
