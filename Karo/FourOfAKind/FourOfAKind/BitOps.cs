using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FourOfAKind
{
    class BitOps
    {
        public static string ConvertToHexString(byte input)
        {
            try
            {
                return input.ToString("X") + "h";
            }
            catch (Exception e)
            {

            }

            return "0x0";
        }

        public static void Set(ref byte aByte, int pos, bool value)
        {
            if (value)
            {
                //left-shift 1, then bitwise OR
                aByte = (byte)(aByte | (1 << pos));
            }
            else
            {
                //left-shift 1, then take complement, then bitwise AND
                aByte = (byte)(aByte & ~(1 << pos));
            }
        }

        public static bool Get(byte aByte, int pos)
        {
            //left-shift 1, then bitwise AND, then check for non-zero
            return ((aByte & (1 << pos)) != 0);
        }
    }
}
