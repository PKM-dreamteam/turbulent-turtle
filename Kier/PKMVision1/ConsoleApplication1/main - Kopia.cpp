#include "PKMVision1.h"
#include "NetCam.h"
//#include "boost/thread.hpp"
//#include <thread>


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
	printf("c - clear all ROI\n\n");

}
int main(int argc, char *argv[])
{
	int camType;
	char* camAddr="";


	char* camAddr1 = "rtsp://admin:DoTestowania@172.20.16.105/profile5/media.smp";
	char* camAddr2 = "rtsp://admin:DoTestowania@172.20.16.106/profile1/media.smp";
	char* camAddr3 = "http://192.168.210.123:80/?action=stream";
	char* camAddr4 = "http://192.168.210.124:80/?action=stream";

	if (argc < 2) {
		//argv[1] = "rtsp://admin:B17ed7bb@172.20.16.106/profile2/media.smp";
		//argv[1]="rtsp://admin:4321@192.168.210.121/profile3/media.smp";
		//camAddr1 = "http://192.168.210.123:80/?action=stream";
		//argv[1]="rtsp://192.168.210.123:554/ch0_0.h264";
		camAddr = "rtsp://admin:DoTestowania@172.20.16.105/profile5/media.smp";
		//camAddr1 = "rtsp://admin:DoTestow@172.20.16.105/profile1/media.smp";
		//camAddr2 = "rtsp://admin:DoTestow@172.20.16.106/profile1/media.smp";
		camType = 1;
		//printf("Opening stream: %s \n",argv[1]);

	}else if (argc == 3){
		camAddr = argv[1];
		camType = atoi(argv[2]);
	}
	else
		helpScreen();
	

	
	////////////////////////////////////////////////////////////////////////////////
	/*
	- read config (if not - exit)
	// AT THIS STAGE (view of max 2 static cameras from one PC)
	- nr of static cameras, position (eg. from left)
	- ip adresses (eg. from left), protocol
	- AI-Ball ip adresses (1, 2 ...)
	// module on/off
	- object detection
	- object tracking
	- area painting on screen (and store output in config)
	-- mouse listener
	- railway areas
	- barier approach (temporary fixed)
	- screen stiching (right window rotation, position, choose which two cameras)

	*/
	//// 
	/*
	dla AI ball - canny, optical flow
	dla IP:
	- poprawa dll DONE
	- ROI, DONE
	- gmm (test parametrow), NOT DONE
	- znacznik na torach (wczytywanie i zapis w konfigu), zapalanie gdy poci¹g na znaczniku DONE
	- 

	
	*/
	///////////////////////////////////////////////////////////////////////////////
	if (false)//read config error
		return -1;
	
	//NetCam* cam = new NetCam();

	NetCam* cam2 = new NetCam();
	int openCam;
	//cam2->open(camAddr3,0);
	openCam = cam2->open(camAddr, camType);
	if (openCam != 0){
		printf("No Camera. Press any key...");
		getchar();
		return 0;
	}
	av_log_set_level(AV_LOG_FATAL);
	
	helpScreen();
	// open streams (method)
	// TODO all streams in AVFormatContext Table

	//if (cam->open(argv[1],2) != 0){
//	if (cam->open(camAddr2, 2) != 0){
//		printf("No opened camera. Press any key...");
//		getchar();
//		return 0;
//	}


	//namedWindow("test", 1);
	//namedWindow("test2", 1);

	//namedWindow("foreground image", WINDOW_NORMAL);
	//namedWindow("foreground image", 0);
	//namedWindow("mean background image", WINDOW_NORMAL);
	PKMVision01* imgProc = new PKMVision01(0);
	if (camType == 1) //for samsung only
		imgProc->paramsLoaded = imgProc->loadParams("params.yml");
	else{
		imgProc->recView = 1;
	}

	if (imgProc->paramsLoaded)
		imgProc->setROImask();


	//while (av_read_frame(cam->pFormatCtx, &cam->packet) >= 0) {
	//	// Is this a packet from the video stream?
	//	if (cam->packet.stream_index == cam->videoStream) {
	//		// Decode video frame
	//		avcodec_decode_video2(cam->pCodecCtx, cam->pFrame, &cam->frameFinished, &cam->packet);
	//		if (cam->frameFinished) {
	//			
	//			imshow("test", cam->readFrame());
	//			waitKey(1);
	//		}
	//	}

	//	// Free the packet that was allocated by av_read_frame
	//	av_free_packet(&cam->packet);
	//}

	imgProc->gmm_init();
	VideoWriter testWrite;
	//testWrite.open("D:\\testout.avi", -1, 5, Size(1280, 1024));
	while (true){
		//av_read_frame(cam->pFormatCtx, &cam->packet);

		// Is this a packet from the video stream?
		//if (cam->packet.stream_index == cam->videoStream) {
		// Decode video frame
		//avcodec_decode_video2(cam->pCodecCtx, cam->pFrame, &cam->frameFinished, &cam->packet);
		//if (cam->frameFinished) {

		//				imshow("test", cam->readFrame());
		//			waitKey(1);
		//	}
		//}
		av_read_frame(cam2->pFormatCtx, &cam2->packet);
		if (cam2->packet.stream_index == cam2->videoStream) {
			// Decode video frame
			avcodec_decode_video2(cam2->pCodecCtx, cam2->pFrame, &cam2->frameFinished, &cam2->packet);
			if (cam2->frameFinished) {
				Mat readFrame = cam2->readFrame();
				//test
				imgProc->calcWhiteArea(&readFrame);

				//testWrite.write(readFrame);
				Mat actualFrame;
				// make smaller img
				if (imgProc->paramsLoaded)
					actualFrame = imgProc->resizeToROImask(&readFrame);
				else
					actualFrame = readFrame;

				if (cam2->recordingOutput && cam2->readyToRecord && imgProc->recView ==1 )
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

				//readFrame.copyTo(imgProc->lastFrame);

				

				//setMouseCallback("image", imgProc->mouseHandler, &imgProc->mParams);
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
					putText(readFrame, format("X: %d Y: %d", imgProc->mParams.mouseXY.x, imgProc->mParams.mouseXY.y), Point(50, 50), FONT_HERSHEY_COMPLEX, 1, Scalar(200, 255, 0), 1);
					putText(readFrame, format("W: %d H: %d", imgProc->gimg.cols, imgProc->gimg.rows), Point(50, 90), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 255, 200), 1);
					putText(readFrame, format("RGB: %3.0f, %3.0f, %3.0f", imgProc->meanVal[2], imgProc->meanVal[1], imgProc->meanVal[0]), Point(50, imgProc->whiteArea.y), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 0, 255), 1);
					imshow("PaintWindow", readFrame);
				}
				if (imgProc->openRoiWindow){
					// rys znacznikow na torach
					if (imgProc->runCanny){
						Mat imgCanny;
						imgCanny.create(imgProc->gimg.size(), imgProc->gimg.type());
						Canny(imgProc->gimg, imgCanny, 100, 255);
						cvtColor(imgCanny, imgProc->gimg, CV_GRAY2BGR);
						//imgCanny.copyTo(imgProc->gimg);
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
						cam2->saveVideoFrames(&imgProc->fgimg);

					if (cam2->recordingOutput && cam2->readyToRecord)
						putText(imgProc->fgimg, format("RECORDING", imgProc->mParams.mouseXY.x, imgProc->mParams.mouseXY.y), Point(50, 50), FONT_HERSHEY_COMPLEX, 1, Scalar(0, 0, 255), 1);
					imshow("Foreground", imgProc->fgimg);
				}
				//if (!imgProc->bgimg.empty())
				//	imshow("mean background image", imgProc->bgimg);
				
				//if (!imgProc->fgmask.empty())
				//	imshow("Object mask", imgProc->fgmask);

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

		char k = (char)waitKey(20);
		if (k == ' ')
			imgProc->update_bg_model = !imgProc->update_bg_model;
		else if (k == 's' || k == 'S'){
			imgProc->setROImask();
			//imshow("testWindow",imgProc->imgRoiMask);
			//waitKey(0);
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
			//imgProc->openMaskWindow = !imgProc->openMaskWindow;
			//if (imgProc->openMaskWindow)
			//	namedWindow("Mask", WINDOW_NORMAL);
			//else
			//	destroyWindow("Mask");
		}
		else if (k == 'e' || k == 'E'){
			imgProc->runCanny = !imgProc->runCanny;
		}
		else if (k == 27) //exit program
		{
			// deinit
			break;
		}
		
	}
	//cam->close();

	// Deinit network protocols
	avformat_network_deinit();

	return 0;
}
