#ifndef _UDPTRANSMISSION_H
#define _UDPTRANSMISSION_H

#include<stdio.h>
#include<winsock2.h>
#include<ctime>

#pragma comment(lib,"ws2_32.lib") //Winsock Library

#define SERVER "127.0.0.1"  //ip address of udp server
#define PORT 11000   //The port on which to listen for incoming data

class UDPtrans
{
public:
	UDPtrans();
	~UDPtrans();

	void sendPacket(int x, int y, int v);

private:
	struct sockaddr_in si_other;
	int s, slen;
	WSADATA wsa;
	void reverse_memcpy(char* dest, const byte* source, int length);
};

#endif