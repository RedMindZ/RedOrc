// TextRenderer.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "TextRenderer.h"


// Forward declaration
template <class T> void SafeRelease(T **ppT);




ID2D1Factory* pD2DFactory = NULL;
ID2D1BitmapRenderTarget* pRT = NULL;
ID2D1SolidColorBrush* pBlackBrush = NULL;
ID2D1SolidColorBrush* pPurpleBrush = NULL;

IDWriteFactory* pDWriteFactory = NULL;

IWICImagingFactory* pWICFactory = NULL;
IWICBitmap* pWICBitmap = NULL;
IWICFormatConverter* pFormatConverter = NULL;

int imageHeight = 0;
int imageWidth = 0;
int imageBitsPerPixel = 0;


IDWriteFontFace* pFontFace = NULL;

UINT32 fontBidiLevel = 0;
FLOAT fontEmSize = 0;




// Image buffer must have at least height * width bytes available
int Init()
{
	// Create the D2D factory
	HRESULT hr = D2D1CreateFactory(D2D1_FACTORY_TYPE_SINGLE_THREADED, &pD2DFactory);

	// Create the DWrite factory
	if (SUCCEEDED(hr))
	{
		hr = DWriteCreateFactory(DWRITE_FACTORY_TYPE_SHARED, __uuidof(IDWriteFactory), reinterpret_cast<IUnknown**>(&pDWriteFactory));
	}

	// Init COM
	if (SUCCEEDED(hr))
	{
		hr = CoInitialize(NULL);
	}

	// Create WICFactory
	if (SUCCEEDED(hr))
	{
		hr = CoCreateInstance(CLSID_WICImagingFactory, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pWICFactory));
	}

	return hr;
}

int SetImageProperties(ImageProperties* imageProps)
{
	imageHeight = imageProps->imageHeight;
	imageWidth = imageProps->imageWidth;
	imageBitsPerPixel = imageProps->bitsPerPixel;

	// Create an IWICBitmap
	SafeRelease(&pWICBitmap);
	HRESULT hr = pWICFactory->CreateBitmap(imageWidth, imageHeight, GUID_WICPixelFormat32bppBGR, WICBitmapCacheOnDemand, &pWICBitmap);

	// Create a WIC format converter
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pFormatConverter);
		hr = pWICFactory->CreateFormatConverter(&pFormatConverter);
	}

	// Initialize the format converter
	if (SUCCEEDED(hr))
	{
		hr = pFormatConverter->Initialize(pWICBitmap, GUID_WICPixelFormat32bppRGBA, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	}

	// Create a Direct2D render target.
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pRT);
		hr = pD2DFactory->CreateWicBitmapRenderTarget(pWICBitmap, D2D1::RenderTargetProperties(), (ID2D1RenderTarget **)&pRT);
	}

	// Create a black brush.
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pBlackBrush);
		hr = pRT->CreateSolidColorBrush(D2D1::ColorF(D2D1::ColorF::Black), &pBlackBrush);
	}

	// Create a purple brush.
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pPurpleBrush);
		hr = pRT->CreateSolidColorBrush(D2D1::ColorF(D2D1::ColorF::Purple), &pPurpleBrush);
	}

	return hr;
}

int SetTextProperties(TextProperties* textProps, BOOL* fontExists)
{
	// Get system fonts
	IDWriteFontCollection* pSystemFontCollection = NULL;
	HRESULT hr = pDWriteFactory->GetSystemFontCollection(&pSystemFontCollection);

	// Find a matching font family
	UINT32 familyIndex;
	if (SUCCEEDED(hr))
	{
		hr = pSystemFontCollection->FindFamilyName(textProps->fontName, &familyIndex, fontExists);
	}

	if (!*fontExists)
	{
		SafeRelease(&pSystemFontCollection);
		return hr;
	}

	// Find the font family
	IDWriteFontFamily* pFontFamily = NULL;
	if (SUCCEEDED(hr))
	{
		hr = pSystemFontCollection->GetFontFamily(familyIndex, &pFontFamily);
	}

	// Find the font
	IDWriteFont* pFont = NULL;
	if (SUCCEEDED(hr))
	{
		hr = pFontFamily->GetFirstMatchingFont(textProps->fontWeight, textProps->fontStretch, textProps->fontStyle, &pFont);
	}

	// Find the font face
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pFontFace);
		hr = pFont->CreateFontFace(&pFontFace);
	}

	// Set the font size and bidi level
	if (SUCCEEDED(hr))
	{
		fontBidiLevel = textProps->fontBidiLevel;
		fontEmSize = textProps->fontEmSize;
	}

	SafeRelease(&pFont);
	SafeRelease(&pFontFamily);
	SafeRelease(&pSystemFontCollection);

	return hr;
}

void GetVisibleGlyphsCount(wchar_t* str, int strLen, int* glyphCount)
{
	*glyphCount = 0;

	for (int i = 0; i < strLen; i++)
	{
		if (iswgraph(str[i]))
		{
			(*glyphCount)++;
		}
	}
}

void ReleaseGlyphRunCollection(DWRITE_GLYPH_RUN** glyphRunCollection, int collectionLength)
{
	for (int i = 0; i < collectionLength; i++)
	{
		if ((*glyphRunCollection)[i].glyphIndices != NULL)
		{
			delete[](*glyphRunCollection)[i].glyphIndices;
		}

		if ((*glyphRunCollection)[i].glyphAdvances != NULL)
		{
			delete[](*glyphRunCollection)[i].glyphAdvances;
		}

		if ((*glyphRunCollection)[i].glyphOffsets != NULL)
		{
			delete[](*glyphRunCollection)[i].glyphOffsets;
		}
	}

	delete[] * glyphRunCollection;
	*glyphRunCollection = NULL;
}

// This function is for internal use only.
//
// The caller must free the following, unless the function fails:
// * ppGlyphBoundingBoxes - use delete[]
// * ppGlyphRunsOrigins - use delete[]
// * ppGlyphRuns - use ReleaseGlyphRunCollection
HRESULT AnalyzeString
(
	wchar_t* str,
	int strLen,
	D2D1_POINT_2F* pBaselineOrigin,
	D2D1_RECT_F* pTextBounds,
	D2D1_RECT_F **ppGlyphBoundingBoxes,
	D2D1_POINT_2F** ppGlyphRunsOrigins,
	DWRITE_GLYPH_RUN** ppGlyphRuns,
	int* pGlyphRunsCount,
	int* pTotalGlyphCount
)
{
	// Get the total number of visible glyphs in the string
	GetVisibleGlyphsCount(str, strLen, pTotalGlyphCount);

	// Translate the string to a list of UINT32
	std::vector<UINT32> vCodePoints(strLen);
	for (int i = 0; i < strLen; i++)
	{
		vCodePoints[i] = str[i];
	}

	// Get the glyph indices for the string
	std::vector<UINT16> vGlyphIndices(strLen);
	HRESULT hr = pFontFace->GetGlyphIndicesW(vCodePoints.data(), vCodePoints.size(), vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	// Get the metrics for the glyphs
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMetrics(strLen);
	hr = pFontFace->GetDesignGlyphMetrics(vGlyphIndices.data(), vGlyphIndices.size(), vGlyphMetrics.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}


	DWRITE_FONT_METRICS fontMetrics;
	pFontFace->GetMetrics(&fontMetrics);

	float fontScale = fontEmSize / fontMetrics.designUnitsPerEm;
	int textBoundsWidth = pTextBounds->right - pTextBounds->left;
	int currentGlyphRunWidth = 0;
	int currentGlyphCount = 0;
	*pGlyphRunsCount = 0;

	// Compute the number of glyph runs in the string

	for (int i = 0; i < strLen; i++)
	{
		int isVisible = iswgraph(str[i]);

		if (isVisible)
		{
			if (currentGlyphCount == 0)
			{
				(*pGlyphRunsCount)++;
			}

			currentGlyphCount++;
			currentGlyphRunWidth += vGlyphMetrics[i].advanceWidth * fontScale;
		}

		if (currentGlyphRunWidth > textBoundsWidth && currentGlyphCount > 1)
		{
			(*pGlyphRunsCount)++;

			currentGlyphCount = 1;
			currentGlyphRunWidth = vGlyphMetrics[i].advanceWidth * fontScale;
		}
	}

	*ppGlyphRunsOrigins = new D2D1_POINT_2F[*pGlyphRunsCount];
	D2D1_POINT_2F currentOrigin = *pBaselineOrigin;

	int originIndex = 0;
	currentGlyphRunWidth = 0;
	currentGlyphCount = 0;

	int lineGap = (fontMetrics.ascent + fontMetrics.descent + fontMetrics.lineGap) * fontScale;

	// Compute the origin of each glyph run:
	// As long we see whitespace characters, we just move the origin.
	// If the whitespace causes the origin to overhang the right bound, we move down a line.
	// If we hit the whitespace after we saw glyphs, then we move to calculating the next origin.
	// When we see visual glyphs, we keep the origin constant and increase the run's width.
	// If the width + origin.x overhangs the right bound, we move the origin to the next line.
	// If the width by itself overhangs the right bound, the we move to the next glyph run.

	for (int i = 0; i < strLen; i++)
	{
		int isVisible = iswgraph(str[i]);

		if (isVisible)
		{
			if (currentGlyphCount == 0)
			{
				(*ppGlyphRunsOrigins)[originIndex] = currentOrigin;
			}

			currentGlyphCount++;
			currentGlyphRunWidth += vGlyphMetrics[i].advanceWidth * fontScale;
		}
		else
		{
			if (currentGlyphCount > 0)
			{
				currentOrigin.x += currentGlyphRunWidth;

				originIndex++;
				currentGlyphCount = 0;
				currentGlyphRunWidth = 0;
			}

			if (str[i] == L'\r')
			{
				currentOrigin.x = pTextBounds->left;
			}
			else if (str[i] == L'\n')
			{
				currentOrigin.x = pTextBounds->left;
				currentOrigin.y += lineGap;
			}

			if (currentOrigin.x + vGlyphMetrics[i].advanceWidth * fontScale > pTextBounds->right)
			{
				currentOrigin.x = pTextBounds->left;
				currentOrigin.y += lineGap;
			}
			else
			{
				currentOrigin.x += vGlyphMetrics[i].advanceWidth * fontScale;
			}
		}

		if (currentGlyphRunWidth > textBoundsWidth)
		{
			if (currentGlyphCount > 1)
			{
				originIndex++;

				currentOrigin.x = pTextBounds->left;
				currentOrigin.y = currentOrigin.y + lineGap;

				(*ppGlyphRunsOrigins)[originIndex] = currentOrigin;

				currentGlyphCount = 1;
				currentGlyphRunWidth = vGlyphMetrics[i].advanceWidth * fontScale;
			}
		}
		else if (currentOrigin.x + currentGlyphRunWidth > pTextBounds->right)
		{
			currentOrigin.x = pTextBounds->left;
			currentOrigin.y += lineGap;

			(*ppGlyphRunsOrigins)[originIndex] = currentOrigin;
		}
	}

	*ppGlyphBoundingBoxes = new D2D1_RECT_F[*pTotalGlyphCount];

	currentOrigin = (*ppGlyphRunsOrigins)[0];
	int boxIndex = 0;

	originIndex = 0;
	currentGlyphRunWidth = 0;
	currentGlyphCount = 0;

	// Compute the bounding boxes for each glyph

	for (int i = 0; i < strLen; i++)
	{
		if (iswgraph(str[i]))
		{
			if (currentGlyphCount == 0)
			{
				currentOrigin = (*ppGlyphRunsOrigins)[originIndex];
			}

			currentGlyphCount++;
			currentGlyphRunWidth += vGlyphMetrics[i].advanceWidth * fontScale;

			if (currentGlyphRunWidth > textBoundsWidth && currentGlyphCount > 1)
			{
				originIndex++;
				currentOrigin = (*ppGlyphRunsOrigins)[originIndex];

				currentGlyphCount = 1;
				currentGlyphRunWidth = vGlyphMetrics[i].advanceWidth * fontScale;
			}

			float rectWidth = (vGlyphMetrics[i].advanceWidth - (vGlyphMetrics[i].leftSideBearing + vGlyphMetrics[i].rightSideBearing)) * fontScale;
			float rectHeight = (vGlyphMetrics[i].advanceHeight - (vGlyphMetrics[i].topSideBearing + vGlyphMetrics[i].bottomSideBearing)) * fontScale;

			float topOffset = ((fontMetrics.ascent + fontMetrics.descent) - vGlyphMetrics[i].advanceHeight);

			float top = currentOrigin.y + (vGlyphMetrics[i].topSideBearing + topOffset - fontMetrics.ascent) * fontScale;
			float left = currentOrigin.x + vGlyphMetrics[i].leftSideBearing * fontScale;

			(*ppGlyphBoundingBoxes)[boxIndex].top = top;
			(*ppGlyphBoundingBoxes)[boxIndex].bottom = top + rectHeight;
			(*ppGlyphBoundingBoxes)[boxIndex].left = left;
			(*ppGlyphBoundingBoxes)[boxIndex].right = left + rectWidth;

			currentOrigin.x += vGlyphMetrics[i].advanceWidth * fontScale;
			boxIndex++;
		}
		else
		{
			currentGlyphCount = 0;
			currentGlyphRunWidth = 0;
		}
	}

	*ppGlyphRuns = new DWRITE_GLYPH_RUN[*pGlyphRunsCount];

	int glyphRunIndex = 0;
	currentGlyphCount = 0;
	currentGlyphRunWidth = 0;
	originIndex = 0;
	currentOrigin = (*ppGlyphRunsOrigins)[0];

	// Lastly, build the glyph runs themselves

	for (int i = 0; i < strLen; i++)
	{
		int isVisible = iswgraph(str[i]);

		if (isVisible)
		{
			currentGlyphCount++;
			currentGlyphRunWidth += vGlyphMetrics[i].advanceWidth * fontScale;


		}
		else if (currentGlyphCount > 0)
		{
			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = pFontFace;
			(*ppGlyphRuns)[glyphRunIndex].isSideways = FALSE;
			(*ppGlyphRuns)[glyphRunIndex].glyphCount = currentGlyphCount;
			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphOffsets = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphAdvances = NULL;

			// Get the glyph indices
			UINT16* pGlyphIndices = new UINT16[currentGlyphCount];
			for (int j = 0; j < currentGlyphCount; j++)
			{
				pGlyphIndices[j] = vGlyphIndices[j + i - currentGlyphCount];
			}

			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = pGlyphIndices;

			currentGlyphCount = 0;
			currentGlyphRunWidth = 0;
			glyphRunIndex++;
		}

		if (currentGlyphRunWidth > textBoundsWidth && currentGlyphCount > 1)
		{
			currentGlyphCount--;

			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = pFontFace;
			(*ppGlyphRuns)[glyphRunIndex].isSideways = FALSE;
			(*ppGlyphRuns)[glyphRunIndex].glyphCount = currentGlyphCount;
			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphOffsets = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphAdvances = NULL;

			// Get the glyph indices
			UINT16* pGlyphIndices = new UINT16[currentGlyphCount];
			for (int j = 0; j < currentGlyphCount; j++)
			{
				pGlyphIndices[j] = vGlyphIndices[j + i - currentGlyphCount];
			}

			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = pGlyphIndices;

			currentGlyphCount = 0;
			currentGlyphRunWidth = 0;
			glyphRunIndex++;
			i--;
		}

		if (isVisible && i == strLen - 1)
		{
			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = pFontFace;
			(*ppGlyphRuns)[glyphRunIndex].isSideways = FALSE;
			(*ppGlyphRuns)[glyphRunIndex].glyphCount = currentGlyphCount;
			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphOffsets = NULL;
			(*ppGlyphRuns)[glyphRunIndex].glyphAdvances = NULL;

			// Get the glyph indices
			UINT16* pGlyphIndices = new UINT16[currentGlyphCount];
			for (int j = 0; j < currentGlyphCount; j++)
			{
				pGlyphIndices[j] = vGlyphIndices[j + i - currentGlyphCount + 1];
			}

			(*ppGlyphRuns)[glyphRunIndex].glyphIndices = pGlyphIndices;

			currentGlyphCount = 0;
			currentGlyphRunWidth = 0;
		}
	}
}

HRESULT RenderString2
(
	wchar_t* str,
	int strLen,
	D2D1_POINT_2F* pBaselineOrigin,
	D2D1_RECT_F* pTextBounds,
	BOOL clearBackground,
	BOOL drawBoundingBoxes,
	BYTE* pImageBuffer
)
{
	BOOL isVisible = FALSE;

	for (int i = 0; i < strLen; i++)
	{
		if (iswgraph(str[i]))
		{
			isVisible = TRUE;
			break;
		}
	}

	if (!isVisible)
	{
		return E_INVALIDARG;
	}

	D2D1_RECT_F* pGlyphBoundingBoxes;
	D2D1_POINT_2F* pGlyphRunsOrigins;
	DWRITE_GLYPH_RUN* pGlyphRuns;
	int glyphRunsCount;
	int totalGlyphCount;

	HRESULT hr = AnalyzeString(str, strLen, pBaselineOrigin, pTextBounds, &pGlyphBoundingBoxes, &pGlyphRunsOrigins, &pGlyphRuns, &glyphRunsCount, &totalGlyphCount);
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	pRT->BeginDraw();

	if (clearBackground)
	{
		pRT->Clear(D2D1::ColorF(D2D1::ColorF::White));
	}

	for (int i = 0; i < glyphRunsCount; i++)
	{
		pRT->DrawGlyphRun(pGlyphRunsOrigins[i], &(pGlyphRuns[i]), pBlackBrush);
	}

	if (drawBoundingBoxes)
	{
		for (int i = 0; i < totalGlyphCount; i++)
		{
			pRT->DrawRectangle(pGlyphBoundingBoxes + i, pBlackBrush);
		}
	}

	hr = pRT->EndDraw();

	if (SUCCEEDED(hr))
	{
		hr = pFormatConverter->CopyPixels(NULL, imageWidth * imageBitsPerPixel / 8, imageWidth * imageHeight * imageBitsPerPixel / 8, pImageBuffer);
	}

	delete[] pGlyphBoundingBoxes;
	delete[] pGlyphRunsOrigins;
	ReleaseGlyphRunCollection(&pGlyphRuns, glyphRunsCount);

	return hr;
}

HRESULT RenderString(wchar_t* str, int strLen, BYTE* imageBuffer, D2D1_RECT_F* textBounds, BOOL clearBackground)
{
	// Create a glyph run
	DWRITE_GLYPH_RUN glyphRun;
	glyphRun.bidiLevel = fontBidiLevel;
	glyphRun.fontEmSize = fontEmSize;
	glyphRun.fontFace = pFontFace;
	glyphRun.glyphAdvances = NULL;
	glyphRun.glyphOffsets = NULL;
	glyphRun.isSideways = FALSE;

	// Translate the text to a list of UINT32
	std::vector<UINT16> vGlyphIndices(strLen);
	std::vector<UINT32> vCodePoints(strLen);
	for (int i = 0; i < strLen; i++)
	{
		vCodePoints[i] = str[i];
	}

	// Get the glyph indices
	HRESULT hr = glyphRun.fontFace->GetGlyphIndicesW(vCodePoints.data(), strLen, vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	// Finish building the glyph run
	glyphRun.glyphCount = strLen;
	glyphRun.glyphIndices = vGlyphIndices.data();

	// Get glyph matrics
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMatrics(glyphRun.glyphCount);
	hr = pFontFace->GetDesignGlyphMetrics(glyphRun.glyphIndices, glyphRun.glyphCount, vGlyphMatrics.data(), glyphRun.isSideways);
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	// Get font matrics
	DWRITE_FONT_METRICS fontMetrics;
	pFontFace->GetMetrics(&fontMetrics);

	// Start drawing
	pRT->BeginDraw();

	pRT->SetAntialiasMode(D2D1_ANTIALIAS_MODE_ALIASED);
	if (clearBackground)
	{
		pRT->Clear(D2D1::ColorF(D2D1::ColorF::White));
	}

	// Draw the glyph bounding boxes
	float scale = glyphRun.fontEmSize / fontMetrics.designUnitsPerEm;
	D2D1_POINT_2F currentOrigin = { textBounds->left, textBounds->top + vGlyphMatrics[0].verticalOriginY * scale };
	D2D1_POINT_2F lineOrigin = currentOrigin;
	DWRITE_GLYPH_RUN drawGlyphRun = glyphRun;
	std::vector<D2D1_RECT_F> vGlyphRect(glyphRun.glyphCount);
	int lineGlyphCount = 0;
	for (UINT32 i = 0; i < glyphRun.glyphCount; i++)
	{
		float rectWidth = (vGlyphMatrics[i].advanceWidth - (vGlyphMatrics[i].leftSideBearing + vGlyphMatrics[i].rightSideBearing)) * scale;
		float rectHeight = (vGlyphMatrics[i].advanceHeight - (vGlyphMatrics[i].topSideBearing + vGlyphMatrics[i].bottomSideBearing)) * scale;
		float topOffset = ((fontMetrics.ascent + fontMetrics.descent) - vGlyphMatrics[i].advanceHeight);

		vGlyphRect[i].top = currentOrigin.y + (vGlyphMatrics[i].topSideBearing + topOffset - fontMetrics.ascent) * scale;
		vGlyphRect[i].bottom = vGlyphRect[i].top + rectHeight;
		vGlyphRect[i].left = currentOrigin.x + vGlyphMatrics[i].leftSideBearing * scale;
		vGlyphRect[i].right = vGlyphRect[i].left + rectWidth;

		pRT->DrawRectangle(vGlyphRect[i], pBlackBrush, 1.0F);

		currentOrigin.x += vGlyphMatrics[i].advanceWidth * scale;
		lineGlyphCount++;

		if (i < glyphRun.glyphCount - 1 && currentOrigin.x + vGlyphMatrics[i + 1].advanceWidth * scale > textBounds->right)
		{
			drawGlyphRun.glyphCount = lineGlyphCount;
			pRT->DrawGlyphRun(lineOrigin, &drawGlyphRun, pBlackBrush);

			currentOrigin.x = textBounds->left;
			currentOrigin.y += (fontMetrics.ascent + fontMetrics.descent + fontMetrics.lineGap) * scale;
			lineOrigin = currentOrigin;
			drawGlyphRun.glyphIndices += lineGlyphCount;
			lineGlyphCount = 0;
		}
	}

	// Draw the last line
	drawGlyphRun.glyphCount = lineGlyphCount;
	pRT->DrawGlyphRun(lineOrigin, &drawGlyphRun, pBlackBrush);

	hr = pRT->EndDraw();

	if (SUCCEEDED(hr))
	{
		hr = pFormatConverter->CopyPixels(NULL, imageWidth * imageBitsPerPixel / 8, imageWidth * imageHeight * imageBitsPerPixel / 8, imageBuffer);
	}

	return hr;
}

void ReleaseAll()
{
	SafeRelease(&pBlackBrush);
	SafeRelease(&pRT);
	SafeRelease(&pD2DFactory);

	SafeRelease(&pDWriteFactory);

	SafeRelease(&pFormatConverter);
	SafeRelease(&pWICBitmap);
	SafeRelease(&pWICFactory);

	SafeRelease(&pFontFace);

	CoUninitialize();
}

template <class T> void SafeRelease(T **ppT)
{
	if (*ppT != NULL)
	{
		(*ppT)->Release();
		*ppT = NULL;
	}
}