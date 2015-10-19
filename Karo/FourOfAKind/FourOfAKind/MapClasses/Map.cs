using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows.Forms;
using System.Xml;
using FourOfAKind.MapClasses;
using System.Drawing;

namespace FourOfAKind.Navigation
{
    public class Map
    {
        public bool isReady = true;
        public List<Intersection> Intersections;
        public List<Track> Tracks;
        public double Zoom;
        public PointDouble Offset = new PointDouble(-200, -200);
        public PointDouble TempOffset = new PointDouble(-200, -200);
        public Point CursorPos = Point.Empty;
        public PointDouble RealCursorPos = new PointDouble(0,0);
        
        public int TrackStartID = -1;
        public List<PointDouble> TrackPoints = new List<PointDouble>();

        public Map()
        {
            this.Zoom = 1.0;
            this.Intersections = new List<Intersection>();
            this.Tracks = new List<Track>();
        }

        /// <summary>
        /// Znajduje węzeł po ID. Zwraca null jeżeli węzeł nie istnieje
        /// </summary>
        /// <param name="ID"></param>
        /// <returns></returns>
        public Intersection getIntersectionByID(int ID)
        {
            foreach (Intersection one in this.Intersections)
            {
                if (one.ID == ID) return one;
            }
            return null;
        }

        /// <summary>
        /// Ustawia wartość pozycji kursora i przelicza ją na współrzędne w jednostkach  mapy
        /// </summary>
        /// <param name="input"></param>
        public void SetCursorPos(Point input)
        {
            CursorPos = input;
            RealCursorPos = new PointDouble(CursorPos.X / Zoom - Offset.X, CursorPos.Y / Zoom - Offset.Y);
        }

        public void RecalcBounds(Size canvasSize)
        {
            double sumX = 0;
            int numX = 0;
            double sumY = 0;
            int numY = 0;

            double top = 0;
            double bottom = 0;
            double left = 0;
            double right = 0;

            foreach (Intersection one in this.Intersections)
            {
                sumX += one.Location.X;
                sumY += one.Location.Y;
                numX++;
                numY++;

                if (one.Location.X < left) left = one.Location.X;
                if (one.Location.X > right) right = one.Location.X;
                if (one.Location.Y < top) top = one.Location.Y;
                if (one.Location.Y > bottom) bottom = one.Location.Y;
            }

            this.Offset = new PointDouble(-sumX / numX, -sumY / numY);  

            double width = right - left + 10;
            double height = bottom - top + 10;

            if(width>=height)
            {
                this.Zoom = Math.Floor((double)canvasSize.Width / width);
            }
            else
            {
                this.Zoom = Math.Floor((double)canvasSize.Height / height);
            }
        }

        /// <summary>
        /// Pobiera następne ID dla węzła. Jeżeli to pierwszy węzeł nadaje mu ID = 1
        /// </summary>
        /// <returns></returns>
        public int NextIntersectionID()
        {
            if (this.Intersections.Count > 0)
                return this.Intersections.Last().ID + 1;
            else
                return 1;
        }

        /// <summary>
        /// Pobiera następne ID dla toru. Jeżeli to pierwszy tor nadaje mu ID = 1
        /// </summary>
        /// <returns></returns>
        public int NextTrackID()
        {
            if (this.Tracks.Count > 0)
                return this.Tracks.Last().ID + 1;
            else
                return 1;
        }

        /// <summary>
        /// Zapis do pliku. Dokumentacja formatu dostępna w folderze Karo/DokumentacjaMapy
        /// </summary>
        /// <param name="filename"></param>
        /// <returns></returns>
        public bool SaveToFile(string filename)
        {
            try
            {
                this.isReady = false;
                List<string> intersTxt = new List<string>();
                List<string> trakcsTxt = new List<string>();

                //  Tworzenie pliku węzłów
                //  Każdy węzeł zaczyna się od I a następnie podane są jego dane
                foreach (Intersection one in this.Intersections)
                {
                    List<string> temp = new List<string>();

                    temp.Add("I");
                    temp.Add(XmlConvert.ToString(one.ID));
                    temp.Add(one.Name);
                    temp.Add(XmlConvert.ToString(one.Location.X));
                    temp.Add(XmlConvert.ToString(one.Location.Y));

                    intersTxt.Add(String.Join(",", temp.ToArray()));
                }

                //  Tworzenie pliku torów
                //  Linia zaczynajaca się od T oznacza początek danych toru
                //  Linia zaczynajaca się od W oznacza punkt pośredni toru
                //  Tor kończy się wraz z rozpoczęciem innego toru od linii T, pustą linią lub końcem pliku
                foreach (Track one in this.Tracks)
                {
                    List<string> temp = new List<string>();

                    temp.Add("T");
                    temp.Add(XmlConvert.ToString(one.ID));
                    temp.Add(one.Name);
                    temp.Add(XmlConvert.ToString(one.Start));
                    temp.Add(XmlConvert.ToString(one.End));
                    temp.Add(XmlConvert.ToString(one.Waypoints.Length));

                    trakcsTxt.Add(String.Join(",", temp.ToArray()));

                    foreach (PointDouble waypoint in one.Waypoints)
                    {
                        List<string> tempWay = new List<string>();

                        tempWay.Add("W");
                        tempWay.Add(XmlConvert.ToString(waypoint.X));
                        tempWay.Add(XmlConvert.ToString(waypoint.Y));

                        trakcsTxt.Add(String.Join(",", tempWay.ToArray()));
                    }
                }

                //  Oddzielenie węzłów od torów pusta linią
                intersTxt.Add("");
                //  Dodanie torów do treści węzłów
                intersTxt.AddRange(trakcsTxt);

                //  Zapis węzłów i torów do wspólnego pliku
                File.WriteAllLines(filename, intersTxt);
                this.isReady = true;
                return true;
            }
            catch (Exception e)
            {
                Log.AddToConsole("Błąd zapisywania mapy (line " + e.LineNumber().ToString() + "): " + e.Message, "error");
                this.isReady = true;
                return false;
            }
        }

        /// <summary>
        /// Odczyt z pliku. Dokumentacja formatu dostępna w folderze Karo/DokumentacjaMapy
        /// </summary>
        /// <param name="filename"></param>
        /// <returns></returns>
        public bool LoadFromFile(string filename)
        {
            try
            {
                this.isReady = false;
                string[] readText = File.ReadAllLines(filename);

                this.Intersections = new List<Intersection>();
                this.Tracks = new List<Track>();
               
                for (int i = 0; i < readText.Length; i++)
                {
                    string lineT = readText[i].Trim();
                    if(lineT.Length>0)
                    {
                        string[] split = lineT.Split((",").ToArray());

                        switch (split[0])
                        {
                            case "I":
                                if (split.Length == 5)
                                {
                                    this.Intersections.Add(new Intersection(XmlConvert.ToInt32(split[1]), split[2], new PointDouble(XmlConvert.ToDouble(split[3]), XmlConvert.ToDouble(split[4]))));
                                }
                                break;
                            case "T":
                                if (split.Length == 5)
                                {
                                    this.Tracks.Add(new Track(XmlConvert.ToInt32(split[1]), split[2], XmlConvert.ToInt32(split[3]), XmlConvert.ToInt32(split[4])));
                                }
                                else if (split.Length == 6)
                                {
                                    this.Tracks.Add(new Track(XmlConvert.ToInt32(split[1]), split[2], XmlConvert.ToInt32(split[3]), XmlConvert.ToInt32(split[4]), XmlConvert.ToInt32(split[5])));

                                    for(int j = 0; j < XmlConvert.ToInt32(split[5]); j++)
                                    {
                                        i++;
                                        if (i >= readText.Length) break;

                                        string[] splitW = readText[i].Trim().Split((",").ToArray());
                                        if (splitW.Length > 0)
                                        {
                                            if (splitW[0] == "W")
                                            {
                                                this.Tracks.Last().Waypoints[j] = new PointDouble(XmlConvert.ToDouble(splitW[1]), XmlConvert.ToDouble(splitW[2]));
                                            }
                                            else
                                            {
                                                break;
                                            }
                                        }
                                        else
                                        {
                                            break;
                                        }
                                    }
                                }
                                break;
                        }
                    }
                }

                this.isReady = true;
                return true;
            }
            catch (Exception e)
            {
                Log.AddToConsole("Błąd wczytywania mapy (line " + e.LineNumber().ToString() + "): " + e.Message, "error");
                this.isReady = true;
                return false;
            }
        }
    }
}
