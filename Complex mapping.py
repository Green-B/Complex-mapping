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
        self.fx_str = ["z", "**", "2"]
        self.left_click_down = False
        self.press_cb = fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.move_cb = fig.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.release_cb = fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.update_plot_display()
        
    def update_plot_display(self):
        ax1.clear()
        ax2.clear()
        try:
            for z_curve in self.z_pts:
                ax1.plot(np.real(z_curve), np.imag(z_curve), color="#0000B0")
                # Evaluate in a function to limit the scope of a variable with a very general name like z
                def fx(): z = z_curve; return eval("".join(self.fx_str))
                w_curve = fx()
                ax2.plot(np.real(w_curve), np.imag(w_curve), color="#B00000")
            # set_xlim doesn't seem to work... plotting ghost data is a workaround to set the axis limits.
            for ax in [ax1, ax2]:
                ax.plot([1,-1,0,0], [0,0,1,-1], color="white", linestyle="None", marker="None")
                ax.axis("equal")
                ax.spines[["left", "bottom"]].set_position("zero")
                ax.spines[["right", "top"]].set_visible(False)
            plt.draw()
        except Exception:
            print("\nInvalid function syntax - check your complex map entry and try again.")
    
    def on_press(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.z_pts.append(np.array([event.xdata + 1j*event.ydata]))
            self.left_click_down = True
            self.update_plot_display()
    
    def on_move(self, event):
        if event.inaxes==ax1 and self.left_click_down==True:
            self.z_pts[-1] = np.append(self.z_pts[-1], event.xdata + 1j*event.ydata)
            self.update_plot_display()
    
    def on_release(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.left_click_down = False
            self.update_plot_display()
    
    def fx_str_builder(self, str):
        if str=="Clear":
            self.fx_str = []
        elif str=="Back":
            self.fx_str.pop()
        else:
            self.fx_str.append(str)
        self.update_fx_str_display()
    
    def update_fx_str_display(self):
        ax_fx_str.clear()
        # Use Greek pi, use i not 1j, and hide the "np." packages in the displayed text
        fx_str_display = "f(z) = {}".format("".join(self.fx_str)).replace("np.pi", "π").replace("1j", "i").replace("np.", "")
        ax_fx_str.text(0.5, 0.5, fx_str_display, horizontalalignment="center", verticalalignment="center")
        ax_blank.set_visible(False)
        ax_fx_str.set_xticks([])
        ax_fx_str.set_yticks([])
        plt.draw()
    
    def clear_plot_axes(self):
        self.z_pts = []
        self.w_pts = []
        self.update_plot_display()

CM = ComplexMapper(fig)

(N_button_rows, N_button_cols) = (5, 5)
(left_edge, top_edge) = (0.7, 0.8)
[button_width, button_height] = [0.045, 0.1]
[button_width_margin, button_height_margin] = [button_width/4, button_height/4]
# Mapping function readout in the GUI; give it button height but the width of all buttons together
ax_fx_str = fig.add_axes((left_edge, top_edge, N_button_cols*button_width+(N_button_cols-1)*button_width_margin, button_height))
CM.update_fx_str_display()
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
# Make calcluator buttons
for row in range(N_button_rows):
    for col in range(N_button_cols):
        make_button(row, col, col+row*N_button_cols)
# Make button to clear the plots
ax_clear = fig.add_axes((left_edge, top_edge-N_button_rows*button_height-N_button_rows*button_height_margin, N_button_rows*button_width+(N_button_rows-1)*button_width_margin, button_height))
button_clear = Button(ax_clear, "Clear axes", color="0.75", hovercolor="0.875")
button_clear.on_clicked(func=lambda x: CM.clear_plot_axes())

plt.show()
