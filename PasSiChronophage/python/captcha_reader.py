"""
Pas Si Chronophage
- DG'Hack 2022
---

@author CorentinGoet
"""

import numpy as np
import cv2
from PIL import Image


class CaptchaReader:
    """
    This class is in charge of reading time from a captcha analog clock.
    """

    def __init__(self, image_path="", image=None):
        self.image_file = image_path
        if image is not None:
            self.original_image = np.asarray(image)
        else:
            self.original_image = self.open_image()
        self.filtered_image = self.filter()
        self.time = None
        self.empty_clock_img = None

    def open_image(self) -> np.ndarray:
        """
        Opens the image file and converts it to numpy array.
        """
        img = np.asarray(Image.open(self.image_file))
        return img

    def save_image(self, output_name: str):
        """
        saves filtered image with given name.
        """
        img = Image.fromarray(self.filtered_image, "RGB")
        img.save(output_name)

    def filter(self) -> np.ndarray:
        """
        Filters the colored lines out of the original image.
        """
        filtered = np.zeros(self.original_image.shape, dtype=np.uint8)
        mask = np.asarray(Image.open("images/mask.png"))[:, :, 0:3]
        masked = np.bitwise_or(self.original_image, mask)
        img = Image.fromarray(masked, "RGB")
        #img.save("masked.png")
        for i in range(masked.shape[0]):
            for j in range(masked.shape[1]):
                if all(masked[i, j] == 255):
                    filtered[i, j] = [255, 255, 255]
                elif all(masked[i, j] == 0):
                    filtered[i, j] = [0, 0, 0]
                else:
                    # we do not need to worry about edge cases
                    # because the pixels close to the edges
                    # are whited out by the mask

                    # count the number of black pixels around
                    thresh = 3   # out of 8
                    cnt = 0
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if all(masked[i + k, j + l] == 0):
                                cnt += 1

                    if cnt >= thresh:
                        filtered[i, j] = [0, 0, 0]
                    else:
                        filtered[i, j] = [255, 255, 255]
        return filtered


    def read_time(self):
        """
        Read the time from the clock by comparing the filtered image to generated clock images.

        This is done in 2 steps:
        - determine minutes by finding the highest correlation between original and all possible minute hands
        - find hour same method
        """

        correlations_min = []
        correlations_hours = []

        target = self.filtered_image[:, :, 0].reshape(200*200)

        # find minutes
        for m in range(0, 60):
            generated = self.generate_clock(0, m, w_hours=0)[:, :, 0].reshape(200*200)
            corr = np.correlate(target, generated)
            correlations_min.append(corr)

        identified_m = correlations_min.index(max(correlations_min))

        for h in range(0, 12):
            generated = self.generate_clock(h, identified_m)[:, :, 0].reshape(200*200)
            corr = np.correlate(target, generated)
            correlations_hours.append(corr)

        identified_h = correlations_hours.index(max(correlations_hours))
        return identified_h, identified_m

    def generate_clock(self, hour: int, minute: int, w_hours=5, w_min=1) -> np.ndarray:
        """
        Generate an image in the form of a numpy array of an analog clock showing the time given as parameter.

        :param w_min: width of minutes hand
        :param w_hour: width of hours hand
        :param hour: hour to show on the clock (1-12)
        :param minute: minute to show on the clock
        :return: numpy array of shape resolution in grayscale with pixel values 0-1.
        """

        hands = 255 * np.ones((200, 200, 3), dtype=np.uint8)

        # drawing parameters
        r_hours = 10    # length for hours hand
        r_min = 70      # length for minutes hand

        # Get angles
        theta_hour, theta_min = self.time2angle(hour, minute)

        # coord of center
        x0, y0 = 100, 100

        # Coords of the hours hand extremity
        x_hour = int(x0 + r_hours * np.cos(theta_hour))
        y_hour = int(y0 + r_hours * np.sin(theta_hour))

        # coords of the minutes hand
        x_min = int(x0 + r_min * np.cos(theta_min))
        y_min = int(y0 + r_min * np.sin(theta_min))

        # draw hands
        if w_hours > 0:
            cv2.line(hands, (x0, y0), (x_hour, y_hour), [0, 0, 0], w_hours)
        if w_min > 0:
            cv2.line(hands, (x0, y0), (x_min, y_min), [0, 0, 0], w_min)

        return hands

    def time2angle(self, hour: int, minute: int):
        """
        Finds angle for hours and minutes hands on analog clock from time.

        :param hour: hour int (0 - 11)
        :param minute: minute (0 - 59)
        :return: (theta_hour, theta_minute) angles in radians for hour and minute hands
        """

        theta_min = minute * (2 * np.pi / 60) - np.pi / 2
        theta_hour = (hour + minute/60) * (2 * np.pi / 12) - np.pi / 2

        return theta_hour, theta_min


if __name__ == '__main__':
    r = CaptchaReader("images/captcha_example.png")
    print(r.read_time())



























