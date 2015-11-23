#include "NetCam.h"
using namespace cv;

NetCam::NetCam()
{
	// Register all formats and codecs, network protocols
	av_register_all();
	avcodec_register_all();
	avformat_network_init();

	videoStream = 0;
	frameFinished = 0;
	numBytes = 0;
	recordingOutput = false;
	readyToRecord = false;
}


NetCam::~NetCam()
{
}

int NetCam::init()
{
	// Allocate video frame
	pFrame = av_frame_alloc();
	// Allocate an AVFrame structure
	pFrameBGR = av_frame_alloc();

	if (pFrameBGR == NULL){
		printf("Could not allocate frame");//return -1;
		return -1;
	}
	else
		return 0;
}

int NetCam::open(char* camIpAddress,int camType)
{
	this->camType = camType;

	AVDictionary *options = NULL;
	AVInputFormat* fmt = NULL;
	AVDictionaryEntry *t = NULL;  //to check option entries

	//av_dict_set(&options, "max_delay", "200000", 0);
	//av_dict_set(&options, "rtbufsize", "10000", 0);

	if (camType==1) //SAMSUNG
	{
		//av_dict_set(&options, "rtsp_transport", "tcp", 0);
		//av_dict_set(&options, "pixel_format", "rgb24", 0);
		if (avformat_open_input(&pFormatCtx, camIpAddress, fmt, &options))
			return -1;
	}
	else if (camType == 2) //AI-BALL
	{
		char * format = "mjpeg";
		fmt = av_find_input_format(format);
		if (avformat_open_input(&pFormatCtx, camIpAddress, fmt, &options))
			return -1;
	}
	else if (camType == 0){ // FROM FILE
		if (avformat_open_input(&pFormatCtx, camIpAddress, NULL, NULL))
			return -1;
	}
	else
		return -1;

	while (t = av_dict_get(options, "", t, AV_DICT_IGNORE_SUFFIX)) {
		printf("Option %s not recognized by the demuxer.\n", t->key);
	}
	av_dict_free(&options);

	// Retrieve stream information
	if (avformat_find_stream_info(pFormatCtx, NULL)<0)
		return -1; // Couldn't find stream information

	// Dump information about file onto standard error
	av_dump_format(pFormatCtx, 0, camIpAddress, 0);

	// Find the first video stream
	videoStream = -1;
	for (int i = 0; i<pFormatCtx->nb_streams; i++)
		if (pFormatCtx->streams[i]->codec->codec_type == AVMEDIA_TYPE_VIDEO) {
		videoStream = i;
		break;
		}
	if (videoStream == -1)
		return -1; // Didn't find a video stream

	// Get a pointer to the codec context for the video stream
	pCodecCtx = pFormatCtx->streams[videoStream]->codec;
	// Find the decoder for the video stream
	pCodec = avcodec_find_decoder(pCodecCtx->codec_id);
	if (pCodec == NULL) {
		fprintf(stderr, "Unsupported codec!\n");
		return -1; // Codec not found
	}
	// Open codec
	if (avcodec_open2(pCodecCtx, pCodec, NULL)<0)
		return -1; // Could not open codec

	// Determine required buffer size and allocate buffer
	numBytes = avpicture_get_size(PIX_FMT_RGB24, pCodecCtx->width,
		pCodecCtx->height);
	buffer = (uint8_t *)av_malloc(numBytes*sizeof(uint8_t));

	// Assign appropriate parts of buffer to image planes in pFrameBGR
	// Note that pFrameBGR is an AVFrame, but AVFrame is a superset
	// of AVPicture
	if (init() != 0)
		return -1;

	avpicture_fill((AVPicture *)pFrameBGR, buffer, PIX_FMT_BGR24,
		pCodecCtx->width, pCodecCtx->height);

	// initialize SWS context for software scaling
	sws_ctx = sws_getContext(pCodecCtx->width,
		pCodecCtx->height,
		pCodecCtx->pix_fmt,
		pCodecCtx->width,
		pCodecCtx->height,
		PIX_FMT_BGR24,
		SWS_BILINEAR,
		NULL,
		NULL,
		NULL
		);


	return 0;
}
Mat NetCam::readFrame()
{
	// Convert the image from its native format to BGR
	sws_scale(sws_ctx, (uint8_t const * const *)pFrame->data,
		pFrame->linesize, 0, pCodecCtx->height,
		pFrameBGR->data, pFrameBGR->linesize);

	frame = avFrame2Mat(pFrame);

	return frame;
}
bool NetCam::initSaveVideo(Mat* img, char* filename)
{
	//outputVideo.open("D:\\outputVideo.avi", CV_FOURCC('D', 'I', 'V', 'X'), 20, img->size(), true);
	//status = outputVideo.open(filename, CV_FOURCC('D', 'I', 'V', 'X'), 10, img->size(), true);
	int status;
	if (readyToRecord == false)
		status = outputVideo.open(filename, CV_FOURCC('D', 'I', 'V', 'X'), 10, img->size(), true);
	if (!outputVideo.isOpened()){
		readyToRecord = false;
		return false;
	}
	else{
		readyToRecord = true;
		return true;
	}
}
void NetCam::saveVideoFrames(Mat* img)
{
	Mat outputFrame = *img;
	outputVideo.write(outputFrame);
}
void NetCam::closeSaveVideo()
{
	outputVideo.release();
}
Mat NetCam::avFrame2Mat(AVFrame *frame)
{
	AVFrame dst;
	cv::Mat m;
	memset(&dst, 0, sizeof(dst));
	int w = frame->width, h = frame->height;
	m = cv::Mat(h, w, CV_8UC3);
	dst.data[0] = (uint8_t *)m.data;
	avpicture_fill((AVPicture *)&dst, dst.data[0], PIX_FMT_BGR24, w, h);
	struct SwsContext *convert_ctx = NULL;
	enum PixelFormat src_pixfmt = (enum PixelFormat)frame->format;
	enum PixelFormat dst_pixfmt = PIX_FMT_BGR24;
	convert_ctx = sws_getContext(w, h, src_pixfmt, w, h, dst_pixfmt,
		SWS_FAST_BILINEAR, NULL, NULL, NULL);
	sws_scale(convert_ctx, frame->data, frame->linesize, 0, h,
		dst.data, dst.linesize);
	sws_freeContext(convert_ctx);
	return m;
}
void NetCam::close()
{
	// Free the RGB image
	av_free(buffer);
	av_free(pFrameBGR);

	// Free the YUV frame
	av_free(pFrame);

	// Close the codec
	avcodec_close(pCodecCtx);

	// Close the video file
	avformat_close_input(&pFormatCtx);
}