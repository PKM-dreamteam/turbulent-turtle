using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Server
{
    public partial class Form1 : Form
    {
        ServerThread serverThread = new ServerThread();
        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            serverThread.Start();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            serverThread.Stop();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            DataPack received = serverThread.GetLastDataPack();
            textBox1.Text = received.length.ToString();
            textBox2.Text = received.deviceId.ToString();
            textBox3.Text = received.timestamp.ToString();
            textBox4.Text = received.x.ToString();
            textBox5.Text = received.y.ToString();
            textBox6.Text = received.z.ToString();
            textBox7.Text = received.velocity.ToString();
            
            string result = System.Text.Encoding.Default.GetString(received.data);
            textBox8.Text = result;



        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void label1_Click_1(object sender, EventArgs e)
        {

        }
    }
}
