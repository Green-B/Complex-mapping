import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

fig_height = 4
width_ratios = [1,1,1]
fig_size = [fig_height*np.sum(np.array(width_ratios)), fig_height]
fig, [ax1, ax2, ax_blank] = plt.subplots(1, 3, width_ratios=width_ratios, figsize=fig_size)

plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)

class ComplexMapper:
    
    def __init__(self, fig):
        self.z_pts = []
        self.fx_str = "z**2"
        self.left_click_down = False
        self.press_cb = fig.canvas.mpl_connect('button_press_event', self.onPress)
        self.move_cb = fig.canvas.mpl_connect('motion_notify_event', self.onMove)
        self.release_cb = fig.canvas.mpl_connect('button_release_event', self.onRelease)
        self.updateDisplay()
        
    def updateDisplay(self):
        ax1.clear()
        ax2.clear()
        for z_curve in self.z_pts:
            ax1.plot(np.real(z_curve), np.imag(z_curve), color="#0000B0")
            # Evaluate in a function to limit the scope of a variable with a very general name like z
            def fx(): z = z_curve; return eval(self.fx_str)
            w_curve = fx()
            ax2.plot(np.real(w_curve), np.imag(w_curve), color="#B00000")
        ax1.plot([1,-1,0,0], [0,0,1,-1], color="white", linestyle="None", marker="None")
        ax2.plot([1,-1,0,0], [0,0,1,-1], color="white", linestyle="None", marker="None")
        ax1.set_ylim([-1,1])
        ax1.set_xlim([-1,1])
        ax1.axis("equal")
        ax2.set_ylim([-1,1])
        ax2.set_xlim([-1,1])
        ax2.axis("equal")
        plt.draw()
    
    def onPress(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.z_pts.append(np.array([event.xdata + 1j*event.ydata]))
            self.left_click_down = True
            self.updateDisplay()
    
    def onMove(self, event):
        if event.inaxes==ax1 and self.left_click_down==True:
            self.z_pts[-1] = np.append(self.z_pts[-1], event.xdata + 1j*event.ydata)
            self.updateDisplay()
    
    def onRelease(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.left_click_down = False
            self.updateDisplay()
    
    def fx_str_builder(self, str):
        if str=="Clear":
            self.fx_str = ""
        elif str=="Back":
            self.fx_str = self.fx_str[:-1]
        else:
            self.fx_str += str
        ax_fx_str.clear()
        ax_fx_str.text(0.5, 0.5, "f(z) = {}".format(self.fx_str), horizontalalignment="center", verticalalignment="center")
        ax_fx_str.set_xticks([])
        ax_fx_str.set_yticks([])
        plt.draw()
    

CM = ComplexMapper(fig)

(N_button_rows, N_button_cols) = (5, 5)
(left_edge, top_edge) = (0.7, 0.8)
[button_width, button_height] = [0.045, 0.1]
[button_width_margin, button_height_margin] = [button_width/4, button_height/4]
# Mapping function readout in the GUI; give it button height but the width of all buttons together
ax_fx_str = fig.add_axes((left_edge, top_edge, N_button_rows*button_width+(N_button_rows-1)*button_width_margin, button_height))
CM.fx_str_builder("")
# Update top_edge so buttons are below text box
top_edge -= button_height+button_height_margin
# Used in actual function
button_strings = ["Clear", "Back", "(", ")", "np.log(",
                  "7", "8", "9", "/", "np.exp(",
                  "4", "5", "6", "*", "np.pi",
                  "1", "2", "3", "-", "1j",
                  "z", "0", ".", "+", "**",]
# Used in GUI
button_labels = ["Clear", "Back", "(", ")", "ln",
                  "7", "8", "9", "/", "exp",
                  "4", "5", "6", "×", "π",
                  "1", "2", "3", "–", "$i$",
                  "z", "0", ".", "+", "^",]
button_axes = []
buttons = []
def make_button(row, col, str_index):
    button_horizontal_position = left_edge + col*(button_width+button_width_margin)
    button_vertical_position = top_edge - row*(button_height+button_height_margin)
    button_axes.append(fig.add_axes((button_horizontal_position, button_vertical_position, button_width, button_height)))
    buttons.append(Button(button_axes[-1], button_labels[str_index], color="0.75", hovercolor="0.875"))
    buttons[-1].on_clicked(func=lambda x: CM.fx_str_builder(button_strings[str_index]))
for row in range(N_button_rows):
    for col in range(N_button_cols):
        make_button(row, col, col+row*N_button_cols)

plt.show()
