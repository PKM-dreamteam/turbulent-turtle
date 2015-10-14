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
using System.IO;

// ---- Nasze klasy
using FourOfAKind.MapClasses;
using FourOfAKind.Navigation;

namespace FourOfAKind
{
    public partial class mainForm : Form
    {
        Stopwatch frameWatch;
        Stopwatch drawWatch;

        private long frameTime = 0;
        private long drawTime = 0;
        private long framesDrawn = 0;
        private long errorCount = 0;
        private bool redrawing = false;
        private Point drawMiddle = new Point(0, 0);

        private Map PKMap;  // Główny obiekt mapy

        private Point mapPanStart = new Point(0, 0);

        /// <summary>
        /// Redukuje migotanie podczas rysowania
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
            drawWatch = new Stopwatch();

            Log.Console = new ConsoleForm(this);
            Log.Console.Show();
            Log.AddToConsole("Aplikacja uruchomiona");

            PKMap = new Map();
            PKMap.LoadFromFile(Path.Combine(Application.StartupPath, "lastmap.txt"));
            PKMap.RecalcBounds(panelCanvas.Size);

            this.panelCanvas.MouseWheel += panelCanvas_MouseWheel;
        }

        /// <summary>
        /// Rzeczy do wykonania podczas zamykania programu
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void mainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            PKMap.SaveToFile(Path.Combine(Application.StartupPath, "lastmap.txt"));
        }

        /// <summary>
        /// W tej procedurze dokonuje się rysowanie mapy
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_Paint(object sender, PaintEventArgs e)
        {
            if (errorCount > 5) return;
            try
            {
                redrawing = true;
                drawWatch = Stopwatch.StartNew();
                Graphics graphicsObj;
                Bitmap one_frame = new Bitmap(panelCanvas.Width, panelCanvas.Height);
                graphicsObj = Graphics.FromImage(one_frame);
                graphicsObj.Clear(Color.White);
                graphicsObj.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

                drawMiddle = new Point((int)(Math.Round(panelCanvas.Width / 2.0)), (int)(Math.Round(panelCanvas.Height / 2.0)));

                Pen myPen = new Pen(Color.Black, 1);
                Font myFont = new System.Drawing.Font("Consolas", 11.0f, FontStyle.Regular, GraphicsUnit.Pixel);
                Brush myBrush = new SolidBrush(Color.Black);

                if(frameTime>0)
                {
                    graphicsObj.DrawString("FPS: " + String.Format("{0:0.00}", 1000.0 / (double)frameTime) + " / drawTime: " + drawTime + " / Zoom: "+PKMap.Zoom, myFont, myBrush, 0, 0);
                }

                if (PKMap.isReady)
                {
                    //  Punkt początku mapy. Koordynaty 0,0
                    int mapZeroSize = 3;
                    PointDouble mapCenter = new PointDouble(0, 0);
                    graphicsObj.DrawRectangle(myPen, mapCenter.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom).X - mapZeroSize, mapCenter.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom).Y - mapZeroSize, 2 * mapZeroSize, 2 * mapZeroSize);


                    Pen interPen = new Pen(Color.FromArgb(0, 90, 255), 2);
                    Font interFont = new System.Drawing.Font("Consolas", 10.0f, FontStyle.Regular, GraphicsUnit.Pixel);
                    foreach (Intersection one in PKMap.Intersections)
                    {
                        Point spot = one.Location.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom);

                        graphicsObj.DrawEllipse(interPen, new Rectangle(spot.X - 2, spot.Y - 2, 4, 4));
                        graphicsObj.DrawString(one.Name, interFont, myBrush, spot.X + 2, spot.Y + 2);
                    }
                    interFont.Dispose();
                    interPen.Dispose();


                    Pen trackPen = new Pen(Color.FromArgb(30, 30, 30), 1);
                    // wyświetlanie istniejących torów
                    foreach (Track one in PKMap.Tracks)
                    {
                        List<Point> points = new List<Point>();
                        points.Add(PKMap.getIntersectionByID(one.Start).Location.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));
                        foreach (PointDouble waypoint in one.Waypoints)
                        {
                            points.Add(waypoint.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));
                        }
                        points.Add(PKMap.getIntersectionByID(one.End).Location.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));

                        graphicsObj.DrawLines(trackPen, points.ToArray());
                    }

                    // Wyświetlanie toru w trakcie edycji
                    if (PKMap.TrackStartID >= 0)
                    {
                        List<Point> points = new List<Point>();
                        points.Add(PKMap.getIntersectionByID(PKMap.TrackStartID).Location.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));
                        foreach (PointDouble waypoint in PKMap.TrackPoints)
                        {
                            points.Add(waypoint.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));
                        }
                        points.Add(PKMap.RealCursorPos.getDrawingPoint(drawMiddle, PKMap.Offset, PKMap.Zoom));

                        graphicsObj.DrawLines(trackPen, points.ToArray());
                    }

                    trackPen.Dispose();

                    //  Middle Point
                    int crossSize = 10;
                    graphicsObj.DrawLine(myPen, drawMiddle.X, drawMiddle.Y - crossSize, drawMiddle.X, drawMiddle.Y + crossSize);
                    graphicsObj.DrawLine(myPen, drawMiddle.X - crossSize, drawMiddle.Y, drawMiddle.X + crossSize, drawMiddle.Y);

                    //  Cursor position display
                    graphicsObj.DrawEllipse(myPen, drawMiddle.X + PKMap.CursorPos.X - 2, drawMiddle.Y + PKMap.CursorPos.Y - 2, 4, 4);
                    graphicsObj.DrawString(String.Format("{0:0.00}", PKMap.RealCursorPos.X) + ";" + String.Format("{0:0.00}", PKMap.RealCursorPos.Y), myFont, myBrush, drawMiddle.X + PKMap.CursorPos.X, drawMiddle.Y + PKMap.CursorPos.Y - 12);
                }

                e.Graphics.DrawImage(one_frame, 0, 0);
                myPen.Dispose();
                myBrush.Dispose();
                myFont.Dispose();
                graphicsObj.Dispose();
                one_frame.Dispose();


                drawWatch.Stop();
                drawTime = drawWatch.ElapsedMilliseconds;

                frameWatch.Stop();
                frameTime = frameWatch.ElapsedMilliseconds;
                framesDrawn++;
                frameWatch = Stopwatch.StartNew();
                errorCount = 0;
            }
            catch (Exception ex)
            {
                Log.AddToConsole("Błąd rysowania mapy (line " + ex.LineNumber().ToString() + "): " + ex.Message, "error");
                errorCount++;

                if (errorCount > 5)
                { 
                    mainTimer.Enabled = false;
                    Log.AddToConsole("Wstrzymano rysowanie mapy z powodu wielokrotnego błędu", "info");
                }
            }
            redrawing = false;
        }

        /// <summary>
        /// Procedura obsługuje kliknięcia myszy w obszarze mapy. (kliknięcie to wciśniecie i puszczenie klawisza. Dla wciśnieć patrz MouseDown niżej...)
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_MouseClick(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                Log.AddToConsole("MouseClick: Left", "info");
                if (rbAddIntersection.Checked)
                {
                    PKMap.Intersections.Add(new Intersection(PKMap.NextIntersectionID(), txtAddName.Text, PKMap.RealCursorPos));
                }

                if(rbAddTrack.Checked)
                {
                    if (PKMap.TrackStartID == -1)
                    {
                        double min = 2;
                        Intersection best = null;
                        foreach (Intersection one in PKMap.Intersections)
                        {
                            double dist = one.Location.CalcDistance(PKMap.RealCursorPos);
                            if (dist < min)
                            {
                                best = one;
                                min = dist;
                            }
                        }

                        if ( best != null )
                        {
                            PKMap.TrackStartID = best.ID;
                        }
                    }
                    else
                    {
                        double min = 2;
                        Intersection best = null;
                        foreach (Intersection one in PKMap.Intersections)
                        {
                            if (one.ID == PKMap.TrackStartID) continue;
                            double dist = one.Location.CalcDistance(PKMap.RealCursorPos);
                            if (dist < min)
                            {
                                best = one;
                                min = dist;
                            }
                        }

                        if (best != null)
                        {
                            PKMap.Tracks.Add(new Track(PKMap.NextTrackID(), txtAddName.Text, PKMap.TrackStartID, best.ID, PKMap.TrackPoints.Count, PKMap.TrackPoints.ToArray()));
                            PKMap.TrackStartID = -1;
                            PKMap.TrackPoints = new List<PointDouble>();
                        }
                        else
                        {
                            PKMap.TrackPoints.Add(PKMap.RealCursorPos);
                        }
                    }
                }

                if(rbRemove.Checked)
                {
                    double min = 2;
                    Intersection bestInter = null;
                    foreach (Intersection one in PKMap.Intersections)
                    {
                        double dist = one.Location.CalcDistance(PKMap.RealCursorPos);
                        if (dist < min)
                        {
                            bestInter = one;
                            min = dist;
                        }
                    }

                    if(bestInter != null)
                    {
                        for (int i = 0; i<PKMap.Tracks.Count; i++)
                        {
                            Track one = PKMap.Tracks[i];
                            if(one.Start==bestInter.ID || one.End == bestInter.ID)
                            {
                                PKMap.Tracks.RemoveAt(i);
                                i--;
                            }
                        }
                        PKMap.Intersections.Remove(bestInter);
                    }

                    min = 2;
                    Track bestTrack = null;
                    foreach (Track one in PKMap.Tracks)
                    {
                        foreach (PointDouble waypoint in one.Waypoints)
                        {
                            double dist = waypoint.CalcDistance(PKMap.RealCursorPos);
                            if (dist < min)
                            {
                                bestTrack = one;
                                min = dist;
                            }
                        }
                    }

                    if (bestTrack != null)
                    {
                        while (redrawing) Application.DoEvents();
                        PKMap.Tracks.Remove(bestTrack);
                    }

                }
            }

            if(e.Button == MouseButtons.Right)
            {
                Log.AddToConsole("MouseClick: Right", "info");
                if (rbAddTrack.Checked)
                {
                    if (PKMap.TrackPoints.Count > 0)
                    {
                        PKMap.TrackPoints.RemoveAt(PKMap.TrackPoints.Count - 1);
                    }
                    else
                    {
                        PKMap.TrackStartID = -1;
                        PKMap.TrackPoints = new List<PointDouble>();
                    }
                }
            }
        }

        /// <summary>
        /// Obsługa kółka myszy do zmiany zbliżenia
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_MouseWheel(object sender, MouseEventArgs e)
        {
            double multi = 0.2;
            PKMap.Zoom += e.Delta / 120 * multi;

            if (PKMap.Zoom < 0.1) PKMap.Zoom = 0.2;
        }

        /// <summary>
        /// Procedura nadająca focus panelowi. Niezbędna do prawidłowego przechwycenia kółka myszy
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_MouseHover(object sender, EventArgs e)
        {
            panelCanvas.Focus();
        }

        /// <summary>
        /// Wywoływana podczas każdego przemieszczenia myszy nad panelem przelicza przesunięcie
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_MouseMove(object sender, MouseEventArgs e)
        {
            PKMap.SetCursorPos(new Point(e.Location.X - drawMiddle.X, e.Location.Y - drawMiddle.Y));

            if(e.Button == MouseButtons.Right)
            {
                PointDouble change = new PointDouble(e.Location.X - mapPanStart.X, e.Location.Y - mapPanStart.Y);
                change = change.Mul(1.0/PKMap.Zoom);
                PKMap.Offset = PKMap.TempOffset.Add(change);
            }
        }

        /// <summary>
        /// Wykonuje się w momencie wciśnięcia przycisków myszy i pozwala na zapisanie danych przed akcjami typu przytrzymaj i przeciagnij
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void panelCanvas_MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Right)
            {
                //  Zapamietanie wartości offsetu do przyszłych obliczeń podczas przesuwania widoku
                mapPanStart = e.Location;
                PKMap.TempOffset = PKMap.Offset;
            }
        }

        /// <summary>
        /// Główny timer wymuszajacy przerysowanie panelu panelCanvas co ok. 30 ms
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void mainTimer_Tick(object sender, EventArgs e)
        {
            if(!redrawing)
                panelCanvas.Refresh();
        }

        /// <summary>
        /// Zapisywanie aktualnej mapy do pliku
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void btnSave_Click(object sender, EventArgs e)
        {
            saveFileDialog.InitialDirectory = Application.StartupPath;

            if (saveFileDialog.ShowDialog() == DialogResult.OK)
            {
                PKMap.SaveToFile(saveFileDialog.FileName);
            }
        }

        /// <summary>
        /// Wczytuje mapę i zastępuje aktuelnie wczytaną
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void btnLoad_Click(object sender, EventArgs e)
        {
            openFileDialog.InitialDirectory = Application.StartupPath;

            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                PKMap.LoadFromFile(openFileDialog.FileName);
                PKMap.RecalcBounds(panelCanvas.Size);
            }
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
