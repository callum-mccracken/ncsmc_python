import matplotlib.pyplot as plt
import matplotlib.widgets

temp_descr = 'wow'
axLabel = plt.axes([0.7, 0.05, 0.21, 0.075])
textbox = matplotlib.widgets.TextBox(axLabel, 'Label: ', temp_descr)

textbox.set_val("jojojo")
plt.show()