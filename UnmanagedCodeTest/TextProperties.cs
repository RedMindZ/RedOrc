using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace UnmanagedCodeTest
{
    [StructLayout(LayoutKind.Sequential)]
    public struct TextProperties
    {
        [MarshalAs(UnmanagedType.LPWStr)]
        public string FontName;

        public DWRITE_FONT_WEIGHT FontWeight;
        public DWRITE_FONT_STRETCH FontStretch;
        public DWRITE_FONT_STYLE FontStyle;
        public int FontBidiLevel;
        public float FontEmSize;
    }
}
