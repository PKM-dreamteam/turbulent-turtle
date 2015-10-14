using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace FourOfAKind
{
    public partial class ConsoleForm : Form
    {
        private mainForm parentForm;
        private String ConsoleRTFHeader = String.Empty;
        private String ConsoleRTFContents = String.Empty;
        private String ConsoleRTFFooter = String.Empty;

        public ConsoleForm(mainForm parent)
        {
            parentForm = parent;
            InitializeComponent();
            //{\fonttbl{\f0\fnil\fcharset0 Microsoft Sans Serif;}}
            ConsoleRTFHeader = @"{\rtf1\utf8\deff0 {\fonttbl {\f0 Consolas;}}{\colortbl;"
                                + @"\red0\green0\blue0;"            // cf1 - default color
                                + @"\red150\green0\blue0;"          // cf2 - Error color
                                + @"\red200\green170\blue0;"        // cf3 - Warning color
                                + @"\red40\green90\blue170;"        // cf4 - Info color
                                + @"}"
                                + @"\tx1800\fs20";
                                //+ @"\viewkind4\uc1\pard\cf1\lang1033\f0\fs17";

            ConsoleRTFFooter = "}";
        }

        public void RefreshConsole()
        {
            AddToConsole();
            consoleContents.Rtf = ConsoleRTFHeader + ConsoleRTFContents + ConsoleRTFFooter;
            consoleContents.SelectionStart = consoleContents.Text.Length;
            consoleContents.ScrollToCaret();
        }

        /// <summary>
        ///     Adds new messages
        /// </summary>
        /// <param name="message"></param>
        /// <param name="mode"></param>
        /// <param name="colorAll"></param>
        private void AddToConsole()
        {
            while(Log.LogMessages.Count>0)
            {
                ConsoleMessage one = Log.LogMessages.First();
                string consoleMessage = String.Empty;

                switch (one.Type)
                {
                    case "default":
                        consoleMessage = @"\cf1";
                        break;
                    case "error":
                        consoleMessage = @"\cf2";
                        break;
                    case "warning":
                        consoleMessage = @"\cf3";
                        break;
                    case "info":
                        consoleMessage = @"\cf4";
                        break;
                    default:
                        consoleMessage = @"\cf1";
                        break;
                }
                consoleMessage += @"\b " + one.Timestamp + @"\b0";
                if (!one.ColorAll) consoleMessage += @"\cf1";
                consoleMessage += @"\tab " + one.Content + @"\par";
                ConsoleRTFContents += consoleMessage;
                Log.LogMessages.Remove(one);
            }
        }
    }
}
