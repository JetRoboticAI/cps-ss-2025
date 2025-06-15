from matplotlib import pyplot as plt
import math


f = 100  # Hz
max_t = 10  # seconds

data = []
for x in range(0, max_t * f, 1):
    y = math.sin(f)
    data.append((x, y))

# Extract x and y values from data
x_values = [point[0] for point in data]
y_values = [point[1] for point in data]

# Plot the data
plt.plot(x_values, y_values)
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.title('Sine Wave')
plt.grid(True)
plt.show()


