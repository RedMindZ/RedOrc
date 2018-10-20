using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace UnmanagedCodeTest
{
    [TestClass]
    public class TextRendererTest
    {
        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int Init();

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetImageProperties(ref ImageProperties imageProps);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetTextProperties(ref TextProperties textProps, out bool fontExists);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int RenderString([MarshalAs(UnmanagedType.LPWStr)] string str, int strLen, IntPtr imageBuffer, ref D2D1_RECT_F rect, bool clearBackground);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int RenderString2([MarshalAs(UnmanagedType.LPWStr)] string str, int strLen, ref D2D1_POINT_2F pBaselineOrigin, ref D2D1_RECT_F pTextBounds, bool clearBackground, bool drawBoundingBoxes, IntPtr pImageBuffer);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void ReleaseAll();

        [TestMethod]
        public void TestInit()
        {


            try
            {
                int hres = Init();
                if (hres < 0)
                {
                    throw new Exception("Init function failed with code " + hres);
                }

                ImageProperties imageProps = new ImageProperties
                {
                    ImageHeight = 500,
                    ImageWidth = 500,
                    BitsPerPixel = 32,
                    WICPixelFormat = GUID.WICPixelFormat32bppRGBA
                };

                hres = SetImageProperties(ref imageProps);
                if (hres < 0)
                {
                    throw new Exception("SetImageSize function failed with code " + hres);
                }

                string[] approvedFonts = File.ReadAllLines(@"D:\Programing Stuff\Mixed Projects\RedOrc\UnmanagedCodeTest\bin\Debug\ApprovedFonts.txt");
                FontFamily[] fonts = new FontFamily[approvedFonts.Length];
                for (int i = 0; i < fonts.Length; i++)
                {
                    fonts[i] = new FontFamily(approvedFonts[i]);
                }

                foreach (FontFamily font in fonts)
                {
                    TextProperties textProps = new TextProperties
                    {
                        FontBidiLevel = 0,
                        FontEmSize = 56,
                        FontName = font.Name,
                        FontStretch = DWRITE_FONT_STRETCH.DWRITE_FONT_STRETCH_NORMAL,
                        FontStyle = DWRITE_FONT_STYLE.DWRITE_FONT_STYLE_NORMAL,
                        FontWeight = DWRITE_FONT_WEIGHT.DWRITE_FONT_WEIGHT_NORMAL
                    };

                    hres = SetTextProperties(ref textProps, out bool fontExists);
                    if (hres < 0)
                    {
                        throw new Exception("SetTextProperties function failed with code " + hres);
                    }

                    if (!fontExists)
                    {
                        continue;
                    }

                    D2D1_RECT_F boundingRect = new D2D1_RECT_F
                    {
                        Left = 0,
                        Top = 0,
                        Right = 500,
                        Bottom = 500
                    };

                    D2D1_POINT_2F baselineOrigin = new D2D1_POINT_2F
                    {
                        X = 20,
                        Y = 100
                    };

                    Bitmap bmp = new Bitmap(imageProps.ImageHeight, imageProps.ImageWidth, PixelFormat.Format32bppArgb);
                    BitmapData bmpData = bmp.LockBits(new Rectangle(0, 0, bmp.Height, bmp.Width), ImageLockMode.ReadWrite, bmp.PixelFormat);

                    string text = "Looooooooooooooooooooooooooooooong";
                    //string text = "This is really cool";
                    //hres = RenderString(text, text.Length, bmpData.Scan0, ref boundingRect, true);
                    hres = RenderString2(text, text.Length, ref baselineOrigin, ref boundingRect, true, true, bmpData.Scan0);
                    if (hres < 0)
                    {
                        throw new Exception("RenderString function failed with code " + hres);
                    }

                    bmp.UnlockBits(bmpData);

                    //FontApprovalForm form = new FontApprovalForm(bmp, font.Name);
                    //form.ShowDialog();

                    //if (form.Approved)
                    //{
                    bmp.Save("Renders\\" + textProps.FontName + ".png");
                    //}
                }
            }
            catch (Exception e)
            {
                Assert.Fail(e.Message);
            }
            finally
            {
                ReleaseAll();
            }

        }
    }
}
