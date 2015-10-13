using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;

// ---- Nasze klasy
using FourOfAKind.MapClasses;
using FourOfAKind.Navigation;

namespace FourOfAKind
{
    public partial class mainForm : Form
    {
        private ConsoleForm Console = null;
        Stopwatch frameWatch;
        private long frameTime = 0;
        private long framesDrawn = 0;
        public List<ConsoleMessage> LogMessages = new List<ConsoleMessage>();

        /// <summary>
        /// Zapobiega migotaniu podczas rysowania
        /// </summary>
        protected override CreateParams CreateParams
        {
            get
            {
                CreateParams cp = base.CreateParams;
                cp.ExStyle |= 0x02000000;
                return cp;
            }
        }

        public mainForm()
        { 
            InitializeComponent();

            frameWatch = new Stopwatch();

            Console = new ConsoleForm(this);
            Console.Show();
            AddToConsole("Aplikacja uruchomiona");
            //Console.AddToConsole("Test wiadomości 1");
            //Console.AddToConsole("Test wiadomości 1", "default");
            //Console.AddToConsole("Test wiadomości 1", "error");
            //Console.AddToConsole("Test wiadomości 1", "warning", false);
            //Console.AddToConsole("Test wiadomości 1", "info");
        }

        public void AddToConsole(string message, string type = "default", bool colorAll = true)
        {
            LogMessages.Add(new ConsoleMessage(message, type, colorAll));
            try
            {
                Console.RefreshConsole();
            }
            catch { }
        }

        /// <summary>
        /// W tej procedurze dokonuje się rysowanie mapy
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_Paint(object sender, PaintEventArgs e)
        {
            try
            {
                Graphics graphicsObj;
                Bitmap one_frame = new Bitmap(panelCanvas.Width, panelCanvas.Height);
                graphicsObj = Graphics.FromImage(one_frame);
                graphicsObj.Clear(Color.White);
                graphicsObj.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

                Pen myPen = new Pen(Color.Black, 1);
                Font myFont = new System.Drawing.Font("Consolas", 11.0f, FontStyle.Regular, GraphicsUnit.Pixel);
                Brush myBrush = new SolidBrush(Color.Black);

                if(frameTime>0)
                {
                    graphicsObj.DrawString("FPS: " + String.Format("{0:0.00}", 1000.0 / (double)frameTime), myFont, myBrush, 10, 10);
                }
                









                e.Graphics.DrawImage(one_frame, 0, 0);
                myPen.Dispose();
                myBrush.Dispose();
                myFont.Dispose();
                graphicsObj.Dispose();
                one_frame.Dispose();


                frameWatch.Stop();
                frameTime = frameWatch.ElapsedMilliseconds;
                framesDrawn++;
                frameWatch = Stopwatch.StartNew();
            }
            catch (Exception ex)
            {
                AddToConsole("Błąd rysowania mapy (line "+ ex.LineNumber().ToString()+ "): "+ex.Message, "error");
            }
        }

        private void mainTimer_Tick(object sender, EventArgs e)
        {
            panelCanvas.Refresh();
        }
    }

    /// <summary>
    /// Klasa rozszerzenia pozwalająca na pobranie numeru linii dowolnego błędu.
    /// Użycie:
    ///     try
    ///     {
    ///         //Do your code here
    ///     }
    ///     catch (Exception e)
    ///     {
    ///         int linenum = e.LineNumber();
    ///     }
    /// </summary>
    public static class ExceptionHelper
    {
        public static int LineNumber(this Exception e)
        {
            int linenum = 0;
            try
            {
                //linenum = Convert.ToInt32(e.StackTrace.Substring(e.StackTrace.LastIndexOf(":line") + 5));
                //For Localized Visual Studio ... In other languages stack trace  doesn't end with ":Line 12"
                linenum = Convert.ToInt32(e.StackTrace.Substring(e.StackTrace.LastIndexOf(' ')));
            }
            catch
            {
                //Stack trace is not available!
            }
            return linenum;
        }
    }
}
