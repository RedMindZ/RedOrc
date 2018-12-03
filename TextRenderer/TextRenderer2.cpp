// TextRenderer.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "TextRenderer2.h"

struct TextRenderer2
{
	ID2D1Factory* pD2DFactory;
	ID2D1BitmapRenderTarget* pRT;
	ID2D1SolidColorBrush* pBlackBrush;
	ID2D1SolidColorBrush* pPurpleBrush;

	IDWriteFactory* pDWriteFactory;
	IDWriteFontFace* pFontFace;

	IWICImagingFactory* pWICFactory;
	IWICBitmap* pWICBitmap;
	IWICFormatConverter* pFormatConverter;

	ImageProperties2* pImageProperties;
	TextProperties2* pTextProperties;

	//UINT32 fontBidiLevel;
	//FLOAT fontEmSize;

};

// Forward declarations
template <class T> void SafeRelease2(T **ppT);
void ReleaseGlyphRunCollection2(DWRITE_GLYPH_RUN* glyphRunCollection, int collectionLength);









int Initialize2()
{
	return CoInitialize(NULL);
}

int CreateInstance(TextRenderer2** instance)
{
	*instance = new TextRenderer2();
	TextRenderer2* instanceRef = *instance;

	// Create the D2D factory
	HRESULT hr = D2D1CreateFactory(D2D1_FACTORY_TYPE_SINGLE_THREADED, &instanceRef->pD2DFactory);

	// Create the DWrite factory
	if (SUCCEEDED(hr))
	{
		hr = DWriteCreateFactory(DWRITE_FACTORY_TYPE_SHARED, __uuidof(IDWriteFactory), reinterpret_cast<IUnknown**>(&instanceRef->pDWriteFactory));
	}

	// Create WICFactory
	if (SUCCEEDED(hr))
	{
		hr = CoCreateInstance(CLSID_WICImagingFactory, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&instanceRef->pWICFactory));
	}

	if (SUCCEEDED(hr))
	{
		instanceRef->pImageProperties = new ImageProperties2();
		instanceRef->pTextProperties = new TextProperties2();
	}

	return hr;
}

int SetImageProperties2(TextRenderer2* instance, ImageProperties2* imageProps)
{
	*instance->pImageProperties = *imageProps;
	ImageProperties2* imagePropsRef = instance->pImageProperties;

	// Create an IWICBitmap
	SafeRelease2(&instance->pWICBitmap);
	HRESULT hr = instance->pWICFactory->CreateBitmap(imagePropsRef->imageWidth, imagePropsRef->imageHeight, GUID_WICPixelFormat32bppBGR, WICBitmapCacheOnDemand, &instance->pWICBitmap);

	// Create a WIC format converter
	if (SUCCEEDED(hr))
	{
		SafeRelease2(&instance->pFormatConverter);
		hr = instance->pWICFactory->CreateFormatConverter(&instance->pFormatConverter);
	}

	// Initialize the format converter
	if (SUCCEEDED(hr))
	{
		hr = instance->pFormatConverter->Initialize(instance->pWICBitmap, imageProps->WICPixelFormat, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	}

	// Create a Direct2D render target.
	if (SUCCEEDED(hr))
	{
		SafeRelease2(&instance->pRT);
		hr = instance->pD2DFactory->CreateWicBitmapRenderTarget(instance->pWICBitmap, D2D1::RenderTargetProperties(), (ID2D1RenderTarget **)&instance->pRT);
	}

	// Create a black brush.
	if (SUCCEEDED(hr))
	{
		SafeRelease2(&instance->pBlackBrush);
		hr = instance->pRT->CreateSolidColorBrush(D2D1::ColorF(D2D1::ColorF::Black), &instance->pBlackBrush);
	}

	// Create a purple brush.
	if (SUCCEEDED(hr))
	{
		SafeRelease2(&instance->pPurpleBrush);
		hr = instance->pRT->CreateSolidColorBrush(D2D1::ColorF(D2D1::ColorF::Purple), &instance->pPurpleBrush);
	}

	return hr;
}

int SetTextProperties2(TextRenderer2* instance, TextProperties2* textProps, BOOL* fontExists)
{
	*instance->pTextProperties = *textProps;
	TextProperties2* textPropsRef = instance->pTextProperties;

	// Get system fonts
	IDWriteFontCollection* pSystemFontCollection = NULL;
	HRESULT hr = instance->pDWriteFactory->GetSystemFontCollection(&pSystemFontCollection);

	// Find a matching font family
	UINT32 familyIndex;
	if (SUCCEEDED(hr))
	{
		hr = pSystemFontCollection->FindFamilyName(textPropsRef->fontName, &familyIndex, fontExists);
	}

	if (!*fontExists)
	{
		SafeRelease2(&pSystemFontCollection);
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
		hr = pFontFamily->GetFirstMatchingFont(textPropsRef->fontWeight, textPropsRef->fontStretch, textPropsRef->fontStyle, &pFont);
	}

	// Find the font face
	if (SUCCEEDED(hr))
	{
		SafeRelease2(&instance->pFontFace);
		hr = pFont->CreateFontFace(&instance->pFontFace);
	}

	SafeRelease2(&pFont);
	SafeRelease2(&pFontFamily);
	SafeRelease2(&pSystemFontCollection);

	return hr;
}

int GetRenderedTextInformation2(TextRenderer2* instance, wchar_t* charSet, D2D1_RECT_F* pTextBounds, RenderedTextInformation2* pTextInformation)
{
	int charsCount = (int)wcslen(charSet);
	std::vector<UINT32> vCodePoints(charsCount);
	std::vector<UINT16> vGlyphIndices(charsCount);
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMetrics(charsCount);

	for (int i = 0; i < charsCount; i++)
	{
		vCodePoints[i] = charSet[i];
	}

	HRESULT hr = instance->pFontFace->GetGlyphIndicesW(vCodePoints.data(), charsCount, vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	hr = instance->pFontFace->GetDesignGlyphMetrics(vGlyphIndices.data(), charsCount, vGlyphMetrics.data());
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
	instance->pFontFace->GetMetrics(&fontMetric);

	pTextInformation->maxGlyphsPerLine = (int)abs(((pTextBounds->right - pTextBounds->left) / (maxWidth * instance->pTextProperties->fontEmSize / fontMetric.designUnitsPerEm)));
	pTextInformation->maxLines = (int)abs((pTextBounds->bottom - pTextBounds->top) / ((fontMetric.ascent + fontMetric.descent + fontMetric.lineGap) * (instance->pTextProperties->fontEmSize / fontMetric.designUnitsPerEm)));

	return hr;
}

void GetVisibleGlyphsCount2(wchar_t* str, int strLen, int* glyphCount)
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
HRESULT AnalyzeString2
(
	TextRenderer2* instance,
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
	GetVisibleGlyphsCount2(str, strLen, pTotalGlyphCount);

	// Translate the string to a list of UINT32
	std::vector<UINT32> vCodePoints(strLen);
	for (int i = 0; i < strLen; i++)
	{
		vCodePoints[i] = str[i];
	}

	// Get the glyph indices for the string
	std::vector<UINT16> vGlyphIndices(strLen);
	HRESULT hr = instance->pFontFace->GetGlyphIndicesW(vCodePoints.data(), (int)vCodePoints.size(), vGlyphIndices.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}

	// Get the metrics for the glyphs
	std::vector<DWRITE_GLYPH_METRICS> vGlyphMetrics(strLen);
	hr = instance->pFontFace->GetDesignGlyphMetrics(vGlyphIndices.data(), (int)vGlyphIndices.size(), vGlyphMetrics.data());
	if (!(SUCCEEDED(hr)))
	{
		return hr;
	}


	DWRITE_FONT_METRICS fontMetrics;
	instance->pFontFace->GetMetrics(&fontMetrics);

	float fontScale = instance->pTextProperties->fontEmSize / fontMetrics.designUnitsPerEm;
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
			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = instance->pTextProperties->fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = instance->pTextProperties->fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = instance->pFontFace;
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

			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = instance->pTextProperties->fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = instance->pTextProperties->fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = instance->pFontFace;
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
			(*ppGlyphRuns)[glyphRunIndex].bidiLevel = instance->pTextProperties->fontBidiLevel;
			(*ppGlyphRuns)[glyphRunIndex].fontEmSize = instance->pTextProperties->fontEmSize;
			(*ppGlyphRuns)[glyphRunIndex].fontFace = instance->pFontFace;
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

int RenderString2
(
	TextRenderer2* instance,
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

	HRESULT hr = AnalyzeString2(instance, str, strLen, pTextBounds, &pGlyphBoundingBoxes, &pGlyphRunsOrigins, &pGlyphRuns, &glyphRunsCount, &totalGlyphCount);
	if (!(SUCCEEDED(hr))) { return hr; }

	instance->pRT->BeginDraw();

	if (clearBackground)
	{
		instance->pRT->Clear(D2D1::ColorF(D2D1::ColorF::White));
	}

	for (int i = 0; i < glyphRunsCount; i++)
	{
		instance->pRT->DrawGlyphRun(pGlyphRunsOrigins[i], &(pGlyphRuns[i]), instance->pBlackBrush);
	}

	if (drawBoundingBoxes)
	{
		for (int i = 0; i < totalGlyphCount; i++)
		{
			instance->pRT->DrawRectangle(pGlyphBoundingBoxes + i, instance->pPurpleBrush);
		}
	}

	hr = instance->pRT->EndDraw();
	if (!(SUCCEEDED(hr)))
	{
		delete[] pGlyphBoundingBoxes;
		return hr;
	}

	hr = instance->pFormatConverter->CopyPixels
	(
		NULL,
		instance->pImageProperties->imageWidth * instance->pImageProperties->bitsPerPixel / 8,
		instance->pImageProperties->imageWidth * instance->pImageProperties->imageHeight * instance->pImageProperties->bitsPerPixel / 8,
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
	ReleaseGlyphRunCollection2(pGlyphRuns, glyphRunsCount);

	return hr;
}

int RenderRectangles2(TextRenderer2* instance, D2D1_RECT_F* pRectangles, int rectanglesCount, BYTE* pImageBuffer)
{
	IWICBitmap* pInputBitmap = NULL;
	IWICFormatConverter* pD2D1FormatConverter = NULL;
	ID2D1Bitmap* pD2D1Bitmap = NULL;

	HRESULT hr = instance->pWICFactory->CreateBitmapFromMemory
	(
		instance->pImageProperties->imageWidth,
		instance->pImageProperties->imageHeight,
		instance->pImageProperties->WICPixelFormat,
		instance->pImageProperties->imageWidth * instance->pImageProperties->bitsPerPixel / 8,
		instance->pImageProperties->imageWidth * instance->pImageProperties->imageHeight * instance->pImageProperties->bitsPerPixel / 8,
		pImageBuffer,
		&pInputBitmap
	);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = instance->pWICFactory->CreateFormatConverter(&pD2D1FormatConverter);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pD2D1FormatConverter->Initialize(pInputBitmap, GUID_WICPixelFormat32bppBGR, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = instance->pRT->CreateBitmapFromWicBitmap(pD2D1FormatConverter, &pD2D1Bitmap);
	if (!(SUCCEEDED(hr))) { goto cleanup; }


	instance->pRT->BeginDraw();

	instance->pRT->DrawBitmap(pD2D1Bitmap);

	for (int i = 0; i < rectanglesCount; i++)
	{
		instance->pRT->DrawRectangle(pRectangles + i, instance->pPurpleBrush);
	}

	hr = instance->pRT->EndDraw();
	if (!(SUCCEEDED(hr))) { goto cleanup; }


	hr = instance->pFormatConverter->CopyPixels
	(
		NULL,
		instance->pImageProperties->imageWidth * instance->pImageProperties->bitsPerPixel / 8,
		instance->pImageProperties->imageWidth * instance->pImageProperties->imageHeight * instance->pImageProperties->bitsPerPixel / 8,
		pImageBuffer
	);

cleanup:
	SafeRelease2(&pD2D1Bitmap);
	SafeRelease2(&pD2D1FormatConverter);
	SafeRelease2(&pInputBitmap);

	return hr;
}

int SaveImageAsPng2(TextRenderer2* instance, wchar_t* imageFilename, BYTE* pImageBuffer)
{
	IWICBitmap* pInputBitmap = NULL;
	IWICFormatConverter* pFileFormatConverter = NULL;
	IWICStream* pStream = NULL;
	IWICBitmapEncoder* pEncoder = NULL;
	IWICBitmapFrameEncode* pFrameEncode = NULL;

	HRESULT hr = instance->pWICFactory->CreateBitmapFromMemory
	(
		instance->pImageProperties->imageWidth,
		instance->pImageProperties->imageHeight,
		instance->pImageProperties->WICPixelFormat,
		instance->pImageProperties->imageWidth * instance->pImageProperties->bitsPerPixel / 8,
		instance->pImageProperties->imageWidth * instance->pImageProperties->imageHeight * instance->pImageProperties->bitsPerPixel / 8,
		pImageBuffer,
		&pInputBitmap
	);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = instance->pWICFactory->CreateFormatConverter(&pFileFormatConverter);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pFileFormatConverter->Initialize(pInputBitmap, GUID_WICPixelFormat32bppRGBA, WICBitmapDitherTypeNone, NULL, 0.0F, WICBitmapPaletteTypeCustom);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = instance->pWICFactory->CreateStream(&pStream);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = pStream->InitializeFromFilename(imageFilename, GENERIC_WRITE);
	if (!(SUCCEEDED(hr))) { goto cleanup; }

	hr = instance->pWICFactory->CreateEncoder(GUID_ContainerFormatPng, NULL, &pEncoder);
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
	SafeRelease2(&pFrameEncode);
	SafeRelease2(&pEncoder);
	SafeRelease2(&pStream);
	SafeRelease2(&pFileFormatConverter);
	SafeRelease2(&pInputBitmap);

	return hr;
}

void DestroyInstance(TextRenderer2* instance)
{
	delete instance->pImageProperties;
	delete instance->pTextProperties;

	SafeRelease2(&instance->pPurpleBrush);
	SafeRelease2(&instance->pBlackBrush);
	SafeRelease2(&instance->pRT);
	SafeRelease2(&instance->pD2DFactory);

	SafeRelease2(&instance->pFormatConverter);
	SafeRelease2(&instance->pWICBitmap);
	SafeRelease2(&instance->pWICFactory);

	SafeRelease2(&instance->pFontFace);
	SafeRelease2(&instance->pDWriteFactory);
}

void Uninitialize2()
{
	CoUninitialize();
}

void ReleaseGlyphRunCollection2(DWRITE_GLYPH_RUN* glyphRunCollection, int collectionLength)
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

void DeleteArray2(void* arr)
{
	delete[] arr;
}

template <class T> void SafeRelease2(T **ppT)
{
	if (*ppT != NULL)
	{
		(*ppT)->Release();
		*ppT = NULL;
	}
}