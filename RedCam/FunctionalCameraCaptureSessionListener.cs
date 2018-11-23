using Android.Hardware.Camera2;
using System;

namespace RedCam
{
    public class FunctionalCameraCaptureSessionListener : CameraCaptureSession.StateCallback
    {
        private readonly Action<CameraCaptureSession> _onConfigured;
        private readonly Action<CameraCaptureSession> _onConfigureFailed;

        public FunctionalCameraCaptureSessionListener(Action<CameraCaptureSession> onConfigured, Action<CameraCaptureSession> onConfigureFailed)
        {
            _onConfigured = onConfigured;
            _onConfigureFailed = onConfigureFailed;
        }

        public override void OnConfigured(CameraCaptureSession session) => _onConfigured(session);
        public override void OnConfigureFailed(CameraCaptureSession session) => _onConfigureFailed(session);
    }
}