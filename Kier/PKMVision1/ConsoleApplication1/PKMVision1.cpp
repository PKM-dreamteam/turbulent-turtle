#include "PKMVision1.h"

#define DEBUG_INFO
using namespace cv;
//cv::Mat avframe_to_cvmat(AVFrame *frame)
PKMVision01::PKMVision01(){
	// Allocate video frame
	//pFrame = av_frame_alloc();
	// Allocate an AVFrame structure
	//pFrameBGR = av_frame_alloc();
	
	//if (pFrameBGR == NULL)
	//	printf("Could not allocate frame");//return -1;
}
PKMVision01::PKMVision01(int flag){
	paramsLoaded = false;
	pointSet = false;
	mParams.mouseXY = Point(0, 0);
	mParams.rectType.selRect = Rect(0, 0, 0, 0);
	mParams.rectType.selType = 0;
	openWindowToDraw = false;
	openRoiWindow = false;
	openForegroundWindow = true;
	setMask = false;
	paramsUpdated = false;
	startDelay = 1;
	runCanny = false;

	needToInit = true;
	resetPointsAfter = 30;
	optFlowCounter = 0;
	opticalType = 2;
	openOpticalFlowWindowAndType = 0;
	opticalFlow_isInit = false;
	smallModel = false;
}

PKMVision01::~PKMVision01(){}
void PKMVision01::mouseHandler(int event, int x, int y, int flag, void* params)
{
	MouseParams *p = (MouseParams*)params;


	if (event == EVENT_LBUTTONDOWN){
		//printf("LDOWN");
		//if (flag == 9){ //ctrl
			p->rectType.selRect.x = x;
			p->rectType.selRect.y = y;

	}
	if (event == EVENT_LBUTTONUP){
		//printf("LUP");
		int x0 = p->rectType.selRect.x;
		int y0 = p->rectType.selRect.y;
		if (x0 < x && y0 < y)
			p->rectType.selRect = Rect(x0, y0, x - x0, y - y0);
		if (x0 > x && y0 < y) //
			p->rectType.selRect = Rect(x, y0, x0 - x, y - y0);
		if (x0 < x && y0 > y)
			p->rectType.selRect = Rect(x0, y, x - x0, y0 - y);
		if (x0 > x && y0 > y) 
			p->rectType.selRect = Rect(x, y, x0 - x, y0 - y);
		if (flag == EVENT_FLAG_CTRLKEY) //flag 8
			p->rectType.selType = 1;
		if (flag == EVENT_FLAG_ALTKEY)
			p->rectType.selType = 2;
		if (flag == EVENT_FLAG_SHIFTKEY)
			p->rectType.selType = 3;
	}

	p->mouseXY.x = x;
	p->mouseXY.y = y;


}

void PKMVision01::gmm_init()
{
	bool update_bg_model = true;
	bg_model = createBackgroundSubtractorMOG2(500,16,false);
	frame_time = 0;
	/*
	bg_model.set("nmixtures", 3);
	bg_model.set("backgroundRatio", 0.9);
	bg_model.set("backgroundRatio", (float) 0.9);
	bg_model.set("detectShadows", true);
	bg_model.set("nShadowDataction", 0);
	bg_model.set("fVarMin", 5);
	bg_model.set("fTau", 0.5);
	*/
}

void PKMVision01::gmm(Mat* frame, bool smooth)
{
	Mat gimg00 = *frame;
	add(gimg00, NULL, gimg0, imgRoiMask);

	resize(gimg0, gimg, Size(gimg0.cols*rescale, gimg0.rows*rescale), INTER_LINEAR);
	//gimg = gimg0;
	if (fgimg.empty())
		fgimg.create(gimg.size(), gimg.type());

	//update the model
	//bg_model->apply(gimg, fgmask, update_bg_model ? -1 : 0);
	bg_model->apply(gimg, fgmask, -1);
	if (smooth)//(smoothMask)
	{
		GaussianBlur(fgmask, fgmask, Size(11, 11), 3.5, 3.5);
		threshold(fgmask, fgmask, 150, 255, THRESH_BINARY);
	}
	
	fgimg = Scalar::all(0);
	gimg.copyTo(fgimg, fgmask);
	
	// Connected components of foreground mask
	Mat labels, stats, centroids;
	int cc_count = connectedComponentsWithStats(fgmask, labels, stats, centroids, 8, 4);

	// max size is 90% of total foreground size
	int max_size = fgmask.size().area() * 9 / 10;

	int min_size;
	//if small model is used, then min size is 1 pixel
	if (smallModel)
		min_size = 1;
	//if large model is used, then min size is 1% of total foreground size
	else
		min_size = fgmask.size().area() / 100;

	// Check if there is a component, that has correct size
	// if there is, get the maximum
	int max_area = -1;
	int max_label = -1;

	for (int i = 1; i <= cc_count; i++)
	{
		int area = stats.at<int>(i, CC_STAT_AREA);
		if (area < max_size && area > min_size)
		{
			if (area > max_area)
			{
				max_label = i;
				max_area = area;
			}
		}
	}

	prev_centroid = centroid;

	modelPosition = false;
	if (max_label > 0)
	{
		//printf("Selected area no. %d; Area: %d; Center: (%f,%f)\n", max_label, max_area, centroids.at<double>(max_label,0), centroids.at<double>(max_label,1));
		centroid.x = round(centroids.at<double>(max_label, 0));
		centroid.y = round(centroids.at<double>(max_label, 1));
		modelPosition = true;
	}

	v = centroid - prev_centroid;
	v = v * 5;
}
void PKMVision01::opticalFlow(Mat* img)
{
	//float start = (float)getTickCount();
	Mat gray;
	cvtColor(*img, gray, CV_BGR2GRAY);

	TermCriteria termcrit(CV_TERMCRIT_ITER | CV_TERMCRIT_EPS, 20, 0.03);
	Size subPixWinSize(10, 10), winSize(31, 31);

	img->copyTo(flow);

	if (needToInit)
	{
		// automatic initialization
		if (openOpticalFlowWindowAndType == 2){
			if (prevGray.empty())
				gray.copyTo(prevGray);
			points[0].clear();
			points[1].clear();
			goodFeaturesToTrack(prevGray, points[1], MAX_COUNT, 0.01, 10, Mat(), 3, 0, 0.04);
			cornerSubPix(prevGray, points[1], subPixWinSize, Size(-1, -1), termcrit);
			needToInit = false;
		}
		else if (!opticalFlow_isInit){		// manual init (Map of points)
			points[0].clear();
			points[1].clear();
			for (int y = 0; y < gray.rows; y += 30)
				for (int x = 0; x < gray.cols; x += 30)
					points[0].push_back(Point2f(x, y));
			opticalFlow_isInit = true;
			}

	}
	else if (!points[0].empty())
	{
		vector<uchar> status;
		vector<float> err;
		if (prevGray.empty())
			gray.copyTo(prevGray);
		calcOpticalFlowPyrLK(prevGray, gray, points[0], points[1], status, err, winSize,
			3, termcrit, 0, 0.001);

		size_t i, k;
		for (i = k = 0; i < points[1].size(); i++)
		{
			if (!status[i])
				continue;

			points[1][k++] = points[1][i];
			if (openOpticalFlowWindowAndType == 2)
				circle(flow, points[1][i], 3, Scalar(0, 255, 0), -1, 8);
			else
				line(flow, points[0][i], points[1][i], Scalar(0, 255, 0));
			
		}
		points[1].resize(k);
	}

	needToInit = false;

	if (openOpticalFlowWindowAndType == 2)
		std::swap(points[1], points[0]);

	cv::swap(prevGray, gray);
	optFlowCounter++;
	if (optFlowCounter == resetPointsAfter){
	//if (points->size() < 50){
		needToInit = true;
		optFlowCounter = 0;
	}


}
void PKMVision01::drawAreas(Mat* img, bool insideRoi)
{
	int x0 = 0, y0 = 0;
	float scale = 1;
	if (insideRoi){
		x0 = Xmin;
		y0 = Ymin;
		scale = rescale;
	}

	// ROI
	if (rectROI.empty() == 0 && !insideRoi)
		for (int i = 0; i < rectROI.size(); i++)
			 rectangle(*img, rectROI.at(i), Scalar(30, 255, 30));

	// CheckAreas
	if (checkAreas.area.empty() == 0)
		for (int i = 0; i < checkAreas.area.size(); i++)
			if (checkAreas.isObject.at(i) == true)
				rectangle(*img, Rect((checkAreas.area.at(i).x - x0)*scale, (checkAreas.area.at(i).y - y0)*scale, checkAreas.area.at(i).width*scale, checkAreas.area.at(i).height*scale), Scalar(255, 50, 0),-1);
			else
				rectangle(*img, Rect((checkAreas.area.at(i).x - x0)*scale, (checkAreas.area.at(i).y - y0)*scale, checkAreas.area.at(i).width*scale, checkAreas.area.at(i).height*scale), Scalar(255, 50, 0));

	// White Area
	if (whiteArea.width != 0 && whiteArea.height != 0)
		rectangle(*img, Rect((whiteArea.x - x0)*scale, (whiteArea.y - y0)*scale, whiteArea.width*scale, whiteArea.height*scale), Scalar(0, 255, 255));
}
void PKMVision01::setMultiROI(Mat* img)
{
	int border = 20;
	if (mParams.rectType.selRect.width != 0 && mParams.rectType.selRect.height != 0){
		if (mParams.rectType.selRect.x < border) mParams.rectType.selRect.x = 0;
		if (mParams.rectType.selRect.y < border) mParams.rectType.selRect.y = 0;
		if (mParams.rectType.selRect.x + mParams.rectType.selRect.width > img->cols - border) mParams.rectType.selRect.width = img->cols - mParams.rectType.selRect.x;
		if (mParams.rectType.selRect.y + mParams.rectType.selRect.height  > img->rows - border) mParams.rectType.selRect.height = img->rows - mParams.rectType.selRect.y;
		if (mParams.rectType.selType == 1)
			rectROI.push_back(mParams.rectType.selRect);
		if (mParams.rectType.selType == 2)
			checkAreas.area.push_back(mParams.rectType.selRect);
		if (mParams.rectType.selType == 3)
			whiteArea = mParams.rectType.selRect;
		mParams.rectType.selRect = Rect(0, 0, 0, 0);
		checkAreas.isObject.push_back(false);
	}
}
void PKMVision01::calcWhiteArea(Mat* orgFrame)
{
	Mat frame = *orgFrame;
	Mat mask = Mat::zeros(frame.size(), CV_8U);
	rectangle(mask, whiteArea, Scalar(255, 255, 255));
	meanVal = mean(frame,mask);
	
}
void PKMVision01::areasObjDetect()
{
	double areaThresh = 0.3;
	if (checkAreas.area.empty() == 0)
		for (int i = 0; i < checkAreas.area.size(); i++){
			int area = checkAreas.area.at(i).width*checkAreas.area.at(i).height;	// calc actual check area
			// skawlowanie wsp.

			int x = (checkAreas.area.at(i).x - Xmin)*rescale;
			int y = (checkAreas.area.at(i).y - Ymin)*rescale;
			int w = checkAreas.area.at(i).width*rescale;
			int h = checkAreas.area.at(i).height*rescale;
			
			int area2;
			try{ 
				area2 = countNonZero(fgmask(Rect(x, y, w, h))); 
				//rectangle(fgimg, Rect(x,y,w,h), Scalar(255, 50, 255)); //testing
				if ((double)area2 / (double)area > areaThresh && startDelay == 0)
					checkAreas.isObject.at(i) = true;
				else
					checkAreas.isObject.at(i) = false;
			} catch (cv::Exception &e){
				printf("CheckArea (blue) outside ROI: %c\n Exit Program. Press any key...", e.msg);
				getchar();
				exit(0);
			}	
		}
}
Mat PKMVision01::resizeToROImask(Mat* img0)
{
	Mat img, roi, imgWithRoi;
	img = *img0;
	if (img0->empty() || !paramsLoaded)
		return img;
	else if (img0->cols >= Xmax && img0->rows >= Ymax) {
		roi =  img(Rect(Xmin,Ymin,Xmax-Xmin,Ymax-Ymin));
		roi.copyTo(imgWithRoi);	
		return imgWithRoi;
	}else
		return img;
}
bool PKMVision01::setROImask()
{
	if (!rectROI.empty()) {
		Xmin = 1000;
		Xmax = 0;
		Ymin = 1000;
		Ymax = 0;
		for (int i = 0; i < rectROI.size(); i++){
			if (rectROI.at(i).x < Xmin) Xmin = rectROI.at(i).x;
			if (rectROI.at(i).y < Ymin) Ymin = rectROI.at(i).y;
			if (rectROI.at(i).x + rectROI.at(i).width > Xmax) Xmax = rectROI.at(i).x + rectROI.at(i).width;
			if (rectROI.at(i).y + rectROI.at(i).height > Ymax) Ymax = rectROI.at(i).y + rectROI.at(i).height;
		}
		imgRoiMask = Mat::zeros(Size(Xmax - Xmin, Ymax - Ymin), CV_8UC1);
		for (int i = 0; i < rectROI.size(); i++){
			rectangle(imgRoiMask, Rect(rectROI.at(i).x - Xmin, rectROI.at(i).y - Ymin, rectROI.at(i).width, rectROI.at(i).height), Scalar(255, 255, 255), -1);
		}
		return true;
	}else
		imgRoiMask = Mat::zeros(gimg.size(),gimg.type());
		return false;

}
bool PKMVision01::loadParams(const string &filenameParam)
{
	if (filenameParam.empty())
		return false;
	Mat maxmin;
	FileStorage fs;
	try {
		fs.open(filenameParam, FileStorage::READ);
		fs["ROIcoords"] >> rectROI;
		fs["ROImaxmin"] >> maxmin;
		fs["CheckAreas"] >> checkAreas.area;
		fs["WhiteArea"] >> whiteArea;
		fs["RecordViewNr"] >> recView;
		fs.release();
	}
	catch (...)
	{
		return false;
	}

	Xmin = maxmin.at<int>(0);
	Ymin = maxmin.at<int>(1);
	Xmax = maxmin.at<int>(2);
	Ymax = maxmin.at<int>(3);

	for (int i = 0; i < checkAreas.area.size(); i++)
		checkAreas.isObject.push_back(false);

	if (rectROI.empty())
		return false;
	else
		return true;

	// optional TODO: check if loaded OK but wrong Mat size
}
bool PKMVision01::saveParams(const string &filenameParam)
{
	if (rectROI.empty()){
		printf("NO ROI");
			return false;
	}
	setROImask();
	Mat maxmin = (Mat_<int>(4, 1) << Xmin, Ymin, Xmax, Ymax);


	FileStorage fs(filenameParam, FileStorage::WRITE);
	if (!fs.isOpened())
		return false;
	fs << "Params" << "camera setup";
	fs << "ROIcoords" << rectROI;
	fs << "ROImaxmin" << maxmin;
	fs << "CheckAreas" << checkAreas.area;
	fs << "WhiteArea" << whiteArea;
	fs << "RecordViewNr" << recView;
	fs.release();
}

