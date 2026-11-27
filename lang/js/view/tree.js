$('#tt').tree({ data:

[
   { "id": 100, "text": "classes",
     "children" : [
         { "id": 110, "text": "C", "kind": "cls", "children" : [
               { "id": 111, "text": "x", "type": "int", "kind": "var" },
               { "id": 112, "text": "y", "type": "int", "kind": "var" }
            ]
         },
         { "id": 120, "text": "D", "kind": "cls", "children" : [
               { "id": 121, "text": "show", "type": "void", "kind": "func", "children" : [
                     { "id": 121, "text": "txt", "type": "string", "kind": "param" }
                  ]
               },
               { "id": 123, "text": "hide", "type": "void", "kind": "func" }
            ]
         }
      ]
   },
   { "id": 300, "text":"files",
     "children" : [
         { "id": 301, "text": "cone.html" },
         { "id": 302, "text": "cube.html" },
         { "id": 302, "text": "jgraph-diagram.html" },
         { "id": 302, "text": "jgraph-layout.html" },
         { "id": 302, "text": "jgraph-tree.html" },
         { "id": 302, "text": "webgl.html" }
     ]
   }
]

});
