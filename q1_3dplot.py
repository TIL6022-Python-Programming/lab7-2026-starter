"""
Question 1: 3D Plot with Matplotlib (3 points in total)

For this excercise, you first create a 3D matplotlib figure with the (x, y, z) 
data to satify following requirements:
    (1) generate two subplots that are put side by side (1 point)
    (2) 3D surface plot on the left, use the colormap 'viridis' (1 point)
    (3) 3D wireframe plot on the right, use the color 'blue' (1 point)

The x, y, and z data are given.

"""

import matplotlib.pyplot as plt
import numpy as np

# function to generate z based on x and y
def generate_z(x, y):
    z = np.sin(np.sqrt(x**2 + y**2))
    return z # z should be a 2D array with shape (len(x), len(y))

def create_3d_plots():
    # Generate x and y data
    x = np.linspace(-10, 10, 20)
    y = np.linspace(-10, 10, 20)
    X, Y = np.meshgrid(x, y)
    Z = generate_z(X, Y)

    # Create a matplotlib figure with two subplots
    fig = plt.figure(figsize=(12, 6))
    
    # TODO: complete your code here 


    plt.show()

    return fig

create_3d_plots()