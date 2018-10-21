using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace UnmanagedCodeTest
{
    public partial class RenderForm : Form
    {
        private ImageProperties _imageProps;

        public int Status { get; private set; }

        public RenderForm()
        {
            InitializeComponent();

            FontSizeInput.Value = 56;

            string[] approvedFonts = File.ReadAllLines(@"D:\Programing Stuff\Mixed Projects\RedOrc\UnmanagedCodeTest\bin\Debug\ApprovedFonts.txt");
            for (int i = 0; i < approvedFonts.Length; i++)
            {
                FontInput.Items.Add(approvedFonts[i]);
            }

            foreach (string fontStretch in Enum.GetNames(typeof(DWRITE_FONT_STRETCH)))
            {
                FontStretchInput.Items.Add(fontStretch);
            }

            foreach (string fontStyle in Enum.GetNames(typeof(DWRITE_FONT_STYLE)))
            {
                FontStyleInput.Items.Add(fontStyle);
            }

            foreach (string fontWeight in Enum.GetNames(typeof(DWRITE_FONT_WEIGHT)))
            {
                FontWeightInput.Items.Add(fontWeight);
            }

            Status = TextRenderer.Initialize();

            if (Status < 0)
            {
                Close();
            }

            _imageProps = new ImageProperties
            {
                ImageHeight = 500,
                ImageWidth = 500,
                BitsPerPixel = 32,
                WICPixelFormat = GUID.WICPixelFormat32bppRGBA
            };

            Status = TextRenderer.SetImageProperties(ref _imageProps);

            if (Status < 0)
            {
                Close();
            }

            FontInput.SelectedIndex = 0;
            FontStretchInput.SelectedIndex = 0;
            FontStyleInput.SelectedIndex = 0;
            FontWeightInput.SelectedIndex = 0;
        }

        private void DrawString(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(TextInput.Text) || string.IsNullOrWhiteSpace(TextInput.Text))
            {
                return;
            }

            if (FontStretchInput.SelectedItem == null || FontStyleInput.SelectedItem == null || FontWeightInput.SelectedItem == null)
            {
                DiagnosticsTextBox.AppendText("You must select the font stretch, style, and weight\n");
                return;
            }

            TextProperties textProps = new TextProperties
            {
                FontBidiLevel = 0,
                FontEmSize = (float)FontSizeInput.Value,
                FontName = FontInput.SelectedItem.ToString(),
                FontStretch = (DWRITE_FONT_STRETCH)Enum.Parse(typeof(DWRITE_FONT_STRETCH), FontStretchInput.SelectedItem.ToString()),
                FontStyle = (DWRITE_FONT_STYLE)Enum.Parse(typeof(DWRITE_FONT_STYLE), FontStyleInput.SelectedItem.ToString()),
                FontWeight = (DWRITE_FONT_WEIGHT)Enum.Parse(typeof(DWRITE_FONT_WEIGHT), FontWeightInput.SelectedItem.ToString())
            };

            Status = TextRenderer.SetTextProperties(ref textProps, out bool fontExists);

            if (Status < 0)
            {
                DiagnosticsTextBox.AppendText($"SetTextProperties failed with status {Status}\n");
                return;
            }

            if (!fontExists)
            {
                DiagnosticsTextBox.AppendText($"The requested font ({textProps.FontName}) is not available\n");
                return;
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
                X = 0,
                Y = 100
            };

            Bitmap bmp = new Bitmap(_imageProps.ImageHeight, _imageProps.ImageWidth, PixelFormat.Format32bppArgb);
            BitmapData bmpData = bmp.LockBits(new Rectangle(0, 0, bmp.Height, bmp.Width), ImageLockMode.ReadWrite, bmp.PixelFormat);

            Stopwatch watch = new Stopwatch();

            watch.Start();
            Status = TextRenderer.RenderString(TextInput.Text, TextInput.Text.Length, ref baselineOrigin, ref boundingRect, true, DrawRectanglesInput.Checked, bmpData.Scan0, out IntPtr boundingBoxesPtr, out int boundingBoxesCount);
            watch.Stop();

            bmp.UnlockBits(bmpData);

            if (Status < 0)
            {
                DiagnosticsTextBox.AppendText($"RenderString2 failed with status {Status}\n");
                return;
            }

            DiagnosticsTextBox.Clear();
            DiagnosticsTextBox.AppendText(string.Format("Render time: {0:0.##}ms\n", watch.Elapsed.TotalMilliseconds));

            DiagnosticsTextBox.AppendText("Bounding boxes count: " + boundingBoxesCount + "\n");

            int boxPtrOffset = 0;
            for (int i = 0; i < boundingBoxesCount; i++)
            {
                D2D1_RECT_F box = Marshal.PtrToStructure<D2D1_RECT_F>(boundingBoxesPtr + boxPtrOffset);
                boxPtrOffset += Marshal.SizeOf<D2D1_RECT_F>();

                DiagnosticsTextBox.AppendText($"{{{box.Left}, {box.Top}, {box.Right}, {box.Bottom}}}\n");
            }

            TextRenderer.DeleteArray(boundingBoxesPtr);

            RenderBox.Image = bmp;
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            TextRenderer.Uninitialize();

            base.OnClosing(e);
        }
    }
}
