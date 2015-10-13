using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using FourOfAKind.MapClasses;

namespace FourOfAKind.Navigation
{
    class Intersection
    {
        public int ID;
        public string Name;
        public PointDouble Location;
        public List<Track> Tracks;
        
        public Intersection()
        {
            this.ID = -1;
            this.Name = "";
            this.Location = new PointDouble();
            this.Tracks = new List<Track>();
        }
        
        public Intersection(int _ID, string _Name, PointDouble _Location, List<Track> _Tracks = null)
        {
            this.ID = _ID;
            this.Name = _Name;
            this.Location = _Location;

            if (_Tracks == null)
                this.Tracks = new List<Track>();
            else
                this.Tracks = _Tracks;
        }
    }

    class Track
    {
        public int ID;
        public string Name;
        public PointDouble Start;
        public PointDouble End;

        public List<PointDouble> Waypoints;

        public Track()
        {
            this.ID = -1;
            this.Name = "";
            this.Start = new PointDouble();
            this.End = new PointDouble();

            this.Waypoints = new List<PointDouble>();
        }

        public Track(int _ID, string _Name, PointDouble _Start, PointDouble _End, List<PointDouble> _Waypoints = null)
        {
            this.ID = _ID;
            this.Name = _Name;
            this.Start = _Start;
            this.End = _End;


            if (_Waypoints == null)
                this.Waypoints = new List<PointDouble>();
            else
                this.Waypoints = _Waypoints;
        }
    }
}
