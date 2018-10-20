using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace UnmanagedCodeTest
{
    public static class TextRenderer
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
    }
}
