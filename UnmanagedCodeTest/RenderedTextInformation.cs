﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace UnmanagedCodeTest
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RenderedTextInformation
    {
        public int MaxGlyphsPerLine;
        public int MaxLines;
    }
}
