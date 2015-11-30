using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace Sender
{
    class Client
    {
        Socket sending_socket;
        IPAddress send_to_address;
        IPEndPoint sending_end_point;

        public Client()
        {
            sending_socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram,
            ProtocolType.Udp);
            send_to_address = IPAddress.Parse("192.168.210.100");
            sending_end_point = new IPEndPoint(send_to_address, 11000);
        }

        public void send(byte[] message)
        {
            if (message.Length != 0)
            {
                //byte[] send_buffer = Encoding.ASCII.GetBytes(message);
                sending_socket.SendTo(message, sending_end_point);
            }
        }
    }

}
