using Server;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Sender
{
    public partial class Form1 : Form
    {
        byte length = 0;
        byte deviceID = 0;
        long timestamp;
        Int32 x = 0, y= 0, z = 0, velocity = 0;
                
        

        Client client = new Client(); 
        public Form1()
        {
            InitializeComponent();
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {

            Byte.TryParse(textBox2.Text, out deviceID);
            //DateTime timestamp = DateTime.ParseExact(textBox3.Text,"yyyy-MM-dd HH:mm:ss", System.Globalization.CultureInfo.InvariantCulture);
            Int64.TryParse(textBox3.Text, out timestamp);
            Int32.TryParse(textBox4.Text, out x);
            Int32.TryParse(textBox5.Text, out y);
            Int32.TryParse(textBox6.Text, out z);
            Int32.TryParse(textBox1.Text, out velocity);
            //Byte.TryParse(textBox7.Text, out data);
            String dataString = textBox7.Text;
            byte[] data = System.Text.Encoding.Default.GetBytes(dataString);


            //DataPack dataPack = new DataPack(length, deviceID, timestamp, x, y, z); 


            byte[] buffer = new DataPack(deviceID, timestamp, x, y, z, velocity, data).ToByteArray();
            client.send(buffer);
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
