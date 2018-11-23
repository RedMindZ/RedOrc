using System;
using System.Collections.Generic;
using System.Threading;
using Android.Graphics;
using Android.Hardware.Camera2;
using Android.Hardware.Camera2.Params;
using Android.OS;
using Android.Util;
using Android.Views;

namespace RedCam
{
    public static class CameraHelper
    {
        private static CameraManager _cameraManager;
        private static CameraDevice _camera;
        private static CameraCaptureSession _captureSession;

        private static HandlerThread _backgroundThread;
        private static Handler _backgroundHandler;

        public static void Initialize(CameraManager cameraManager)
        {
            _cameraManager = cameraManager;
        }

        public static int StartCapture(SurfaceTexture previewSurfaceTexture, Size previewSize)
        {
            // Find the optimal camera and size

            string optimalCamId = null;

            string[] availableCameras = _cameraManager.GetCameraIdList();
            for (int i = 0; i < availableCameras.Length; i++)
            {
                CameraCharacteristics characteristics = _cameraManager.GetCameraCharacteristics(availableCameras[i]);
                var camFace = (Java.Lang.Integer)characteristics.Get(CameraCharacteristics.LensFacing);
                if (camFace != null && camFace.IntValue() == (int)LensFacing.Back)
                {
                    optimalCamId = availableCameras[i];

                    StreamConfigurationMap streamConfig = (StreamConfigurationMap)characteristics.Get(CameraCharacteristics.ScalerStreamConfigurationMap);
                    List<Size> availableSizes = new List<Size>(streamConfig.GetOutputSizes(Java.Lang.Class.FromType(typeof(SurfaceTexture))));
                    if (availableSizes.Exists(s => s.Width == previewSize.Width && s.Height == previewSize.Height))
                    {
                        previewSurfaceTexture.SetDefaultBufferSize(previewSize.Width, previewSize.Height);
                        break;
                    }

                    availableSizes.Sort((s1, s2) => s1.Width * s1.Height - s2.Width * s2.Height);
                    Size maxSize = availableSizes[availableSizes.Count - 1];
                    availableSizes.RemoveAll(s => (s.Height != s.Width * maxSize.Height / maxSize.Width) );
                    availableSizes.Add(previewSize);
                    availableSizes.Sort((s1, s2) => s1.Width * s1.Height - s2.Width * s2.Height);

                    int previewSizeIndex = availableSizes.IndexOf(previewSize);

                    if (previewSizeIndex < availableSizes.Count - 1)
                    {
                        previewSurfaceTexture.SetDefaultBufferSize(availableSizes[previewSizeIndex + 1].Width, availableSizes[previewSizeIndex + 1].Height);
                    }
                    else
                    {
                        previewSurfaceTexture.SetDefaultBufferSize(availableSizes[previewSizeIndex - 1].Width, availableSizes[previewSizeIndex - 1].Height);
                    }

                    break;
                }
            }

            if (optimalCamId == null)
            {
                return 1;
            }


            // Open the camera

            // We use the semaphore to wait for the 'onOpen' function to be called, so that we can aquire the camera device.
            Semaphore utilSemaphore = new Semaphore(0, 1);

            void onOpen(CameraDevice camera)
            {
                _camera = camera;
                utilSemaphore.Release();
            }

            void onDisconnected(CameraDevice camera)
            {
                camera.Close();
                _camera = null;
            }

            void onError(CameraDevice camera, CameraError error)
            {
                onDisconnected(camera);
            }

            _backgroundThread = new HandlerThread("CameraBackgroundWorker");
            _backgroundThread.Start();
            _backgroundHandler = new Handler(_backgroundThread.Looper);


            _cameraManager.OpenCamera(optimalCamId, new FunctionalCameraStateListener(onOpen, onDisconnected, onError), _backgroundHandler);
            utilSemaphore.WaitOne();

            if (_camera == null)
            {
                return 2;
            }



            // Start the capture session

            bool configureFailed = false;
            Surface previewSurface = new Surface(previewSurfaceTexture);

            void onConfigured(CameraCaptureSession session)
            {
                _captureSession = session;

                var captureRequestBuilder = _camera.CreateCaptureRequest(CameraTemplate.Preview);
                captureRequestBuilder.AddTarget(previewSurface);
                captureRequestBuilder.Set(CaptureRequest.ControlAfMode, (int)ControlAFMode.ContinuousVideo);

                var captureRequest = captureRequestBuilder.Build();
                _captureSession.SetRepeatingRequest(captureRequest, null, _backgroundHandler);

                utilSemaphore.Release();
            }

            void onConfigureFailed(CameraCaptureSession session)
            {
                configureFailed = true;
                session.Close();
                utilSemaphore.Release();
            }

            _camera.CreateCaptureSession(new Surface[] { previewSurface }, new FunctionalCameraCaptureSessionListener(onConfigured, onConfigureFailed), _backgroundHandler);

            utilSemaphore.WaitOne();
            if (configureFailed)
            {
                onDisconnected(_camera);
                return 3;
            }

            return 0;
        }



        public static void StopCapture()
        {
            if (_camera != null)
            {
                _camera.Close();
                _camera = null;
            }

            if (_captureSession != null)
            {
                _captureSession.Close();
                _captureSession = null;
            }

            if (_backgroundThread != null)
            {
                _backgroundThread.QuitSafely();
                _backgroundThread.Join();
                _backgroundThread = null;
                _backgroundHandler = null;
            }
        }
    }
}