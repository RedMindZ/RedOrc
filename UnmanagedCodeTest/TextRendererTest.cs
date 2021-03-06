﻿using System;
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
        

        [TestMethod]
        public void RenderTest()
        {
            try
            {
                int hres = TextRenderer.Initialize();
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

                hres = TextRenderer.SetImageProperties(ref imageProps);
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

                    hres = TextRenderer.SetTextProperties(ref textProps, out bool fontExists);
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

                    TextRenderer.GetRenderedTextInformation("abcedfghijklmnopqrstuvwxyz", ref boundingRect, out RenderedTextInformation textInformation);

                    Bitmap bmp = new Bitmap(imageProps.ImageHeight, imageProps.ImageWidth, PixelFormat.Format32bppArgb);
                    BitmapData bmpData = bmp.LockBits(new Rectangle(0, 0, bmp.Height, bmp.Width), ImageLockMode.ReadWrite, bmp.PixelFormat);

                    string text = "This is a very loooooooooooooong tessssssssssssst string";
                    hres = TextRenderer.RenderString(text, text.Length, ref boundingRect, true, true, bmpData.Scan0, out IntPtr boundingBoxesPtr, out int boundingBoxesCount);
                    if (hres < 0)
                    {
                        throw new Exception("RenderString function failed with code " + hres);
                    }

                    TextRenderer.DeleteArray(boundingBoxesPtr);
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
                TextRenderer.Uninitialize();
            }
        }

        [TestMethod]
        public void InteractiveTest()
        {
            RenderForm rf = new RenderForm();
            if (rf.Status < 0)
            {
                Assert.Fail("One of the functions with status code " + rf.Status);
            }
            else
            {
                rf.ShowDialog();
            }
        }
    }
}
