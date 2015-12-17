#include "UDPtransmission.h"
#pragma warning(disable:4996)
UDPtrans::UDPtrans()
{
	slen = sizeof(si_other);

	//Initialise winsock
	printf("\nInitialising Winsock...");
	if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
	{
		printf("Failed. Error Code : %d", WSAGetLastError());
		exit(EXIT_FAILURE);
	}
	printf("Initialised.\n");

	//create socket
	if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == SOCKET_ERROR)
	{
		printf("socket() failed with error code : %d", WSAGetLastError());
		exit(EXIT_FAILURE);
	}

	//setup address structure
	memset((char *)&si_other, 0, sizeof(si_other));
	si_other.sin_family = AF_INET;
	si_other.sin_port = htons(PORT);
	si_other.sin_addr.S_un.S_addr = inet_addr(SERVER);
}

UDPtrans::~UDPtrans()
{
	closesocket(s);
	WSACleanup();
}


// reversing bytes of multi-byte memcpy
void UDPtrans::reverse_memcpy(char* dest, const byte* source, int length)
{
	for (int i = 0; i < length; i++)
	{
		memcpy(dest + i, source + (length - (i + 1)), 1);
	}
}

void UDPtrans::sendPacket(int x, int y, int v)
{
	int z = 0;
	byte IdVision = 100;
	byte packetlength = 26;

	std::time_t timestamp = std::time(nullptr);

	const byte* xBytes = reinterpret_cast<const byte*>(&x);
	const byte* yBytes = reinterpret_cast<const byte*>(&y);
	const byte* vBytes = reinterpret_cast<const byte*>(&v);
	const byte* zBytes = reinterpret_cast<const byte*>(&z);
	const byte* lenBytes = reinterpret_cast<const byte*>(&packetlength);
	const byte* idBytes = reinterpret_cast<const byte*>(&IdVision);
	const byte* timeBytes = reinterpret_cast<const byte*>(&timestamp);

	char* buff;
	int a = 26;

	buff = new char[a];
	
	memcpy(buff, lenBytes, 1);
	memcpy(buff + 1, idBytes, 1);
	reverse_memcpy(buff + 2, timeBytes, 8);
	reverse_memcpy(buff + 10, xBytes, 4);
	reverse_memcpy(buff + 14, yBytes, 4);
	reverse_memcpy(buff + 18, zBytes, 4);
	reverse_memcpy(buff + 22, vBytes, 4);

	//send the message
	if (sendto(s, buff, 26, 0, (struct sockaddr *) &si_other, slen) == SOCKET_ERROR)
	{
		printf("sendto() failed with error code : %d", WSAGetLastError());
		exit(EXIT_FAILURE);
	}
}
