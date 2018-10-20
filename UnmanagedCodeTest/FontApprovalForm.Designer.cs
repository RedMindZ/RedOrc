namespace UnmanagedCodeTest
{
    partial class FontApprovalForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.ApprovalPictureBox = new System.Windows.Forms.PictureBox();
            this.ApproveButton = new System.Windows.Forms.Button();
            this.DenyButton = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.ApprovalPictureBox)).BeginInit();
            this.SuspendLayout();
            // 
            // ApprovalPictureBox
            // 
            this.ApprovalPictureBox.Location = new System.Drawing.Point(12, 12);
            this.ApprovalPictureBox.Name = "ApprovalPictureBox";
            this.ApprovalPictureBox.Size = new System.Drawing.Size(500, 500);
            this.ApprovalPictureBox.TabIndex = 0;
            this.ApprovalPictureBox.TabStop = false;
            // 
            // ApproveButton
            // 
            this.ApproveButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ApproveButton.Location = new System.Drawing.Point(12, 518);
            this.ApproveButton.Name = "ApproveButton";
            this.ApproveButton.Size = new System.Drawing.Size(230, 48);
            this.ApproveButton.TabIndex = 1;
            this.ApproveButton.Text = "Approve";
            this.ApproveButton.UseVisualStyleBackColor = true;
            this.ApproveButton.Click += new System.EventHandler(this.ApproveButton_Click);
            // 
            // DenyButton
            // 
            this.DenyButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.DenyButton.Location = new System.Drawing.Point(282, 518);
            this.DenyButton.Name = "DenyButton";
            this.DenyButton.Size = new System.Drawing.Size(230, 48);
            this.DenyButton.TabIndex = 2;
            this.DenyButton.Text = "Deny";
            this.DenyButton.UseVisualStyleBackColor = true;
            this.DenyButton.Click += new System.EventHandler(this.DenyButton_Click);
            // 
            // FontApprovalForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(523, 574);
            this.Controls.Add(this.DenyButton);
            this.Controls.Add(this.ApproveButton);
            this.Controls.Add(this.ApprovalPictureBox);
            this.Name = "FontApprovalForm";
            this.Text = "FontApprovalForm";
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.FontApprovalForm_KeyDown);
            ((System.ComponentModel.ISupportInitialize)(this.ApprovalPictureBox)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox ApprovalPictureBox;
        private System.Windows.Forms.Button ApproveButton;
        private System.Windows.Forms.Button DenyButton;
    }
}