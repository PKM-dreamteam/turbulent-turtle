using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Server
{
    public class DataPack
    {
        public byte length;
        public byte deviceId;
        public long timestamp;
   
        public Int32 x;
        public Int32 y;
        public Int32 z;
        public Int32 velocity;

        public byte[] data;
        

        public DataPack(byte _deviceId, long _timestamp, Int32 _x, Int32 _y, Int32 _z, Int32 _velocity, byte[] _data=null)
        {
            length = 1 + 1 + 8 + 4 * 4;
            deviceId = _deviceId;
            timestamp = _timestamp;
            x = _x;
            y = _y;
            z = _z;
            velocity = _velocity;

            if(_data != null)
            {
                data = _data;
                length += (byte)data.Length;
            }
            else
            {
                data = new byte[0];
            }
        }


        public DataPack(byte[] _data)
        {
            length = _data[0];
            deviceId = _data[1];

            byte[] dataTimeBytes = new byte[8];
            byte[] xBytes = new byte[4];
            byte[] yBytes = new byte[4];
            byte[] zBytes = new byte[4];
            byte[] velBytes = new byte[4];
            data = new byte[length-26];
            
            Array.Copy(_data, 2, dataTimeBytes, 0, 8);
            Array.Copy(_data, 10, xBytes, 0, 4);
            Array.Copy(_data, 14, yBytes, 0, 4);
            Array.Copy(_data, 18, zBytes, 0, 4);
            Array.Copy(_data, 22, velBytes, 0, 4);
            Array.Copy(_data, 26, data, 0, data.Length);
  
            
            timestamp = BitConverter.ToInt64(dataTimeBytes, 0);

            x = BitConverter.ToInt32(xBytes, 0);
            y = BitConverter.ToInt32(yBytes, 0);
            z = BitConverter.ToInt32(zBytes, 0);
            velocity = BitConverter.ToInt32(velBytes, 0);
            

        }

        public byte[] ToByteArray()
        {
            byte[] dataBytes = new byte[length];

            byte[] lengthBytes = BitConverter.GetBytes(length);
            byte[] deviceID = BitConverter.GetBytes(deviceId);
            byte[] xBytes = BitConverter.GetBytes(x);
            byte[] yBytes = BitConverter.GetBytes(y);
            byte[] zBytes = BitConverter.GetBytes(z);
            byte[] velBytes = BitConverter.GetBytes(velocity);
            byte[] dataTimeBytes = BitConverter.GetBytes(timestamp);


            dataBytes[0] = lengthBytes[0];
            dataBytes[1] = deviceID[0];

            Array.Copy(dataTimeBytes, 0, dataBytes, 2, dataTimeBytes.Length);
            Array.Copy(xBytes, 0, dataBytes, 10, xBytes.Length);
            Array.Copy(yBytes, 0, dataBytes, 14, yBytes.Length);
            Array.Copy(zBytes, 0, dataBytes, 18, zBytes.Length);
            Array.Copy(velBytes, 0, dataBytes, 22, velBytes.Length);
            Array.Copy(data, 0, dataBytes, 26, data.Length);

            
            return dataBytes;
        }
    }

}
