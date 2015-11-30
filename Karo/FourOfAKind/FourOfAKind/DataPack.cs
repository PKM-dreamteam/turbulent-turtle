using System;
using System.Net;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FourOfAKind
{
    public class DataPack
    {
        public byte length;
        public byte deviceId;
        public long timestamp;

        public int x;
        public int y;
        public int z;
        public int velocity;

        public byte[] data;


        public DataPack(byte _deviceId, long _timestamp, int _x, int _y, int _z, int _velocity, byte[] _data = null)
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

        public static void PrintBits(byte [] input, string title = "")
        {
            string dataStr = "";
            if (BitConverter.IsLittleEndian)
            {
                for(int j = input.Length - 1; j >= 0; j--)
                {
                    for (int i = 7; i >= 0; i--)
                    {
                        if (BitOps.Get(input[j], i))
                            dataStr += "1";
                        else
                            dataStr += "0";
                    }
                    dataStr += "\n";
                }
            }
            else
            {
                for (int j = 0; j < input.Length; j++)
                {
                    for (int i = 0; i < 8; i++)
                    {
                        if (BitOps.Get(input[j], i))
                            dataStr += "1";
                        else
                            dataStr += "0";
                    }
                    dataStr += "\n";
                }
            }

            if (title != "")
                Console.WriteLine(title + ":\n");
            else
                Console.WriteLine("Data:\n");

            Console.WriteLine(dataStr);
            Console.WriteLine("--------------------------------------------------------------------");
        }
    
        public static void PrintHex(byte[] input, string title = "")
        {
            string dataStr = "";
            for (int j = 0; j < input.Length; j++)
            {
                dataStr += "0x" + BitConverter.ToString(input, j, 1);//BitOps.ConvertToHexString(input[j]);

                dataStr += "\t";
                for (int i = 0; i < 8; i++)
                {
                    if (BitOps.Get(input[j], i))
                        dataStr += "1";
                    else
                        dataStr += "0";
                }

                dataStr += "\n";
            }

            if (title != "")
                Console.WriteLine(title + ":\n");
            else
                Console.WriteLine("Data:\n");

            Console.WriteLine(dataStr);
            Console.WriteLine("--------------------------------------------------------------------");
        }

        public DataPack(byte[] _data)
        {
            PrintBits(_data);

            if (_data.Length >= 26)
            {
                length = _data[0];
                if (length >= 26)
                {
                    deviceId = _data[1];

                    byte[] dataTimeBytes = new byte[8];
                    byte[] xBytes = new byte[4];
                    byte[] yBytes = new byte[4];
                    byte[] zBytes = new byte[4];
                    byte[] velBytes = new byte[4];
                    data = new byte[length - 26];

                    Array.Copy(_data, 2, dataTimeBytes, 0, 8);
                    Array.Copy(_data, 10, xBytes, 0, 4);
                    Array.Copy(_data, 14, yBytes, 0, 4);
                    Array.Copy(_data, 18, zBytes, 0, 4);
                    Array.Copy(_data, 22, velBytes, 0, 4);
                    Array.Copy(_data, 26, data, 0, data.Length);


                    timestamp = IPAddress.NetworkToHostOrder(BitConverter.ToInt64(dataTimeBytes, 0));

                    x = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(xBytes, 0));
                    y = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(yBytes, 0));
                    z = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(zBytes, 0));
                    velocity = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(velBytes, 0));
                }
                else
                {
                    Log.AddToConsole("Incorrect length!", "server");
                    Console.WriteLine("Incorrect length!");
                }
            }
            else
            {
                Log.AddToConsole("To short data for DataPack!", "server");
                Console.WriteLine("To short data for DataPack!");
            }
        }

        public byte[] ToByteArray()
        {
            byte[] dataBytes = new byte[length];

            byte[] lengthBytes = BitConverter.GetBytes(length);
            byte[] deviceID = BitConverter.GetBytes(deviceId);

            byte[] dataTimeBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(timestamp));
            byte[] xBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(x));
            byte[] yBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(y));
            byte[] zBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(z));
            byte[] velBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(velocity));


            //PrintBits(lengthBytes, "lengthBytes");
            //PrintBits(deviceID, "deviceID");
            //PrintBits(dataTimeBytes, "dataTime");
            //PrintBits(xBytes, "xBytes");
            //PrintBits(yBytes, "yBytes");
            //PrintBits(zBytes, "zBytes");
            //PrintBits(velBytes, "velBytes");
            

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

        public override string ToString()
        {
            return this.deviceId.ToString() + " (" + this.timestamp.ToString() + "):\t" + this.x.ToString() + "\t" + this.y.ToString() + "\t" + this.z.ToString() + "\t" + this.velocity.ToString();
        }
    }

}
