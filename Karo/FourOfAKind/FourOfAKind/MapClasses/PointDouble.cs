using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;

namespace FourOfAKind.MapClasses
{
    class PointDouble
    {
        public double X;
        public double Y;

        public PointDouble() { X = 0; Y = 0; }

        public PointDouble(double _X, double _Y)
        {
            X = _X;
            Y = _Y;
        }

        public Point getDrawingPoint()
        {
            return new Point((int)Math.Round(this.X), (int)Math.Round(this.Y));
        }
    }
}
