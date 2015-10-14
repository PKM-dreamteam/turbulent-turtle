using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;

namespace FourOfAKind.MapClasses
{
    public class PointDouble
    {
        private static Point zeroOffset = new Point(0,0);
        public double X;
        public double Y;

        public PointDouble() { X = 0; Y = 0; }

        public PointDouble(double _X, double _Y)
        {
            X = _X;
            Y = _Y;
        }

        public Point getDrawingPoint(Point offset, double Zoom = 1.0)
        {
            double tX = this.X * Zoom;
            double tY = this.Y * Zoom;
            if (offset == null)
            {
                return new Point((int)Math.Round(tX), (int)Math.Round(tY));
            }
            else
            {
                Point result = new Point((int)Math.Round(tX), (int)Math.Round(tY));
                result.X += offset.X;
                result.Y += offset.Y;
                return result;
            }
        }
    }
}
