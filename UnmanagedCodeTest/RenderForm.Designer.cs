namespace UnmanagedCodeTest
{
    partial class RenderForm
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
            this.RenderBox = new System.Windows.Forms.PictureBox();
            this.TextInput = new System.Windows.Forms.RichTextBox();
            this.FontStretchInput = new System.Windows.Forms.ComboBox();
            this.FontInput = new System.Windows.Forms.ComboBox();
            this.FontSizeInput = new System.Windows.Forms.NumericUpDown();
            this.FontStyleInput = new System.Windows.Forms.ComboBox();
            this.FontWeightInput = new System.Windows.Forms.ComboBox();
            this.DiagnosticsTextBox = new System.Windows.Forms.RichTextBox();
            this.DrawRectanglesInput = new System.Windows.Forms.CheckBox();
            ((System.ComponentModel.ISupportInitialize)(this.RenderBox)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.FontSizeInput)).BeginInit();
            this.SuspendLayout();
            // 
            // RenderBox
            // 
            this.RenderBox.Location = new System.Drawing.Point(294, 12);
            this.RenderBox.Name = "RenderBox";
            this.RenderBox.Size = new System.Drawing.Size(500, 500);
            this.RenderBox.TabIndex = 0;
            this.RenderBox.TabStop = false;
            // 
            // TextInput
            // 
            this.TextInput.Location = new System.Drawing.Point(13, 13);
            this.TextInput.Name = "TextInput";
            this.TextInput.Size = new System.Drawing.Size(275, 168);
            this.TextInput.TabIndex = 1;
            this.TextInput.Text = "";
            this.TextInput.TextChanged += new System.EventHandler(this.DrawString);
            // 
            // FontStretchInput
            // 
            this.FontStretchInput.FormattingEnabled = true;
            this.FontStretchInput.Location = new System.Drawing.Point(12, 240);
            this.FontStretchInput.Name = "FontStretchInput";
            this.FontStretchInput.Size = new System.Drawing.Size(275, 21);
            this.FontStretchInput.TabIndex = 2;
            this.FontStretchInput.SelectedIndexChanged += new System.EventHandler(this.DrawString);
            // 
            // FontInput
            // 
            this.FontInput.FormattingEnabled = true;
            this.FontInput.Location = new System.Drawing.Point(12, 213);
            this.FontInput.Name = "FontInput";
            this.FontInput.Size = new System.Drawing.Size(275, 21);
            this.FontInput.TabIndex = 3;
            this.FontInput.SelectedIndexChanged += new System.EventHandler(this.DrawString);
            // 
            // FontSizeInput
            // 
            this.FontSizeInput.Location = new System.Drawing.Point(12, 187);
            this.FontSizeInput.Name = "FontSizeInput";
            this.FontSizeInput.Size = new System.Drawing.Size(275, 20);
            this.FontSizeInput.TabIndex = 4;
            this.FontSizeInput.ValueChanged += new System.EventHandler(this.DrawString);
            // 
            // FontStyleInput
            // 
            this.FontStyleInput.FormattingEnabled = true;
            this.FontStyleInput.Location = new System.Drawing.Point(12, 267);
            this.FontStyleInput.Name = "FontStyleInput";
            this.FontStyleInput.Size = new System.Drawing.Size(275, 21);
            this.FontStyleInput.TabIndex = 2;
            this.FontStyleInput.SelectedIndexChanged += new System.EventHandler(this.DrawString);
            // 
            // FontWeightInput
            // 
            this.FontWeightInput.FormattingEnabled = true;
            this.FontWeightInput.Location = new System.Drawing.Point(12, 294);
            this.FontWeightInput.Name = "FontWeightInput";
            this.FontWeightInput.Size = new System.Drawing.Size(275, 21);
            this.FontWeightInput.TabIndex = 2;
            this.FontWeightInput.SelectedIndexChanged += new System.EventHandler(this.DrawString);
            // 
            // DiagnosticsTextBox
            // 
            this.DiagnosticsTextBox.Location = new System.Drawing.Point(13, 373);
            this.DiagnosticsTextBox.Name = "DiagnosticsTextBox";
            this.DiagnosticsTextBox.ReadOnly = true;
            this.DiagnosticsTextBox.Size = new System.Drawing.Size(274, 142);
            this.DiagnosticsTextBox.TabIndex = 5;
            this.DiagnosticsTextBox.Text = "";
            // 
            // DrawRectanglesInput
            // 
            this.DrawRectanglesInput.AutoSize = true;
            this.DrawRectanglesInput.Location = new System.Drawing.Point(12, 321);
            this.DrawRectanglesInput.Name = "DrawRectanglesInput";
            this.DrawRectanglesInput.Size = new System.Drawing.Size(108, 17);
            this.DrawRectanglesInput.TabIndex = 6;
            this.DrawRectanglesInput.Text = "Draw Rectangles";
            this.DrawRectanglesInput.UseVisualStyleBackColor = true;
            this.DrawRectanglesInput.CheckedChanged += new System.EventHandler(this.DrawString);
            // 
            // RenderForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(806, 527);
            this.Controls.Add(this.DrawRectanglesInput);
            this.Controls.Add(this.DiagnosticsTextBox);
            this.Controls.Add(this.FontSizeInput);
            this.Controls.Add(this.FontInput);
            this.Controls.Add(this.FontWeightInput);
            this.Controls.Add(this.FontStyleInput);
            this.Controls.Add(this.FontStretchInput);
            this.Controls.Add(this.TextInput);
            this.Controls.Add(this.RenderBox);
            this.Name = "RenderForm";
            this.Text = "RenderForm";
            ((System.ComponentModel.ISupportInitialize)(this.RenderBox)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.FontSizeInput)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.PictureBox RenderBox;
        private System.Windows.Forms.RichTextBox TextInput;
        private System.Windows.Forms.ComboBox FontStretchInput;
        private System.Windows.Forms.ComboBox FontInput;
        private System.Windows.Forms.NumericUpDown FontSizeInput;
        private System.Windows.Forms.ComboBox FontStyleInput;
        private System.Windows.Forms.ComboBox FontWeightInput;
        private System.Windows.Forms.RichTextBox DiagnosticsTextBox;
        private System.Windows.Forms.CheckBox DrawRectanglesInput;
    }
}