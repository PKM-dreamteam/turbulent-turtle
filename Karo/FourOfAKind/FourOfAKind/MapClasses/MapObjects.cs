using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using FourOfAKind.MapClasses;

namespace FourOfAKind.Navigation
{
    public class Intersection
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

    public class Track
    {
        public int ID;
        public string Name;
        public int Start;
        public int End;

        public PointDouble[] Waypoints;

        public Track()
        {
            this.ID = -1;
            this.Name = "";
            this.Start = -1;
            this.End = -1;
            this.Waypoints = new PointDouble[] { };
        }

        public Track(int _ID, string _Name, int _Start, int _End, int _waypointsCount = 0, PointDouble[] _Waypoints = null)
        {
            this.ID = _ID;
            this.Name = _Name;
            this.Start = _Start;
            this.End = _End;
            
            this.Waypoints = new PointDouble[_waypointsCount];

            if (_Waypoints != null) this.Waypoints = _Waypoints;
        }
    }
}
