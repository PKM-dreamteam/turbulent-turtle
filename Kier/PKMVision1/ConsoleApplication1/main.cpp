#include "PKMVision1.h"
#include "NetCam.h"
#include "CoordSys.h"
#include "UDPtransmission.h"
//#include "boost/thread.hpp"
//#include <thread>

using namespace cv;

void helpScreen(){
	printf("\n\n HELP SCREEN:\n");
	printf("PKMVision.exe <cameraIP> <camera type(0 - file, 1 - samsung, 2 - AIBall)>\n");
	printf("p - open/close printWindow\n");
	printf("r - open/close ROI Window\n");
	printf("w - write to file (recorded view set in params)\n");
	printf("e - edge detection in ROI Window\n");
	printf("o - optical Flow\n");
	printf("l - load parameters from file params.yml\n");
	printf("s - save parameters to file params.yml\n");
	printf("t - setup coordinate system\n");
	printf("c - clear all ROI\n\n");

}
int main(int argc, char *argv[])
{
	int camType;
	char* camAddr="";

	if (argc < 2) {
		camAddr = "C:\\projekty\\turbulent-turtle-master\\Kier\\PKMVision1\\Release\\test1.avi";
		camType = 0;
	}else if (argc == 3){
		camAddr = argv[1];
		camType = atoi(argv[2]);
	}
	else
		helpScreen();

	//Create coordinate system objet
	CoordSys* coordSystem = new CoordSys();

	//Create UDP transmission client
	UDPtrans* udp = new UDPtrans();

	//Create time variable for speed calculations
	int tick_before = 0;

	// Open camera and stream //
	NetCam* cam2 = new NetCam();
	int openCam;
	openCam = cam2->open(camAddr, camType);
	if (openCam != 0){
		printf("No Camera. Press any key...");
		getchar();
		return 0;
	}
	av_log_set_level(AV_LOG_FATAL); // disable FFMPEG warnings
	
	helpScreen();

	PKMVision01* imgProc = new PKMVision01(0);
	//if (camType == 1) //for samsung only
		imgProc->paramsLoaded = imgProc->loadParams("params.yml"); // not robust if params are missing
	////else{
	//	imgProc->recView = 1;
	//}

	if (imgProc->paramsLoaded)
		imgProc->setROImask();

	imgProc->gmm_init();
	VideoWriter testWrite;
	while (true){
		
		av_read_frame(cam2->pFormatCtx, &cam2->packet); // read single frame from camera
		if (cam2->packet.stream_index == cam2->videoStream) {
			// Decode video frame
			avcodec_decode_video2(cam2->pCodecCtx, cam2->pFrame, &cam2->frameFinished, &cam2->packet);
			if (cam2->frameFinished) {
				Mat readFrame = cam2->readFrame();
				//test
				imgProc->calcWhiteArea(&readFrame);

				coordSystem->setFrameDimension(readFrame.cols, readFrame.rows);

				Mat actualFrame;
				// resize img
				if (imgProc->paramsLoaded)
					actualFrame = imgProc->resizeToROImask(&readFrame);
				else
					actualFrame = readFrame;

				if (cam2->recordingOutput && cam2->readyToRecord && imgProc->recView == 1)
					cam2->saveVideoFrames(&readFrame);

				if (imgProc->paramsLoaded){
					imgProc->setMultiROI(&readFrame);
					imgProc->drawAreas(&readFrame, 0);
					imgProc->gmm(&actualFrame, true);
					imgProc->areasObjDetect();
				}
				else {
					imgProc->fgimg = Mat::zeros(readFrame.size(), readFrame.type());
					imgProc->gimg = readFrame;
				}
				
				if (imgProc->startDelay == 0 && imgProc->openOpticalFlowWindowAndType){
					imgProc->opticalFlow(&readFrame);
					imshow("OpticalFlow",imgProc->flow);
				}

				if (imgProc->paramsLoaded){
					if (imgProc->update_bg_model)
						putText(readFrame, "Model update", Point(50, 150), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 255, 0), 2);
					else
						putText(readFrame, "Model detect", Point(50, 150), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 255, 0), 2);
				}
				// DRAW & SHOW IN WINDOWS
				if (imgProc->openWindowToDraw){
					if (imgProc->paramsLoaded)
						imgProc->drawAreas(&readFrame, 0);
					if (coordSystem->isSetupInProgress())
					{
						if (coordSystem->getState() == CoordSys::GET_LOCAL_XY)
							putText(readFrame, "Mark known point", Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
						else if (coordSystem->getState() == CoordSys::SET_GLOBAL_X)
							putText(readFrame, format("X: %s", coordSystem->getBuffer().c_str()), Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
						else if (coordSystem->getState() == CoordSys::SET_GLOBAL_Y)
							putText(readFrame, format("Y: %s", coordSystem->getBuffer().c_str()), Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
						else if (coordSystem->getState() == CoordSys::GET_LOCAL_LINE_A)
							putText(readFrame, "Mark A point", Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
						else if (coordSystem->getState() == CoordSys::GET_LOCAL_LINE_B){
							putText(readFrame, "Mark B point", Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
							line(readFrame, coordSystem->getLocalLineA(), imgProc->mParams.mouseXY, Scalar(0, 255, 0), 2);
						}
						else if (coordSystem->getState() == CoordSys::SET_GLOBAL_AB){
							putText(readFrame, format("Length: %s cm", coordSystem->getBuffer().c_str()), Point(50, 250), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
							line(readFrame, coordSystem->getLocalLineA(), coordSystem->getLocalLineB(), Scalar(0, 255, 0), 2);
						}

						if (coordSystem->getState() > CoordSys::GET_LOCAL_XY)
							circle(readFrame, coordSystem->getLocalKnownPoint(), 6, Scalar(0, 0, 255), -1);
					}
					if (imgProc->modelPosition)
					{
						circle(readFrame, Point(imgProc->centroid.x * 10 / 7 + imgProc->Xmin, imgProc->centroid.y * 10 / 7 + imgProc->Ymin), 3, Scalar(0, 0, 255), -1);
					}
					putText(readFrame, format("X: %d Y: %d", imgProc->mParams.mouseXY.x, imgProc->mParams.mouseXY.y), Point(50, 50), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
					putText(readFrame, format("W: %d H: %d", imgProc->gimg.cols, imgProc->gimg.rows), Point(50, 90), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 255, 200), 1);
					putText(readFrame, format("RGB: %3.0f, %3.0f, %3.0f", imgProc->meanVal[2], imgProc->meanVal[1], imgProc->meanVal[0]), Point(50, imgProc->whiteArea.y), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 0, 255), 1);
					imshow("PaintWindow", readFrame);
				}
				if (imgProc->openRoiWindow){
					// draw markers on railway
					if (imgProc->runCanny){
						Mat imgCanny;
						imgCanny.create(imgProc->gimg.size(), imgProc->gimg.type());
						Canny(imgProc->gimg, imgCanny, 100, 255);
						cvtColor(imgCanny, imgProc->gimg, CV_GRAY2BGR);
					}
					if (imgProc->paramsLoaded && !imgProc->runCanny)
						imgProc->drawAreas(&imgProc->gimg,1);
					if (cam2->recordingOutput && cam2->readyToRecord && imgProc->recView == 3)
						cam2->saveVideoFrames(&imgProc->gimg);
					imshow("Image", imgProc->gimg);

				}
				if (imgProc->openForegroundWindow){
					if (imgProc->paramsLoaded)
						imgProc->drawAreas(&imgProc->fgimg, 1);
					if (cam2->recordingOutput && cam2->readyToRecord && imgProc->recView == 2)
						cam2->saveVideoFrames(&imgProc->fgmask);

					if (cam2->recordingOutput && cam2->readyToRecord)
						putText(imgProc->fgimg, format("RECORDING", imgProc->mParams.mouseXY.x, imgProc->mParams.mouseXY.y), Point(50, 50), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 0, 255), 1);

					if (imgProc->modelPosition)
					{
						circle(imgProc->fgimg, Point(imgProc->centroid.x, imgProc->centroid.y), 3, Scalar(0,0,255), -1);	
						arrowedLine(imgProc->fgimg, imgProc->centroid, imgProc->centroid + Point2d(imgProc->v), Scalar(0, 255, 0));

						if (coordSystem->isSetupDone())
						{
							float g_x = coordSystem->localToGlobalCoordXInversed((imgProc->centroid.x * 10 / 7) + imgProc->Xmin);
							float g_y = coordSystem->localToGlobalCoordYInversed((imgProc->centroid.y * 10 / 7) + imgProc->Ymin);

							// calculating speed
							int v_x = imgProc->centroid.x - imgProc->prev_centroid.x;
							int v_y = imgProc->centroid.y - imgProc->prev_centroid.y;

							double v = sqrt((v_x * v_x) + (v_y * v_y));

							float g_v = coordSystem->localToGlobalLengthF(v * 10.0 / 7.0);

							int tick = GetTickCount();
							if (tick_before != 0)
							{
								int timediff = tick - tick_before;
								udp->sendPacket((int)(g_x * 10), (int)(g_y * 10), (int)((g_v * 10) / ((float)timediff / 1000)));
								//printf("%f(x) %f(y) %f(v) %f(v/t)\n", g_x, g_y, g_v, (g_v / ((float)timediff / 1000)));
							}
							tick_before = tick;
						}
					}
					imshow("Foreground", imgProc->fgimg);
				}

				///////////// RECORDING //////////////////
				if (cam2->recordingOutput){
					if (!cam2->readyToRecord)
						if (imgProc->recView == 1){
							cam2->recordingOutput = cam2->initSaveVideo(&readFrame, "test1.avi");
						}
						if (imgProc->recView == 2)
							cam2->recordingOutput = cam2->initSaveVideo(&imgProc->fgimg, "test2.avi");
						if (imgProc->recView == 3)
							cam2->recordingOutput = cam2->initSaveVideo(&imgProc->gimg, "test3.avi");
				}

			}
			if (imgProc->startDelay > 0)
				imgProc->startDelay--;
		}

		// Free the packet that was allocated by av_read_frame
		av_free_packet(&cam2->packet);

		// Keyboard callback //
		char k = (char)waitKey(20);
		if (k == ' ')
			imgProc->update_bg_model = !imgProc->update_bg_model;
		else if (k == 's' || k == 'S'){
			imgProc->setROImask();
			imgProc->saveParams("params.yml");
		}
		else if (k == 'l' || k == 'L')
			imgProc->loadParams("params.yml");
		else if (k == 'c' || k == 'C'){
			imgProc->rectROI.clear();
			imgProc->checkAreas.area.clear();
			imgProc->whiteArea.width = 0;
		}
		else if (k == 'w' || k == 'W'){
			cam2->recordingOutput = !cam2->recordingOutput;
			if (!cam2->recordingOutput && cam2->readyToRecord){
				cam2->readyToRecord = false;
				cam2->closeSaveVideo();
			}
		}
		else if (k == 'p' || k == 'P'){
			imgProc->openWindowToDraw = !imgProc->openWindowToDraw;
			if (imgProc->openWindowToDraw){
				namedWindow("PaintWindow", WINDOW_AUTOSIZE);
				setMouseCallback("PaintWindow", imgProc->mouseHandler, &imgProc->mParams);
			}
			else{
				setMouseCallback("PaintWindow", NULL, NULL);
				destroyWindow("PaintWindow");
			}
		}
		else if (k == 'r' || k == 'R'){
			imgProc->openRoiWindow = !imgProc->openRoiWindow;
			if (imgProc->openRoiWindow)
				namedWindow("Image", WINDOW_NORMAL);
			else
				destroyWindow("Image");
		}
		else if (k == 'f' || k == 'F'){
			imgProc->openForegroundWindow = !imgProc->openForegroundWindow;
			if (imgProc->openForegroundWindow)
				namedWindow("Foreground", WINDOW_NORMAL);
			else
				destroyWindow("Foreground");
		}
		else if (k == 'o' || k == 'O'){
			imgProc->openOpticalFlowWindowAndType = (imgProc->openOpticalFlowWindowAndType + 1) % 3;
			imgProc->needToInit = true;
			if (imgProc->openOpticalFlowWindowAndType != 0)
				namedWindow("OpticalFlow", WINDOW_NORMAL);
			else{
				destroyWindow("OpticalFlow");
				imgProc->opticalFlow_isInit = 0;
			}
		}
		else if (k == 'm' || k == 'M'){
			imgProc->setMask = !imgProc->setMask;
		}
		else if (k == 'e' || k == 'E'){
			imgProc->runCanny = !imgProc->runCanny;
		}
		else if (k == 't' || k == 'T'){
			if (coordSystem->isSetupInProgress())
				coordSystem->endCoordSetup();
			else
				coordSystem->startCoordSetup();
		}
		else if (k == 'x' || k == 'X')
		{
			imgProc->smallModel = !imgProc->smallModel;
		}
		else if (k == 27) //exit program
		{
			// additional deinit ?
			break;
		}
		else if (k == 13) //Enter
		{
			if (coordSystem->isSetupInProgress()) {
				if (coordSystem->getState() == CoordSys::GET_LOCAL_XY)
					coordSystem->setLocalKnownPoint(imgProc->mParams.mouseXY);
				else if (coordSystem->getState() == CoordSys::SET_GLOBAL_X)
					coordSystem->setGlobalKnownPointX(26);
				else if (coordSystem->getState() == CoordSys::SET_GLOBAL_Y)
					coordSystem->setGlobalKnownPointY(620);
				else if (coordSystem->getState() == CoordSys::GET_LOCAL_LINE_A)
					coordSystem->setLocalLineA(imgProc->mParams.mouseXY);
				else if (coordSystem->getState() == CoordSys::GET_LOCAL_LINE_B)
					coordSystem->setLocalLineB(imgProc->mParams.mouseXY);
				else if (coordSystem->getState() == CoordSys::SET_GLOBAL_AB)
				{
					coordSystem->setGlobalLineABLength(10);
				}

				coordSystem->nextState();

				if (coordSystem->getState() == CoordSys::SETUP_DONE)
				{
					coordSystem->setSetupDone();
					coordSystem->endCoordSetup();
					//printf("%f\n\n", coordSystem->localToGlobalLengthF(1));
				}
			}
		}
		else if (coordSystem->isSetupInProgress() && k != -1) //Read input data for coordinate system
		{
			if (k == 8) //Backspace
			{
				if (coordSystem->getBuffer().length() > 0)
					coordSystem->backspaceInBuffer();
			}
			else if (coordSystem->getState() == CoordSys::SET_GLOBAL_X ||
				coordSystem->getState() == CoordSys::SET_GLOBAL_Y ||
				coordSystem->getState() == CoordSys::SET_GLOBAL_AB)
				coordSystem->addCharToBuffer(k);
		}
		
	}
	
	// Deinit network protocols
	avformat_network_deinit();

	return 0;
}
