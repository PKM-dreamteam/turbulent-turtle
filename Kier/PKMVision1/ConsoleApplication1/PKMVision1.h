#ifndef _PKMVISION1_H
#define _PKMVISION1_H
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
#include <ctime>
#include "opencv2/core/core.hpp"
//#include <opencv2/core/utility.hpp>
#include "opencv2/video/background_segm.hpp"
#include "opencv2/video.hpp"
//#include "opencv2/videoio.hpp"
#include "opencv2/video/tracking.hpp"

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

class PKMVision01
{
public:
	PKMVision01();
	PKMVision01(int flag);
	~PKMVision01();

	int recView; // record view (set in params)

	// ALL IMG
	cv::Mat imgRoi, imgRoiMask;
	cv::Mat gimg0, gimg, fgmask, fgimg, bgimg; //gmm
	cv::Mat flow, prevGray; // optFlow

	// centroid for estimated position of PKM model
	cv::Point2d centroid;
	cv::Point2d prev_centroid;

	// distance between last and current centroid
	float dist;

	// speed vector
	cv::Vec2d v;

	// time of last frame
	int frame_time = 0;

	//flag to notify that model position is found
	bool modelPosition;

	//flag to notify that small model is used
	bool smallModel;

	float rescale = 0.7;
	int startDelay; // delay processing X frames (some algorithms may need it)

	// GMM & PROCESS
	cv::Ptr<cv::BackgroundSubtractor> bg_model;
	bool update_bg_model; // model update flag
	void gmm_init(); // init gmm variables
	void gmm(cv::Mat* frame, bool smooth); // object detection algorithm
	void calcWhiteArea(cv::Mat* orgFrame); // calculate mean RGB for a given area
	cv::Rect whiteArea; // area for calcWhiteArea
	cv::Scalar meanVal; // output RGB of calcWhiteArea
	bool runCanny; // flag to run Canny Edge Detection
	
	// OPTICAL FLOW
	bool opticalFlow_isInit;
	void opticalFlow(cv::Mat* img);
	const int MAX_COUNT = 500; // max number of characteristics points
	bool needToInit;
	int resetPointsAfter; // reset optical flow after X frames
	int optFlowCounter; // frame counter
	int opticalType; // optical flow type (flow vectors, track points)
	vector<cv::Point2f> points[2]; // characteristics points
	

	// MOUSE CALLBACK
	static void mouseHandler(int event, int x, int y, int flags, void* params);
	struct MouseParams{
		cv::Point mouseXY;
		struct rectType{
			cv::Rect selRect;
			int selType;
		} rectType;
		int flag;
	} mParams;
	
	// ROI
	void areasObjDetect();
	void setMultiROI(cv::Mat* img);
	void setCheckAreas(cv::Mat* img);
	void drawAreas(cv::Mat* img, bool insideRoi);
	void saveROI();
	bool setROImask();
	cv::Mat resizeToROImask(cv::Mat* img0);
	vector<cv::Rect> rectROI;
	struct RectBool{
		vector<cv::Rect> area;
		vector<bool> isObject;
	} checkAreas;
	
	//vector<Rect> updatedROI;
	bool pointSet;
	bool paramsUpdated;
	bool openWindowToDraw, openRoiWindow, openForegroundWindow, setMask;
	int openOpticalFlowWindowAndType;

	// CONFIG & PARAMS
	bool loadParams(const string &filenameParam);
	bool saveParams(const string &filenameParam);
	bool paramsLoaded;
	int Xmin, Xmax, Ymin, Ymax;


};
#endif
