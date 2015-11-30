#ifndef _COORDSYS_H
#define _COORDSYS_H

#include "PKMVision1.h"

class CoordSys
{
public:
	CoordSys();
	~CoordSys(void);

	enum State {
		GET_LOCAL_XY,
		SET_GLOBAL_X,
		SET_GLOBAL_Y,
		GET_LOCAL_LINE_A,
		GET_LOCAL_LINE_B,
		SET_GLOBAL_AB,
		SETUP_DONE
	};
	void setFrameDimension(int width, int height);

	void startCoordSetup();
	void endCoordSetup();

	void setLocalKnownPoint(cv::Point point);
	cv::Point getLocalKnownPoint();
	void setGlobalKnownPointX(float x);
	void setGlobalKnownPointY(float y);

	void setLocalLineA(cv::Point point);
	void setLocalLineB(cv::Point point);
	cv::Point getLocalLineA();
	cv::Point getLocalLineB();
	void setGlobalLineABLength(float length);

	void addCharToBuffer(char k);
	void backspaceInBuffer();
	float getNumberFromBuffer();
	std::string getBuffer();

	void nextState();
	State getState();

	bool isSetupInProgress();
	bool isSetupDone();
	void setSetupDone();

	void computePixelLength();
	void computeGlobalInLocalX0Y0();

	float localToGlobalLength(int length);
	float localToGlobalLengthF(float length);
	float localToGlobalCoordX(int x);
	float localToGlobalCoordY(int y);
	float localToGlobalCoordXInversed(int x); //Final results
	float localToGlobalCoordYInversed(int y);

private:
	int screenWidth;
	int screenHeight;

	cv::Point localKnownPoint;
	float globalKnownPointX;
	float globalKnownPointY;

	cv::Point localLineA;
	cv::Point localLineB;
	float globalLineABLength;

	float cmPerPixel;
	float globalInLocalX0;
	float globalInLocalY0;
	float globalInLocalX0Inversed;
	float globalInLocalY0Inversed;

	bool setupInProgress = false;
	bool setupDone = false; //To check if can compute and show global numbers

	std::string inputBuffer = "";

	State confState;
};

#endif