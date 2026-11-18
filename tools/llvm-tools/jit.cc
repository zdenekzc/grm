
/* clang-jit.cc */

#include "jit.h"

#ifndef RESOURCE_DIR
    #define RESOURCE_DIR ""
#endif

#include <unistd.h> // extern char **environ;
// #include "dlfcn.h"

#include <iostream> // important when compiled code is using iostream
using namespace std;

/* ---------------------------------------------------------------------- */

#undef emit
#include "llvm/Config/llvm-config.h"

#include "clang/Basic/DiagnosticOptions.h"
#include "clang/CodeGen/CodeGenAction.h"
#include "clang/Frontend/CompilerInvocation.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/TextDiagnosticPrinter.h"
#include "clang/Frontend/Utils.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/ExecutionEngine/GenericValue.h"
#include "llvm/ExecutionEngine/MCJIT.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/IR/Module.h"
#include "llvm/Object/Archive.h"
#include "llvm/Object/ObjectFile.h"

llvm::ExecutionEngine * global_engine = nullptr;

/* ---------------------------------------------------------------------- */

int compileAndRun (string file_name,
                   string_list options,
                   string_list libraries,
                   string_list new_argumets,
                   string_list new_environment)
{
   int Res = 255;

   /* options as char pointers */
   std::vector <const char *> params;

   params.push_back ("interpreter_name"); // necessary, otherwise : expected exactly one compiler job
   params.push_back (file_name.c_str ());

   int opt_cnt = options.size ();
   for (int i = 0; i < opt_cnt; i++)
   {
       params.push_back (options[i].c_str ());
       std::cout << "OPT " << options[i] << std::endl;
   }

   #if 0
   llvm::IntrusiveRefCntPtr<clang::DiagnosticOptions> diagOpts = new clang::DiagnosticOptions();
   clang::TextDiagnosticPrinter * diagClient = new clang::TextDiagnosticPrinter(llvm::errs(), &*diagOpts);
   llvm::IntrusiveRefCntPtr<clang::DiagnosticIDs> diagID = new clang::DiagnosticIDs ();
   llvm::IntrusiveRefCntPtr<clang::DiagnosticsEngine> diags = new clang::DiagnosticsEngine (diagID, &*diagOpts, diagClient);
   #endif

   #if LLVM_VERSION_MAJOR <= 14
      std::unique_ptr<clang::CompilerInvocation> CI = clang::createInvocationFromCommandLine (params);
   #else
      std::unique_ptr<clang::CompilerInvocation> CI = clang::createInvocation (params);
   #endif

   clang::CompilerInstance * compiler = new clang::CompilerInstance;
   compiler->setInvocation (std::move (CI));

   #if LLVM_VERSION_MAJOR >= 20
      compiler->createDiagnostics (*llvm::vfs::getRealFileSystem());
   #else
      compiler->createDiagnostics ();
   #endif
   if (!compiler->hasDiagnostics ())
      return Res;

   compiler->getHeaderSearchOpts().ResourceDir = RESOURCE_DIR;

   #if 0
   std::unique_ptr<clang::FrontendAction> FrontAct (new clang::ASTPrintAction());
   if (!compiler->ExecuteAction (*FrontAct))
       return Res;

   // transferASTDataFromCompilerInstance
   if (compiler->hasASTContext ())
   {
       clang::ASTContext & ast_ctx = compiler->getASTContext ();
       for (clang::DeclContext::decl_iterator I = ast_ctx.getTranslationUnitDecl()->decls_begin (),
            E = ast_ctx.getTranslationUnitDecl()->decls_end ();
            I != E;
            ++ I )
        {
            clang::Decl * decl = *I;
            string kind = decl->getDeclKindName ();
            string name = "";
            if (clang::NamedDecl * named_decl = llvm::dyn_cast <clang::NamedDecl> (decl))
            {
                name = named_decl->getQualifiedNameAsString ();
            }
            cout << "Declaration " << name << " : " << kind << endl;
        }
   }
   #endif

   llvm::InitializeNativeTarget();
   llvm::InitializeNativeTargetAsmParser();
   llvm::InitializeNativeTargetAsmPrinter();

   if (false)
   {
      clang::EmitLLVMAction * Act = new clang::EmitLLVMAction;
      compiler->ExecuteAction (*Act);
   }

   {
      // clang::EmitBCAction * Act = new clang::EmitBCAction;
      // compiler->ExecuteAction (*Act);
   }

   if (false)
   {
      clang::EmitAssemblyAction * Act = new clang::EmitAssemblyAction;
      compiler->ExecuteAction (*Act);
   }

   {
      // clang::EmitObjAction * Act = new clang::EmitObjAction;
      // compiler->ExecuteAction (*Act);
   }

   clang::EmitLLVMOnlyAction * Act = new clang::EmitLLVMOnlyAction;
   if (!compiler->ExecuteAction (*Act))
       return Res;

   llvm::Module * Module = Act->takeModule().release ();

   if (Module)
   {
      std::cout << "MODULE" << std::endl;

      llvm::Function * EntryFn = Module->getFunction("main");
      if (!EntryFn)
      {
         llvm::errs() << "main function not found in module.\n";
         return 255;
      }

      std::cout << "POINT 1" << std::endl;

      std::unique_ptr<llvm::Module> M (Module);
      std::string Error;
      llvm::ExecutionEngine * EE =
         llvm::EngineBuilder (std::move (M))
           .setEngineKind(llvm::EngineKind::Either)
           .setErrorStr(&Error)
           .create();

      std::cout << "POINT 2" << std::endl;

      if (!EE) { llvm::errs() << "unable to make execution engine: " << Error << "\n"; }
      global_engine = EE;

      int cnt = libraries.size ();
      for (int inx = 0; inx < cnt; inx++)
      {
         std::string library = libraries [inx];
         cout << "LIBRARY " << library << endl;
         #if 0
            // from llvm/tools/lli/lli.cpp
            using namespace llvm;
            using namespace object;

            int len = library.length ();
            if (len > 2 && library.substr (len-2) == ".a") // !?
            {
               ErrorOr <std::unique_ptr<MemoryBuffer>> ArBufOrErr =
                  MemoryBuffer::getFileOrSTDIN (library);

               if (!ArBufOrErr)
               {
                  cout << "Library not found: " << library << endl;
               }
               else
               {
                  std::unique_ptr<MemoryBuffer> &ArBuf = ArBufOrErr.get();

                  Expected<std::unique_ptr<object::Archive>> ArOrErr =
                     object::Archive::create(ArBuf->getMemBufferRef());

                  if (!ArOrErr)
                  {
                     cout << "Library not loaded: " << library << endl;
                  }
                  else
                  {
                      std::unique_ptr<object::Archive> & Ar = ArOrErr.get();
                      object::OwningBinary<object::Archive> OB(std::move(Ar), std::move(ArBuf));
                      EE->addArchive(std::move(OB));
                      cout << "Library added: " << library << endl;
                  }
               }
            }
            else
            {
               Expected<llvm::object::OwningBinary<object::ObjectFile>> Obj =
                  llvm::object::ObjectFile::createObjectFile (library);
               if (!Obj)
               {
                  cout << "library not found: " << library << endl;
               }
               else
               {
                  llvm::object::OwningBinary <object::ObjectFile> & V = Obj.get ();
                  EE->addObjectFile (std::move(V));
                  cout << "Library added: " << library << endl;
               }
            }
         #else
            #if 0
               void* lib_handle = dlopen (library.c_str(), RTLD_NOW | RTLD_GLOBAL);
               if (lib_handle == NULL)
                  llvm::errs() << "library not loaded: " << library << "\n";
            #endif
         #endif
      }

      std::cout << "POINT 3" << std::endl;

      EE->finalizeObject();
      EE->runStaticConstructorsDestructors (false);

      std::cout << "POINT 4" << std::endl;

      /* arguments as char pointers */
      int new_argc = new_argumets.size ();
      const char * * new_argv = new const char * [new_argc];
      for (int i = 0; i < new_argc; i++)
      {
         new_argv [i] = new_argumets [i].c_str();
      }

      std::vector<std::string> Args;
      if (new_argc == 0)
      {
         Args.push_back (Module->getModuleIdentifier());
      }
      else
      {
         for (int i = 0; i < new_argc; i++)
             Args.push_back (new_argv [i]);
      }

      /* environment as char pointer */
      char * * new_envp = environ;

      int env_cnt = new_environment.size ();
      if (env_cnt > 0)
      {
         typedef char * CStr;
         new_envp = new CStr [env_cnt+1];
         for (int i = 0; i < env_cnt; i++)
         {
             new_envp [i] = (char *) new_environment [i].c_str();
         }
         new_envp [env_cnt] = NULL;
      }

      std::cout << "POINT 5 " << EntryFn << std::endl;

      Res = EE->runFunctionAsMain (EntryFn, Args, new_envp);

      std::cout << "POINT 6" << std::endl;

      delete [] new_argv;
      if (env_cnt > 0) delete [] new_envp;

      #if 0
      std::cout << "COUT " << (void*) & cout << std::endl;
      EE->addGlobalMapping ("cout", (uint64_t) & cout);
      EE->addGlobalMapping ("_ZSt4cout", (uint64_t) & cout);

      llvm::Function * func = EntryFn; //  EE->FindFunctionNamed ("main2");
      if (func)
      {
      llvm::GenericValue a; a.UIntPairVal.first = 11;
          llvm::GenericValue b; b.PointerVal = & cout;
      vector <llvm::GenericValue> args;
      args.push_back (a);
      args.push_back (b);
          std::cout << "CALL" << std::endl;
          llvm::GenericValue result = EE->runFunction (func, args);
      }
      #endif

      std::cout << "DONE" << std::endl;
   }

   // Shutdown.
   // llvm::llvm_shutdown();

   return Res;
}

/* ---------------------------------------------------------------------- */

int compileModule (string file_name, string_list options)
{
   int Res = 255;

   vector <const char *> params;
   params.push_back ("interpreter_name");
   params.push_back (file_name.c_str ());

   int argc = options.size ();
   for (int i = 0; i < argc; i++)
       params.push_back (options [i].c_str ());

   #if LLVM_VERSION_MAJOR <= 14
      std::unique_ptr<clang::CompilerInvocation> CI = clang::createInvocationFromCommandLine (params);
   #else
      std::unique_ptr<clang::CompilerInvocation> CI = clang::createInvocation (params);
   #endif

   clang::CompilerInstance * compiler = new clang::CompilerInstance;
   compiler->setInvocation (std::move (CI));

   #if LLVM_VERSION_MAJOR >= 20
      compiler->createDiagnostics(*llvm::vfs::getRealFileSystem());
   #else
      compiler->createDiagnostics ();
   #endif
   if (!compiler->hasDiagnostics ())
      return Res;

   compiler->getHeaderSearchOpts().ResourceDir = RESOURCE_DIR;

   clang::EmitLLVMOnlyAction * Act = new clang::EmitLLVMOnlyAction;
   if (!compiler->ExecuteAction (*Act))
       return Res;

   std::unique_ptr<llvm::Module> Module = Act->takeModule();

   if (Module)
   {
      global_engine->addModule (std::move (Module));
      std::cout << "ADD MODULE" << std::endl;
   }

   Res = 1;
   return Res;
}

/* ---------------------------------------------------------------------- */
