import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

fig_height = 4
width_ratios = [1,1,1]
fig_size = [fig_height*np.sum(np.array(width_ratios)), fig_height]
fig, [ax1, ax2, ax_blank] = plt.subplots(1, 3, width_ratios=width_ratios, figsize=fig_size)
fig.set_facecolor("0.9")

(subplots_top, subplots_left) = (0.9, 0.03)
(subplots_right, subplots_bottom) = (1-subplots_left, 1-subplots_top)
subplots_spacing = 0.1
plt.subplots_adjust(top=subplots_top, bottom=subplots_bottom, left=subplots_left, right=subplots_right, hspace=subplots_spacing, wspace=subplots_spacing)
# List of button axes; to be filled later
(N_button_rows, N_button_cols) = (5, 5)
(left_edge, top_edge) = (0.68, 0.8)
[button_width, button_height] = [0.3/(N_button_cols+N_button_cols*0.25), (subplots_top-subplots_bottom)/(N_button_rows+2+(N_button_rows+1)*0.25)] # Since button margin will be button size/4; add 2 for readout and axes-clearing button
[button_width_margin, button_height_margin] = [button_width/4, button_height/4]
button_axes = []
# Readout in the GUI showing the mapping function; give it button height but the width of all buttons together
ax_fx_str = fig.add_axes((left_edge, top_edge, N_button_cols*button_width+(N_button_cols-1)*button_width_margin, button_height))
# Button to clear axes
ax_clear = fig.add_axes((left_edge, top_edge-(N_button_rows+1)*button_height-(N_button_rows+1)*button_height_margin, N_button_rows*button_width+(N_button_rows-1)*button_width_margin, button_height))

# Axes to display intro and error messages
ax_message = fig.add_axes((subplots_left, subplots_bottom, subplots_right-subplots_left, subplots_top-subplots_bottom))
def display_message(message):
    # Maxe message axes visible and all other axes invisible
    for ax in [ax1, ax2]+button_axes:
        ax.set_visible(False)
    ax_fx_str.set_visible(False)
    ax_clear.set_visible(False)
    ax_message.set_visible(True)
    ax_message.clear()
    ax_message.axis("off")
    ax_message.text(0.5, 0.5, message, horizontalalignment="center", verticalalignment="center", fontsize=14)
    plt.draw()
error_message = """Invalid function syntax - check your complex map and try again.
Note that multiplication must be explicit, e.g. 2*z not 2z.
Click to close this message."""

class ComplexMapper:
    
    def __init__(self, fig):
        self.z_pts = []
        self.fx_str = ["z", "**", "2"]
        self.left_click_down = False
        self.total_scroll_amount = 0
        self.press_cb = fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.move_cb = fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.release_cb = fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.scroll_cb = fig.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.update_plot_display()
    
    def update_plot_display(self):
        for ax in [ax1, ax2]:
            ax.clear()
            ax.autoscale(enable=False)
            base_ax_lim = np.array([-2,2])
            scaled_ax_lim = base_ax_lim*((1.1)**self.total_scroll_amount)
            ax.set_xlim(scaled_ax_lim)
            ax.set_ylim(scaled_ax_lim)
            [(scaled_ax_min, scaled_ax_max), scaled_ax_range] = [scaled_ax_lim, scaled_ax_lim[1]-scaled_ax_lim[0]]
            ax.spines[["left", "bottom"]].set_position("zero")
            ax.spines[["right", "top"]].set_visible(False)
            def simplify_ticks(lim):
                # Keep the axis limits looking clean as we zoom by choosing a number OTF int x 10^X as the largest tick
                lim_sign = np.sign(lim)
                lim_exponent = np.floor(np.log10(lim_sign*lim))
                return lim_sign*np.fix(lim_sign*lim/(10**lim_exponent))*(10**lim_exponent)
            (tick_min, tick_max) = (simplify_ticks(scaled_ax_min), simplify_ticks(scaled_ax_max))
            ax.set_xticks(np.linspace(tick_min, tick_max, 5))
            ax.set_yticks(np.linspace(tick_min, tick_max, 5))
        label_inset = 0.025
        ax1.text(scaled_ax_min+label_inset*scaled_ax_range, scaled_ax_max-label_inset*scaled_ax_range, "z", horizontalalignment="left", verticalalignment="top", fontsize=12)
        ax2.text(scaled_ax_min+label_inset*scaled_ax_range, scaled_ax_max-label_inset*scaled_ax_range, "f(z)", horizontalalignment="left", verticalalignment="top", fontsize=12)
        for z_curve in self.z_pts:
            ax1.plot(np.real(z_curve), np.imag(z_curve), color="#0000B0")
            # Evaluate in a function to limit the scope of a variable with a very general name like z
            def fx(): z = z_curve; return eval("".join(self.fx_str))
            w_curve = fx()
            ax2.plot(np.real(w_curve), np.imag(w_curve), color="#B00000")
        plt.draw()
    
    def on_press(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.z_pts.append(np.array([event.xdata + 1j*event.ydata]))
            self.left_click_down = True
            try:
                self.update_plot_display()
            except Exception:
                display_message(error_message)
    
    def on_move(self, event):
        if event.inaxes==ax1 and self.left_click_down==True:
            self.z_pts[-1] = np.append(self.z_pts[-1], event.xdata + 1j*event.ydata)
            try:
                self.update_plot_display()
            except Exception:
                display_message(error_message)
                # Release held button so as not to trigger continuous redraw attempts on moving over ax1
                self.left_click_down = False
        if event.inaxes!=ax1:        
            # Release the mouse if we move outside the axes
            self.left_click_down = False
    
    def on_release(self, event):
        if event.button==1 and event.inaxes==ax1:
            self.left_click_down = False
            try:
                self.update_plot_display()
            except:
                # Don't display the error message upon release in case the user clicks and release above ax1 while dismissing it
                pass
    
    def on_scroll(self, event):
        self.total_scroll_amount -= event.step
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
        fx_str_display = "f(z) = {}".format("".join(self.fx_str)).replace("np.pi", "π").replace("1j", "i").replace("np.", "").replace("**", "^")
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

CM.update_fx_str_display()
# Update top_edge so buttons are below text box
top_edge -= button_height+button_height_margin
# Used in actual function
button_strings = ["Clear", "Back", "(", ")", "np.log(",
                  "7", "8", "9", "/", "np.exp(",
                  "4", "5", "6", "*", "**",
                  "1", "2", "3", "-", "np.pi",
                  "z", "0", ".", "+", "1j"]
# Used in GUI
button_labels = ["Clear", "Back", "(", ")", "ln",
                  "7", "8", "9", "/", "exp",
                  "4", "5", "6", "×", "^",
                  "1", "2", "3", "–", "π",
                  "z", "0", ".", "+", "$i$"]
buttons = []
def make_button(row, col, str_index):
    button_horizontal_position = left_edge + col*(button_width+button_width_margin)
    button_vertical_position = top_edge - row*(button_height+button_height_margin)
    button_axes.append(fig.add_axes((button_horizontal_position, button_vertical_position, button_width, button_height)))
    buttons.append(Button(button_axes[-1], button_labels[str_index], color="0.75", hovercolor="0.875"))
    buttons[-1].on_clicked(func=lambda x: CM.fx_str_builder(button_strings[str_index]))
# Make calculator buttons
for row in range(N_button_rows):
    for col in range(N_button_cols):
        make_button(row, col, col+row*N_button_cols)
# Make button to clear the plots
button_clear = Button(ax_clear, "Clear axes", color="0.75", hovercolor="0.875")
button_clear.on_clicked(func=lambda x: CM.clear_plot_axes())

def dismiss_message(event):
    # Maxe message axes invisible and all other axes visible
    for ax in [ax1, ax2]+button_axes:
        ax.set_visible(True)
    ax_fx_str.set_visible(True)
    ax_clear.set_visible(True)
    ax_message.set_visible(False)
    plt.draw()
message_dismiss_cb = fig.canvas.mpl_connect("button_press_event", dismiss_message)

intro_message = """This tool takes user-drawn curves from one copy of the complex plane and maps them to another.
Click and hold with the left mouse button to draw curves in the complex plane on the left.
They will be mapped by a function you define into the complex plane on the right.
You can zoom in and out with the scroll wheel.
Use the calculator buttons on the right to define your own complex map.
Click to close this message and open the tool."""
display_message(intro_message)

plt.show()
