using System;

namespace SharpView
{
    public class Output
    {
        public Output () { }
      
        public void error (string msg)
        {
            throw new Exception(msg);
        }
    
		public void send (string s)
        {
        }
      
   }
}