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
        public static extern int Initialize();

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetImageProperties(ref ImageProperties imageProps);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetTextProperties(ref TextProperties textProps, out bool fontExists);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int GetRenderedTextInformation([MarshalAs(UnmanagedType.LPWStr)] string charSet, ref D2D1_RECT_F pTextBounds, out RenderedTextInformation pTextInformation);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int RenderString([MarshalAs(UnmanagedType.LPWStr)] string str, int strLen, ref D2D1_RECT_F pTextBounds, bool clearBackground, bool drawBoundingBoxes, IntPtr pImageBuffer, out IntPtr ppOutBoundingBoxes, out int boundingBoxesCount);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void DeleteArray(IntPtr arr);

        [DllImport("TextRenderer.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void Uninitialize();
    }
}
