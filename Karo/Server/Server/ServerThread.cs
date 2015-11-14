using Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class ServerThread
{
    private const int listenPort = 11000;
    Thread serverThread;
    UdpClient listener = new UdpClient(listenPort);
    IPEndPoint groupEP = new IPEndPoint(IPAddress.Any, listenPort);
    bool isRunning = false;
    public DataPack receiveData;
    public List<DataPack> DataPackList = new List<DataPack>();

    public void Start()
    {
        serverThread = new Thread(new ThreadStart(ReceivePackets));
        serverThread.Start();
    }

    public void Stop()
    {
        isRunning = false;
        serverThread.Join();
    }

    public DataPack GetLastDataPack()
    {
        return DataPackList.Last();
    }

    public void ReceivePackets()
    {
        isRunning = true;
        byte[] receive_byte_array;
        
            while (isRunning)
            {
                if (listener.Available > 0) {
                    receive_byte_array = listener.Receive(ref groupEP);
                    //receiveData = Encoding.ASCII.GetString(receive_byte_array, 0, receive_byte_array.Length);
                    receiveData = new DataPack(receive_byte_array);
                    DataPackList.Add(receiveData);
                }      
            }
        
        listener.Close();
    }
} 