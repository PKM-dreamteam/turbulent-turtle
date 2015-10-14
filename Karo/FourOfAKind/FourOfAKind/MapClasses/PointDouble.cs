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

        public Point getDrawingPoint(Point drawingOffset, PointDouble offset, double Zoom = 1.0)
        {
            double tX = this.X * Zoom;
            double tY = this.Y * Zoom;
            if (offset == null)
            {
                return new Point((int)Math.Round(tX), (int)Math.Round(tY));
            }
            else
            {
                offset = offset.Mul(Zoom);
                Point result = new Point((int)Math.Round(tX), (int)Math.Round(tY));
                result.X += drawingOffset.X + (int)Math.Round(offset.X);
                result.Y += drawingOffset.Y + (int)Math.Round(offset.Y);
                return result;
            }
        }

        public double CalcDistance(PointDouble other)
        {
            double dX = other.X - this.X;
            double dY = other.Y - this.Y;

            return Math.Sqrt(dX * dX + dY * dY);
        }

        public PointDouble Add(PointDouble other)
        {
            double newX = this.X + other.X;
            double newY = this.Y + other.Y;

            return new PointDouble(newX, newY);
        }

        public PointDouble Mul(double scalar)
        {
            double newX = this.X * scalar;
            double newY = this.Y * scalar;

            return new PointDouble(newX, newY);
        }
    }
}
