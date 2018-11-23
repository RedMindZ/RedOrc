using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

using Android.App;
using Android.Content;
using Android.OS;
using Android.Runtime;
using Android.Views;
using Android.Widget;
using Android.Media;

namespace RedCam
{
    public class VideoEncoder
    {
        public VideoEncoder(int width, int height)
        {
            MediaFormat videoFormat = MediaFormat.CreateVideoFormat(MediaFormat.MimetypeVideoAvc, width, height);
            MediaCodecList availableCodecs = new MediaCodecList(MediaCodecListKind.RegularCodecs);
            MediaCodec encoder = MediaCodec.CreateEncoderByType(MediaFormat.MimetypeVideoAvc);

            encoder.Configure(videoFormat, null, null, MediaCodecConfigFlags.Encode);
            encoder.Start();
        }
    }
}