using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace UnmanagedCodeTest
{
    [StructLayout(LayoutKind.Sequential)]
    public struct GUID
    {
        public uint Data1;
        public ushort Data2;
        public ushort Data3;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
        public byte[] Data4;

        public GUID(uint data1, ushort data2, ushort data3, byte data41, byte data42, byte data43, byte data44, byte data45, byte data46, byte data47, byte data48)
        {
            Data1 = data1;
            Data2 = data2;
            Data3 = data3;
            Data4 = new byte[8] { data41, data42, data43, data44, data45, data46, data47, data48 };
        }

        public static GUID WICPixelFormat32bppRGBA => new GUID(0xf5c7ad2d, 0x6a8d, 0x43dd, 0xa7, 0xa8, 0xa2, 0x99, 0x35, 0x26, 0x1a, 0xe9);
        public static GUID WICPixelFormat32bppRGB => new GUID(0xd98c6b95, 0x3efe, 0x47d6, 0xbb, 0x25, 0xeb, 0x17, 0x48, 0xab, 0x0c, 0xf1);
        public static GUID WICPixelFormat8bppGray => new GUID(0x6fddc324, 0x4e03, 0x4bfe, 0xb1, 0x85, 0x3d, 0x77, 0x76, 0x8d, 0xc9, 0x08);
    }
}
