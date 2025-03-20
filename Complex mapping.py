import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

fig_height = 4
width_ratios = [1,1,1]
fig_size = [fig_height*np.sum(np.array(width_ratios)), fig_height]
fig, [ax1, ax2, ax_blank] = plt.subplots(1, 3, width_ratios=width_ratios, figsize=fig_size)
ax_blank.spines[["top", "bottom", "left", "right"]].set_visible(False)
ax_blank.set_xticks([])
ax_blank.set_yticks([])
#plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)

class ComplexMapper:
    
    def __init__(self, fig):
        self.z_pts = []
        self.fx = lambda z: z**2
        self.left_click_down = False
        self.press_cb = fig.canvas.mpl_connect('button_press_event', self.onPress)
        self.move_cb = fig.canvas.mpl_connect('motion_notify_event', self.onMove)
        self.release_cb = fig.canvas.mpl_connect('button_release_event', self.onRelease)
        self.updateDisplay()
        
    def updateDisplay(self):
        ax1.cla()
        ax2.cla()
        for z_curve in self.z_pts:
            ax1.plot(np.real(z_curve), np.imag(z_curve), color="#0000B0")
            w_curve = self.fx(z_curve)
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


CM = ComplexMapper(fig)

plt.show()
