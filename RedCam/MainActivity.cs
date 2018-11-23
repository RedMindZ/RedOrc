using Android.App;
using Android.OS;
using Android.Support.V7.App;
using Android.Runtime;
using Android.Widget;
using Android.Hardware.Camera2;
using Android.Views;
using Android;
using Android.Support.V4.Content;
using Android.Support.V4.App;
using Android.Util;

namespace RedCam
{
    [Activity(Label = "@string/app_name", Theme = "@style/AppTheme", MainLauncher = true)]
    public class MainActivity : AppCompatActivity
    {
        private bool capturing = false;

        protected override void OnCreate(Bundle savedInstanceState)
        {
            base.OnCreate(savedInstanceState);
            // Set our view from the "main" layout resource
            SetContentView(Resource.Layout.activity_main);

            if ((int)Build.VERSION.SdkInt >= 23 && ContextCompat.CheckSelfPermission(this, Manifest.Permission.Camera) != Android.Content.PM.Permission.Granted)
            {
                ActivityCompat.RequestPermissions(this, new string[] { Manifest.Permission.Camera }, 0);
            }

            TextureView previewView = FindViewById<TextureView>(Resource.Id.CameraPreviewView);
            previewView.SurfaceTextureAvailable += (sender, e) => StartCapture(e.Width, e.Height);

            Button captureButton = FindViewById<Button>(Resource.Id.CaptureButton);
            captureButton.Click += (sender, e) => StartCapture(previewView.Width, previewView.Height);

            CameraHelper.Initialize((CameraManager)GetSystemService(CameraService));
        }

        protected override void OnResume()
        {
            base.OnResume();

            TextureView previewView = FindViewById<TextureView>(Resource.Id.CameraPreviewView);
            if (previewView.IsAvailable)
            {
                StartCapture(previewView.Width, previewView.Height);
            }
        }

        protected override void OnPause()
        {
            CameraHelper.StopCapture();
            capturing = false;

            base.OnPause();
        }

        private void StartCapture(int width, int height)
        {
            if (capturing)
            {
                return;
            }

            capturing = true;
            TextureView previewView = FindViewById<TextureView>(Resource.Id.CameraPreviewView);
            int status = CameraHelper.StartCapture(previewView.SurfaceTexture, new Size(width, height));

            if (status != 0)
            {
                Toast.MakeText(ApplicationContext, $"Error {status} while trying to start capture.", ToastLength.Long).Show();
                capturing = false;
            }
        }
    }
}