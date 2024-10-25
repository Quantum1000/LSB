import matplotlib.pyplot as plt
import numpy as np

def PDH(img1, img2):
    arr = img1.astype(np.int16).copy().reshape((-1))
    diffed = arr-np.roll(arr,3)
    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True, figsize=(20,10))
    bins = range(-255, 255+1)
    for ax in axs:
        ax.set_xlim([-255, 255])
    axs[0].hist(diffed, bins=bins)
    arr = img2.astype(np.int16).copy().reshape((-1))
    diffed = arr-np.roll(arr,3)
    axs[1].hist(diffed, bins=bins)
    plt.show()