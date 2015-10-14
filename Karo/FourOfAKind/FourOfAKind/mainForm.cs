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

        private Map PKMap;
        private Point mapOffset = new Point(20, 20);

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

            PKMap = new Map();
            PKMap.Zoom = 2;

            PKMap.Intersections.Add(new Intersection(1, "Test01", new PointDouble(0, 0)));
            PKMap.Intersections.Add(new Intersection(2, "Test02", new PointDouble(20, 0)));
            PKMap.Intersections.Add(new Intersection(3, "Test03", new PointDouble(40, 0)));
            PKMap.Intersections.Add(new Intersection(4, "Test04", new PointDouble(0, 20)));
            PKMap.Intersections.Add(new Intersection(5, "Test05", new PointDouble(0, 40)));
            PKMap.Intersections.Add(new Intersection(6, "Test06", new PointDouble(60, 60)));

            PKMap.Tracks.Add(new Track(1, "", 1, 2));
            PKMap.Tracks.Add(new Track(2, "", 2, 3));
            PKMap.Tracks.Add(new Track(3, "", 3, 6, new PointDouble[] { new PointDouble(60, 10), new PointDouble(65, 15), new PointDouble(68, 20), new PointDouble(70, 30), new PointDouble(68, 40), new PointDouble(65, 50) }));
            PKMap.Tracks.Add(new Track(2, "", 5, 6));

            PKMap.SaveToDir(Application.StartupPath);
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
                    graphicsObj.DrawString("FPS: " + String.Format("{0:0.00}", 1000.0 / (double)frameTime), myFont, myBrush, 0, 0);
                }

                Pen interPen = new Pen(Color.FromArgb(0,90,255), 2);
                Font interFont = new System.Drawing.Font("Consolas", 10.0f, FontStyle.Regular, GraphicsUnit.Pixel);
                foreach (Intersection one in PKMap.Intersections)
                {
                    Point spot = one.Location.getDrawingPoint(mapOffset, PKMap.Zoom);

                    graphicsObj.DrawEllipse(interPen, new Rectangle(spot.X-2, spot.Y-2, 4, 4));
                    graphicsObj.DrawString(one.Name, interFont, myBrush, spot.X+2, spot.Y+2);
                }
                interFont.Dispose();
                interPen.Dispose();


                Pen trackPen = new Pen(Color.FromArgb(30, 30, 30), 1);
                foreach (Track one in PKMap.Tracks)
                {
                    List<Point> points = new List<Point>();
                    points.Add(PKMap.getIntersectionByID(one.Start).Location.getDrawingPoint(mapOffset, PKMap.Zoom));
                    foreach (PointDouble waypoint in one.Waypoints)
                    {
                        points.Add(waypoint.getDrawingPoint(mapOffset, PKMap.Zoom));
                    }
                    points.Add(PKMap.getIntersectionByID(one.End).Location.getDrawingPoint(mapOffset, PKMap.Zoom));

                    graphicsObj.DrawLines(trackPen, points.ToArray());
                }
                trackPen.Dispose();


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

        private void panelCanvas_MouseClick(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
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
