namespace FourOfAKind
{
    partial class ConsoleForm
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
            this.consoleContents = new System.Windows.Forms.RichTextBox();
            this.SuspendLayout();
            // 
            // consoleContents
            // 
            this.consoleContents.BackColor = System.Drawing.Color.White;
            this.consoleContents.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.consoleContents.Dock = System.Windows.Forms.DockStyle.Fill;
            this.consoleContents.Font = new System.Drawing.Font("Consolas", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.consoleContents.ForeColor = System.Drawing.Color.Black;
            this.consoleContents.Location = new System.Drawing.Point(0, 0);
            this.consoleContents.Name = "consoleContents";
            this.consoleContents.ReadOnly = true;
            this.consoleContents.Size = new System.Drawing.Size(808, 347);
            this.consoleContents.TabIndex = 0;
            this.consoleContents.Text = "";
            // 
            // ConsoleForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.White;
            this.ClientSize = new System.Drawing.Size(808, 347);
            this.Controls.Add(this.consoleContents);
            this.Font = new System.Drawing.Font("Consolas", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.ForeColor = System.Drawing.Color.Black;
            this.Name = "ConsoleForm";
            this.Text = "Console";
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.RichTextBox consoleContents;
    }
}