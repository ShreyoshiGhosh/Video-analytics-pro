import cv2
import numpy as np

def dark_channel_prior(img, size=15):
    """
    Calculate the dark channel prior for the image.
    img: input RGB image as numpy array
    size: patch size for minimum filter
    """
    # Minimum over color channels
    min_channel = np.min(img, axis=2)
    # Apply minimum filter (erode)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    dark_channel = cv2.erode(min_channel, kernel)
    return dark_channel

def estimate_atmospheric_light(img, dark_channel, percentile=0.001):
    """
    Estimate atmospheric light A from the image and dark channel
    percentile: fraction of brightest pixels in dark channel to consider
    """
    flat_dark = dark_channel.ravel()
    flat_img = img.reshape((-1, 3))

    # Number of pixels to consider
    num_pixels = int(max(flat_dark.size * percentile, 1))

    # Indices of pixels with highest intensity in dark channel
    indices = np.argpartition(flat_dark, -num_pixels)[-num_pixels:]

    # Atmospheric light as max intensity pixel among these pixels in original image
    atmospheric_light = np.max(flat_img[indices], axis=0)
    return atmospheric_light

def estimate_transmission(img, A, omega=0.6, size=15):
    """
    Estimate the transmission map t of the image
    omega: weight to keep some haze to avoid artifacts
    """
    norm_img = img.astype(np.float32) / A  # normalize by atmospheric light
    transmission = 1 - omega * dark_channel_prior(norm_img, size=size)
    transmission = np.clip(transmission, 0.1, 1)
    return transmission

def recover_image(img, t, A, t0=0.3):
    """
    Recover haze-free image using transmission map and atmospheric light
    t0: lower bound for transmission to avoid division by zero
    """
    t = np.clip(t, t0, 1.0)
    recovered = np.empty_like(img, dtype=np.float32)
    for c in range(3):
        recovered[:, :, c] = (img[:, :, c] - A[c]) / t + A[c]
    recovered = np.clip(recovered, 0, 255).astype(np.uint8)
    return recovered

def apply_dcp(img0, prev_A=None, prev_t=None):
    """
    Full DCP pipeline: input img0 in uint8 RGB
    Returns dehazed image, updated prev_A and prev_t for smoothness
    """
    dark_channel = dark_channel_prior(img0)

    if prev_A is None:
        A = estimate_atmospheric_light(img0, dark_channel, percentile=0.001)
    else:
        A = 0.9 * prev_A + 0.1 * estimate_atmospheric_light(img0, dark_channel, percentile=0.001)

    t = estimate_transmission(img0, A, omega=0.6, size=15)
    if prev_t is not None:
        t = 0.9 * prev_t + 0.1 * t  # Smooth transition

    img0 = recover_image(img0, t, A, t0=0.3)

    return img0, A, t
def apply_dcp_stream(img0):
    """
    Simplified DCP pipeline for video streams (no history)
    Input: img0 in uint8 RGB
    Returns: dehazed image only
    """
    dark_channel = dark_channel_prior(img0)
    A = estimate_atmospheric_light(img0, dark_channel, percentile=0.001)
    t = estimate_transmission(img0, A, omega=0.6, size=15)
    img0 = recover_image(img0, t, A, t0=0.3)
    return img0

