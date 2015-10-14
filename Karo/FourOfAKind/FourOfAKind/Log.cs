using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FourOfAKind
{
    class Log
    {
        public static ConsoleForm Console = null;
        public static List<ConsoleMessage> LogMessages = new List<ConsoleMessage>();

        /// <summary>
        /// Procedura dodająca do konsoli
        /// </summary>
        /// <param name="message">Treść wiadomości</param>
        /// <param name="type">Rodzaj, default, error, warning, info</param>
        /// <param name="colorAll">Czy kolorować cały tekst czy tylko znacznik czasu</param>
        public static void AddToConsole(string message, string type = "default", bool colorAll = true)
        {
            LogMessages.Add(new ConsoleMessage(message, type, colorAll));
            try
            {
                Console.RefreshConsole();
            }
            catch { }
        }
    }
}
