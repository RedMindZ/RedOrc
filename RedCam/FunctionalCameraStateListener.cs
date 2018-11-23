using Android.Hardware.Camera2;
using Android.Runtime;
using System;

namespace RedCam
{
    public class FunctionalCameraStateListener : CameraDevice.StateCallback
    {
        private readonly Action<CameraDevice> _onOpen;
        private readonly Action<CameraDevice> _onDisconnected;
        private readonly Action<CameraDevice, CameraError> _onError;

        public FunctionalCameraStateListener(Action<CameraDevice> onOpen, Action<CameraDevice> onDisconnected, Action<CameraDevice, CameraError> onError)
        {
            _onOpen = onOpen;
            _onDisconnected = onDisconnected;
            _onError = onError;
        }

        public override void OnOpened(CameraDevice camera) => _onOpen(camera);
        public override void OnDisconnected(CameraDevice camera) => _onDisconnected(camera);
        public override void OnError(CameraDevice camera, [GeneratedEnum] CameraError error) => _onError(camera, error);
    }
}