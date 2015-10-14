using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows.Forms;
using System.Xml;
using FourOfAKind.MapClasses;

namespace FourOfAKind.Navigation
{
    public class Map
    {
        public List<Intersection> Intersections;
        public List<Track> Tracks;
        public double Zoom;

        public Map()
        {
            this.Zoom = 1.0;
            this.Intersections = new List<Intersection>();
            this.Tracks = new List<Track>();
        }

        public Intersection getIntersectionByID(int ID)
        {
            foreach (Intersection one in this.Intersections)
            {
                if (one.ID == ID) return one;
            }
            return null;
        }

        public bool SaveToDir(string dirname)
        {
            try
            {
                List<string> intersTxt = new List<string>();
                List<string> trakcsTxt = new List<string>();

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

                foreach (Track one in this.Tracks)
                {
                    List<string> temp = new List<string>();

                    temp.Add("T");
                    temp.Add(XmlConvert.ToString(one.ID));
                    temp.Add(one.Name);
                    temp.Add(XmlConvert.ToString(one.Start));
                    temp.Add(XmlConvert.ToString(one.End));

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

                File.WriteAllLines(Path.Combine(dirname, "intersections.txt"), intersTxt);
                File.WriteAllLines(Path.Combine(dirname, "tracks.txt"), trakcsTxt);
            }
            catch (Exception e)
            {
                MessageBox.Show("Błąd zapisywania mapy:\n"+e.Message);
                return false;
            }

            return false;
        }
    }
}
