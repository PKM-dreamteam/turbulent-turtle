using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FourOfAKind
{
    public class ConsoleMessage
    {
        public string Timestamp;
        public string Content;
        public string Type;
        public bool ColorAll;

        public ConsoleMessage()
        {
            this.Timestamp = DateTime.Now.ToString("H:mm:ss.fff:");
            this.Content = String.Empty;
            this.Type = "default";
            this.ColorAll = true;
        }

        public ConsoleMessage(string _Content, string _Type = "default", bool _ColorAll = true)
        {
            this.Timestamp = DateTime.Now.ToString("H:mm:ss.fff:");
            this.Content = _Content;
            this.Type = _Type;
            this.ColorAll = _ColorAll;
        }
    }
}
