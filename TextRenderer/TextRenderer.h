#pragma once

#ifdef TEXTRENDERER_EXPORTS
#define TEXTRENDERER_API __declspec(dllexport)
#else
#define TEXTRENDERER_API __declspec(dllimport)
#endif

typedef struct
{
	int imageHeight;
	int imageWidth;
	int bitsPerPixel;
	GUID WICPixelFormat;

} ImageProperties;

typedef struct
{
	wchar_t* fontName;
	DWRITE_FONT_WEIGHT fontWeight;
	DWRITE_FONT_STRETCH fontStretch;
	DWRITE_FONT_STYLE fontStyle;
	UINT32 fontBidiLevel;
	FLOAT fontEmSize;

} TextProperties;

extern "C" TEXTRENDERER_API int Initialize();
extern "C" TEXTRENDERER_API int SetImageProperties(ImageProperties* imageProps);
extern "C" TEXTRENDERER_API int SetTextProperties(TextProperties* textProps, BOOL* fontExists);
extern "C" TEXTRENDERER_API HRESULT RenderString(wchar_t* str, int strLen, D2D1_RECT_F* pTextBounds, BOOL clearBackground, BOOL drawBoundingBoxes, BYTE* pImageBuffer, D2D1_RECT_F** ppOutBoundingBoxes, int* boundingBoxesCount);
extern "C" TEXTRENDERER_API void DeleteArray(void* arr);
extern "C" TEXTRENDERER_API void Uninitialize();