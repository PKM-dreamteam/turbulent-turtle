#include "CoordSys.h"

CoordSys::CoordSys()
{
}

CoordSys::~CoordSys()
{
}

//==================================================
void CoordSys::setFrameDimension(int width, int height)
{
	screenWidth = width;
	screenHeight = height;
}

//==================================================
void CoordSys::startCoordSetup()
{
	confState = GET_LOCAL_XY;
	setupInProgress = true;
}

void CoordSys::endCoordSetup()
{
	inputBuffer = "";
	setupInProgress = false;

	//Compute all the shit
	if (setupDone)
	{
		computePixelLength();
		computeGlobalInLocalX0Y0();
	}
}

//==================================================
void CoordSys::setLocalKnownPoint(cv::Point point)
{
	localKnownPoint = point;
}

cv::Point CoordSys::getLocalKnownPoint()
{
	return localKnownPoint;
}

void CoordSys::setGlobalKnownPointX(float x)
{
	globalKnownPointX = x;
}

void CoordSys::setGlobalKnownPointY(float y)
{
	globalKnownPointY = y;
}

//==================================================
void CoordSys::setLocalLineA(cv::Point point)
{
	localLineA = point;
}

void CoordSys::setLocalLineB(cv::Point point)
{
	localLineB = point;
}

cv::Point CoordSys::getLocalLineA()
{
	return localLineA;
}

cv::Point CoordSys::getLocalLineB()
{
	return localLineB;
}

void CoordSys::setGlobalLineABLength(float length)
{
	globalLineABLength = length;
}

//==================================================
void CoordSys::addCharToBuffer(char k)
{
	inputBuffer.append(&k);
}

void CoordSys::backspaceInBuffer()
{
	inputBuffer = inputBuffer.substr(0, inputBuffer.length() - 1);
}

float CoordSys::getNumberFromBuffer()
{
	istringstream stream(inputBuffer);
	float returnValue;
	stream >> returnValue;
	if (stream.fail())
		return -1; //TODO: Dodac obsluge tego errora
	else
		return returnValue;
}

std::string CoordSys::getBuffer()
{
	return inputBuffer;
}

//==================================================
void CoordSys::nextState()
{
	inputBuffer = "";
	confState = (State)(confState + 1);
}

CoordSys::State CoordSys::getState()
{
	return confState;
}

//==================================================
bool CoordSys::isSetupInProgress()
{
	return setupInProgress;
}

bool CoordSys::isSetupDone()
{
	return setupDone;
}

void CoordSys::setSetupDone()
{
	setupDone = true;
}

//==================================================
void CoordSys::computePixelLength()
{
	float localLength = (float)sqrt((localLineA.x - localLineB.x)*(localLineA.x - localLineB.x) + (localLineA.y - localLineB.y)*(localLineA.y - localLineB.y));
	cmPerPixel = globalLineABLength / localLength;
	printf("local length: %f cmPerPixel: %f", localLength, cmPerPixel);
}

void CoordSys::computeGlobalInLocalX0Y0()
{
	globalInLocalX0 = globalKnownPointX + localToGlobalLength(localKnownPoint.x); //(+) Becouse of Inversed global coordinates system
	globalInLocalY0 = globalKnownPointY + localToGlobalLength(localKnownPoint.y);

	globalInLocalX0Inversed = globalInLocalX0 - localToGlobalLength(screenWidth); // Final results
	globalInLocalY0Inversed = globalInLocalY0 - localToGlobalLength(screenHeight);
}

float CoordSys::localToGlobalLength(int length)
{
	return length * cmPerPixel;
}

float CoordSys::localToGlobalLengthF(float length)
{
	return length * cmPerPixel;
}

float CoordSys::localToGlobalCoordX(int x)
{
	return globalInLocalX0 + localToGlobalLength(x);
}

float CoordSys::localToGlobalCoordY(int y)
{
	return globalInLocalY0 + localToGlobalLength(y);
}

//Final results
float CoordSys::localToGlobalCoordXInversed(int x)
{
	return globalInLocalX0Inversed + localToGlobalLength(screenWidth - x);
}

float CoordSys::localToGlobalCoordYInversed(int y)
{
	return globalInLocalY0Inversed + localToGlobalLength(screenHeight - y);
}