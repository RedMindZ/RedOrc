using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace UnmanagedCodeTest
{
    public partial class FontApprovalForm : Form
    {
        public bool Approved { get; private set; }

        public FontApprovalForm(Bitmap bmp, string fontName)
        {
            InitializeComponent();
            ApprovalPictureBox.Image = bmp;
            Text = fontName;
            KeyPreview = true;
        }

        private void ApproveButton_Click(object sender, EventArgs e)
        {
            Approved = true;
            Close();
        }

        private void DenyButton_Click(object sender, EventArgs e)
        {
            Approved = false;
            Close();
        }

        private void FontApprovalForm_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Y)
            {
                Approved = true;
                Close();
            }
            else if (e.KeyCode == Keys.N)
            {
                Approved = false;
                Close();
            }
        }
    }
}
