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
using Java.Net;
using Java.Nio;

namespace RedCam
{
    public class VideoStreamer
    {
        private class EncoderCallback : MediaCodec.Callback
        {
            private DatagramSocket _udpSocket;

            public EncoderCallback()
            {
                _udpSocket = new DatagramSocket();
            }

            public override void OnError(MediaCodec codec, MediaCodec.CodecException e)
            {
                throw new NotImplementedException();
            }

            public override void OnInputBufferAvailable(MediaCodec codec, int index)
            {
                
            }

            public override void OnOutputBufferAvailable(MediaCodec codec, int index, MediaCodec.BufferInfo info)
            {
                ByteBuffer outputBuffer = codec.GetOutputBuffer(index);
                byte[] outputArray = new byte[outputBuffer.Remaining()];
                outputBuffer.Get(outputArray);

                DatagramPacket packet = new DatagramPacket(outputArray, outputArray.Length, InetAddress.GetByAddress(new byte[] { 192, 168, 0, 31}), 9482);
                _udpSocket.Send(packet);

                codec.ReleaseOutputBuffer(index, false);
            }

            public override void OnOutputFormatChanged(MediaCodec codec, MediaFormat format)
            {
                throw new NotImplementedException();
            }
        }

        private HandlerThread _backgroundThread;
        private Handler _backgroundHandler;

        public VideoStreamer(int width, int height)
        {
            MediaFormat videoFormat = MediaFormat.CreateVideoFormat(MediaFormat.MimetypeVideoAvc, width, height);
            MediaCodecList availableCodecs = new MediaCodecList(MediaCodecListKind.RegularCodecs);
            MediaCodec encoder = MediaCodec.CreateEncoderByType(MediaFormat.MimetypeVideoAvc);

            _backgroundThread = new HandlerThread("EncoderBackgroundWorker");
            _backgroundThread.Start();
            _backgroundHandler = new Handler(_backgroundThread.Looper);

            encoder.SetCallback(new EncoderCallback(), _backgroundHandler);
            encoder.Configure(videoFormat, null, null, MediaCodecConfigFlags.Encode);
            encoder.Start();
        }
    }
}