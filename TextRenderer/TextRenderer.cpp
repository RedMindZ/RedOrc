// TextRenderer.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "TextRenderer.h"


// Forward declarations
template <class T> void SafeRelease(T **ppT);
void ReleaseGlyphRunCollection(DWRITE_GLYPH_RUN* glyphRunCollection, int collectionLength);




ID2D1Factory* pD2DFactory = NULL;
ID2D1BitmapRenderTarget* pRT = NULL;
ID2D1SolidColorBrush* pBlackBrush = NULL;
ID2D1SolidColorBrush* pPurpleBrush = NULL;

IDWriteFactory* pDWriteFactory = NULL;
IDWriteFontFace* pFontFace = NULL;

IWICImagingFactory* pWICFactory = NULL;
IWICBitmap* pWICBitmap = NULL;
IWICFormatConverter* pFormatConverter = NULL;

ImageProperties imageProperties = { 0 };

UINT32 fontBidiLevel = 0;
FLOAT fontEmSize = 0;






// Image buffer must have at least height * width bytes available
int Initialize()
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
	//imageHeight = imageProps->imageHeight;
	//imageWidth = imageProps->imageWidth;
	//imageBitsPerPixel = imageProps->bitsPerPixel;
	imageProperties = *imageProps;

	// Create an IWICBitmap
	SafeRelease(&pWICBitmap);
	HRESULT hr = pWICFactory->CreateBitmap(imageProperties.imageWidth, imageProperties.imageHeight, GUID_WICPixelFormat32bppBGR, WICBitmapCacheOnDemand, &pWICBitmap);

	// Create a WIC format converter
	if (SUCCEEDED(hr))
	{
		SafeRelease(&pFormatConverter);
		hr = pWICFactory->CreateFormatConverter(&pFormatConverter);
	}

	// Initialize the format converter
	if (SUCCEEDED(hr))
	{
		hr = pFormatConverter->Initialize(pWICBitmap, imageProps->WICPixelFormat, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
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

int GetRenderedTextInformation(wchar_t* charSet, D2D1_RECT_F* pTextBounds, RenderedTextInformation* pTextInformation)
{
	int charsCount = (int)wcslen(charSet);
	std::vector<UINT32> vCodePoints(charsCount);
	std::vector<UINT16> vGlyphIndices(charsCount);
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMetrics(charsCount);

	for (int i = 0; i < charsCount; i++)
	{
		vCodePoints[i] = charSet[i];
	}

	HRESULT hr = pFontFace->GetGlyphIndicesW(vCodePoints.data(), charsCount, vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	hr = pFontFace->GetDesignGlyphMetrics(vGlyphIndices.data(), charsCount, vGlyphMetrics.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	int maxWidth = 0;
	for (int i = 0; i < charsCount; i++)
	{
		int currentWidth = vGlyphMetrics[i].advanceWidth;
		if (currentWidth > maxWidth)
		{
			maxWidth = currentWidth;
		}
	}

	DWRITE_FONT_METRICS fontMetric;
	pFontFace->GetMetrics(&fontMetric);

	pTextInformation->maxGlyphsPerLine = (int)abs(((pTextBounds->right - pTextBounds->left) / (maxWidth * fontEmSize / fontMetric.designUnitsPerEm)));
	pTextInformation->maxLines = (int)abs((pTextBounds->bottom - pTextBounds->top) / ((fontMetric.ascent + fontMetric.descent + fontMetric.lineGap) * (fontEmSize / fontMetric.designUnitsPerEm)));

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
	HRESULT hr = pFontFace->GetGlyphIndicesW(vCodePoints.data(), (int)vCodePoints.size(), vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	// Get the metrics for the glyphs
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMetrics(strLen);
	hr = pFontFace->GetDesignGlyphMetrics(vGlyphIndices.data(), (int)vGlyphIndices.size(), vGlyphMetrics.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}


	DWRITE_FONT_METRICS fontMetrics;
	pFontFace->GetMetrics(&fontMetrics);

	float fontScale = fontEmSize / fontMetrics.designUnitsPerEm;
	float textBoundsWidth = pTextBounds->right - pTextBounds->left;
	float currentGlyphRunWidth = 0;
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
		else
		{
			currentGlyphCount = 0;
			currentGlyphRunWidth = 0;
		}

		if (currentGlyphRunWidth > textBoundsWidth && currentGlyphCount > 1)
		{
			(*pGlyphRunsCount)++;

			currentGlyphCount = 1;
			currentGlyphRunWidth = vGlyphMetrics[i].advanceWidth * fontScale;
		}
	}

	*ppGlyphRunsOrigins = new D2D1_POINT_2F[*pGlyphRunsCount];
	D2D1_POINT_2F currentOrigin = D2D1_POINT_2F{ pTextBounds->left, pTextBounds->top + fontMetrics.ascent * fontScale };

	int originIndex = 0;
	currentGlyphRunWidth = 0;
	currentGlyphCount = 0;

	float lineGap = (fontMetrics.ascent + fontMetrics.descent + fontMetrics.lineGap) * fontScale;

	// Compute the origin of each glyph run:

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
			else
			{
				currentOrigin.x += vGlyphMetrics[i].advanceWidth * fontScale;
			}

			if (currentOrigin.x > pTextBounds->right)
			{
				currentOrigin.x = pTextBounds->left;
				currentOrigin.y += lineGap;
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

			int topOffset = ((fontMetrics.ascent + fontMetrics.descent) - vGlyphMetrics[i].advanceHeight);

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
			if (currentGlyphCount > 0)
			{
				originIndex++;
			}

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

	return hr;
}

int RenderString
(
	wchar_t* str,
	int strLen,
	D2D1_RECT_F* pTextBounds,
	BOOL clearBackground,
	BOOL drawBoundingBoxes,
	BYTE* pImageBuffer,
	D2D1_RECT_F** ppOutBoundingBoxes,
	int* boundingBoxesCount
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

	D2D1_RECT_F* pGlyphBoundingBoxes = NULL;
	D2D1_POINT_2F* pGlyphRunsOrigins = NULL;
	DWRITE_GLYPH_RUN* pGlyphRuns = NULL;
	int glyphRunsCount;
	int totalGlyphCount;

	HRESULT hr = AnalyzeString(str, strLen, pTextBounds, &pGlyphBoundingBoxes, &pGlyphRunsOrigins, &pGlyphRuns, &glyphRunsCount, &totalGlyphCount);
	if (!(SUCCEEDED(hr))) { return hr; }

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
			pRT->DrawRectangle(pGlyphBoundingBoxes + i, pPurpleBrush);
		}
	}

	hr = pRT->EndDraw();
	if (!(SUCCEEDED(hr)))
	{
		delete[] pGlyphBoundingBoxes;
		return hr;
	}

	hr = pFormatConverter->CopyPixels
	(
		NULL,
		imageProperties.imageWidth * imageProperties.bitsPerPixel / 8,
		imageProperties.imageWidth * imageProperties.imageHeight * imageProperties.bitsPerPixel / 8,
		pImageBuffer
	);

	if (!(SUCCEEDED(hr)))
	{
		delete[] pGlyphBoundingBoxes;
		return hr;
	}

	*ppOutBoundingBoxes = pGlyphBoundingBoxes;
	*boundingBoxesCount = totalGlyphCount;

	delete[] pGlyphRunsOrigins;
	ReleaseGlyphRunCollection(pGlyphRuns, glyphRunsCount);

	return hr;
}

int RenderRectangles(D2D1_RECT_F* pRectangles, int rectanglesCount, BYTE* pImageBuffer)
{
	IWICBitmap* pInputBitmap = NULL;
	IWICFormatConverter* pD2D1FormatConverter = NULL;
	ID2D1Bitmap* pD2D1Bitmap = NULL;

	HRESULT hr = pWICFactory->CreateBitmapFromMemory
	(
		imageProperties.imageWidth,
		imageProperties.imageHeight,
		imageProperties.WICPixelFormat,
		imageProperties.imageWidth * imageProperties.bitsPerPixel / 8,
		imageProperties.imageWidth * imageProperties.imageHeight * imageProperties.bitsPerPixel / 8,
		pImageBuffer,
		&pInputBitmap
	);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pWICFactory->CreateFormatConverter(&pD2D1FormatConverter);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pD2D1FormatConverter->Initialize(pInputBitmap, GUID_WICPixelFormat32bppBGR, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pRT->CreateBitmapFromWicBitmap(pD2D1FormatConverter, &pD2D1Bitmap);
	if (!(SUCCEEDED(hr))) { goto cleanup; }


	pRT->BeginDraw();

	pRT->DrawBitmap(pD2D1Bitmap);

	for (int i = 0; i < rectanglesCount; i++)
	{
		pRT->DrawRectangle(pRectangles + i, pPurpleBrush);
	}

	hr = pRT->EndDraw();
	if (!(SUCCEEDED(hr))) { goto cleanup; }


	hr = pFormatConverter->CopyPixels
	(
		NULL,
		imageProperties.imageWidth * imageProperties.bitsPerPixel / 8,
		imageProperties.imageWidth * imageProperties.imageHeight * imageProperties.bitsPerPixel / 8,
		pImageBuffer
	);

cleanup:
	SafeRelease(&pD2D1Bitmap);
	SafeRelease(&pD2D1FormatConverter);
	SafeRelease(&pInputBitmap);

	return hr;
}

int SaveImageAsPng(wchar_t* imageFilename, BYTE* pImageBuffer)
{
	IWICBitmap* pInputBitmap = NULL;
	IWICFormatConverter* pFileFormatConverter = NULL;
	IWICStream* pStream = NULL;
	IWICBitmapEncoder* pEncoder = NULL;
	IWICBitmapFrameEncode* pFrameEncode = NULL;

	HRESULT hr = pWICFactory->CreateBitmapFromMemory
	(
		imageProperties.imageWidth,
		imageProperties.imageHeight,
		imageProperties.WICPixelFormat,
		imageProperties.imageWidth * imageProperties.bitsPerPixel / 8,
		imageProperties.imageWidth * imageProperties.imageHeight * imageProperties.bitsPerPixel / 8,
		pImageBuffer,
		&pInputBitmap
	);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pWICFactory->CreateFormatConverter(&pFileFormatConverter);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pFileFormatConverter->Initialize(pInputBitmap, GUID_WICPixelFormat32bppRGBA, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pWICFactory->CreateStream(&pStream);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pStream->InitializeFromFilename(imageFilename, GENERIC_WRITE);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pWICFactory->CreateEncoder(GUID_ContainerFormatPng, NULL, &pEncoder);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pEncoder->Initialize(pStream, WICBitmapEncoderNoCache);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pEncoder->CreateNewFrame(&pFrameEncode, NULL);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pFrameEncode->Initialize(NULL);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pFrameEncode->WriteSource(pFileFormatConverter, NULL);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pFrameEncode->Commit();
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pEncoder->Commit();
	if (!(SUCCEEDED(hr))) { goto cleanup; }

cleanup:
	SafeRelease(&pFrameEncode);
	SafeRelease(&pEncoder);
	SafeRelease(&pStream);
	SafeRelease(&pFileFormatConverter);
	SafeRelease(&pInputBitmap);

	return hr;
}

void DeleteArray(void* arr)
{
	delete[] arr;
}

void ReleaseGlyphRunCollection(DWRITE_GLYPH_RUN* glyphRunCollection, int collectionLength)
{
	for (int i = 0; i < collectionLength; i++)
	{
		if (glyphRunCollection[i].glyphIndices != NULL)
		{
			delete[](glyphRunCollection[i].glyphIndices);
		}

		if (glyphRunCollection[i].glyphAdvances != NULL)
		{
			delete[](glyphRunCollection[i].glyphAdvances);
		}

		if (glyphRunCollection[i].glyphOffsets != NULL)
		{
			delete[](glyphRunCollection[i].glyphOffsets);
		}
	}

	delete[] glyphRunCollection;
}

void Uninitialize()
{
	SafeRelease(&pPurpleBrush);
	SafeRelease(&pBlackBrush);
	SafeRelease(&pRT);
	SafeRelease(&pD2DFactory);

	SafeRelease(&pFormatConverter);
	SafeRelease(&pWICBitmap);
	SafeRelease(&pWICFactory);

	SafeRelease(&pFontFace);
	SafeRelease(&pDWriteFactory);

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