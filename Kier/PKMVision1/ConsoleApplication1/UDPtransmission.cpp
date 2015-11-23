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

void UDPtrans::sendPacket(double x, double y, double v)
{
	float z = 0;
	byte IdVision = 100;
	byte packetlength = 42;

	std::time_t timestamp = std::time(nullptr);
	
	printf("Przed: %d %d %f %f %f %f\n", IdVision, packetlength, x, y, z, v);

	const char* xBytes = reinterpret_cast<const char*>(&x);
	const char* yBytes = reinterpret_cast<const char*>(&y);
	const char* vBytes = reinterpret_cast<const char*>(&v);
	const char* zBytes = reinterpret_cast<const char*>(&z);
	const char* lenBytes = reinterpret_cast<const char*>(&packetlength);
	const char* idBytes = reinterpret_cast<const char*>(&IdVision);
	const char* timeBytes = reinterpret_cast<const char*>(&timestamp);

	printf("Po: %d %d %d %d %d %d\n", *idBytes, *lenBytes, *xBytes, *yBytes, *zBytes, *vBytes);

	char* buff;
	int a = 42;

	buff = new char[a];

	printf("Dl pakietu: %d %d %d %d %d %d %d %d\n", strlen(lenBytes), strlen(idBytes),
		strlen(timeBytes), strlen(xBytes), strlen(yBytes),
		strlen(zBytes), strlen(vBytes), a);
	strcpy(buff, lenBytes);
	strcat(buff, idBytes);
	strcat(buff, timeBytes);
	strcat(buff, xBytes);
	strcat(buff, yBytes);
	strcat(buff, zBytes);
	strcat(buff, vBytes);

	printf("%s\n", buff);
	//send the message
	if (sendto(s, buff, 42, 0, (struct sockaddr *) &si_other, slen) == SOCKET_ERROR)
	{
		printf("sendto() failed with error code : %d", WSAGetLastError());
		exit(EXIT_FAILURE);
	}
}
