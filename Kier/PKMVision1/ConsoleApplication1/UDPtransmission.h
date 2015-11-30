#ifndef _UDPTRANSMISSION_H
#define _UDPTRANSMISSION_H

#include<stdio.h>
#include<winsock2.h>
#include<ctime>

#pragma comment(lib,"ws2_32.lib") //Winsock Library

#define SERVER "192.168.210.105"  //ip address of udp server
#define PORT 11000   //The port on which to listen for incoming data

class UDPtrans
{
public:
	UDPtrans();
	~UDPtrans();

	void sendPacket(double x, double y, double v);

private:
	struct sockaddr_in si_other;
	int s, slen;
	WSADATA wsa;
};

#endif