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

} ImageProperties2;

typedef struct
{
	wchar_t* fontName;
	DWRITE_FONT_WEIGHT fontWeight;
	DWRITE_FONT_STRETCH fontStretch;
	DWRITE_FONT_STYLE fontStyle;
	UINT32 fontBidiLevel;
	FLOAT fontEmSize;

} TextProperties2;

typedef struct
{
	int maxGlyphsPerLine;
	int maxLines;

} RenderedTextInformation2;

typedef struct TextRenderer2 TextRenderer2;
extern "C" TEXTRENDERER_API int Initialize2();
extern "C" TEXTRENDERER_API int CreateInstance(TextRenderer2** instance);
extern "C" TEXTRENDERER_API int SetImageProperties2(TextRenderer2* instance, ImageProperties2* imageProps);
extern "C" TEXTRENDERER_API int SetTextProperties2(TextRenderer2* instance, TextProperties2* textProps, BOOL* fontExists);
extern "C" TEXTRENDERER_API int GetRenderedTextInformation2(TextRenderer2* instance, wchar_t* charSet, D2D1_RECT_F* pTextBounds, RenderedTextInformation2* pTextInformation);
extern "C" TEXTRENDERER_API int RenderString2(TextRenderer2* instance, wchar_t* str, int strLen, D2D1_RECT_F* pTextBounds, BOOL clearBackground, BOOL drawBoundingBoxes, BYTE* pImageBuffer, D2D1_RECT_F** ppOutBoundingBoxes, int* boundingBoxesCount);
extern "C" TEXTRENDERER_API int RenderRectangles2(TextRenderer2* instance, D2D1_RECT_F* pRectangles, int rectanglesCount, BYTE* pImageBuffer);
extern "C" TEXTRENDERER_API int SaveImageAsPng2(TextRenderer2* instance, wchar_t* imageFilename, BYTE* pImageBuffer);
extern "C" TEXTRENDERER_API void DestroyInstance(TextRenderer2* instance);
extern "C" TEXTRENDERER_API void Uninitialize2();
extern "C" TEXTRENDERER_API void DeleteArray2(void* arr);