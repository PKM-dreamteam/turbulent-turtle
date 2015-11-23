#ifndef _NETCAM_H
#define _NETCAM_H
#include "stdafx.h"

extern "C" {
#include "libswscale/swscale.h"
#include "libavcodec/avcodec.h"
#include "libavformat/avformat.h"
	//#include "libavutil/common.h"
	//#include "libavutil/fifo.h"
	//#include "libavutil/opt.h"
}
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "opencv2/core/core.hpp"
//#include <opencv2/core/utility.hpp>
#include "opencv2/video/background_segm.hpp"
//#include "opencv2/videoio.hpp"

#define _CRT_SECURE_NO_DEPRECATE
#include <stdio.h>
//#include <istream>
//#include <memory>


// compatibility with newer API
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(55,28,1)
#define av_frame_alloc avcodec_alloc_frame
#define av_frame_free avcodec_free_frame
#endif


using namespace std;



class NetCam
{
public:
	NetCam();
	~NetCam();
	int open(char* camIpAddress, int camType); // open IP camera, type: 1- standard rtsp camera, 2 Ai-Ball (with modified MJPEG header)
	void close(); // close stream from camera
	cv::Mat readFrame(); // read actual frame
	bool initSaveVideo(cv::Mat *img, char* filename); // variable initialization for video recording
	void saveVideoFrames(cv::Mat *img); // record signle frame
	void closeSaveVideo(); // close recording
	cv::Mat avFrame2Mat(AVFrame *frame); // convert FFMpeg frame to OpenCV frame
private:
	int init();
	int camType;

public:
	// FFMpeg variables
	AVFormatContext   *pFormatCtx = NULL;
	int               videoStream;
	AVCodecContext    *pCodecCtx = NULL;
	AVCodec           *pCodec = NULL;

	AVPacket          packet;
	int               frameFinished;
	int               numBytes;
	uint8_t           *buffer = NULL;
	struct SwsContext *sws_ctx = NULL;

private:
	char* camIpAddress;
	cv::VideoWriter outputVideo;
public:
	AVFrame *pFrame = NULL;
	AVFrame *pFrameBGR = NULL;
	cv::Mat frame;
	bool recordingOutput; //recording flags
	bool readyToRecord; //recording flags
};

#endif
