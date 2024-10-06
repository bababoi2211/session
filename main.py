import requests
import logging
import datetime
from time import sleep
import os
from concurrent.futures import ThreadPoolExecutor
import datetime

from PIL import Image


logging.basicConfig(filename="project.log",
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG, filemode="w")


class CountryInfo:

    def get_image(self, json_data, folder_name):
        logging.info("Entering get_image function")
        try:

            # Ensure folder exists
            folder_path = f"{folder_name}_img"
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            for info in json_data:
                image_url = info["flags"]["png"]
                file_name = folder_name
                file_path = os.path.join(folder_path, file_name)
                logging.debug(f"Flag URL: {image_url}, File Name: {file_name}")

                image_response = requests.get(image_url)
                image_response.raise_for_status()

                # Save image to folder
                with open(file_path, mode="wb") as f:
                    f.write(image_response.content)

                logging.info(f"Image saved at {file_path}")
                break
        except requests.RequestException as err:
            logging.error(f"Error downloading image: {err}")
        except Exception as e:
            logging.exception(f"Unexpected error in get_image: {e}")

    def show_details(self, json_data):
        """show capital fullname currency language region"""
        logging.info("Entering the show details function")

        for info in json_data:

            # region variable
            CURRENCY = list(info["currencies"].keys())[0]
            CURRENCY_NAME = list(info["currencies"].values())[0]["name"]
            # endregion

            print("________________________________________\n")

            details = {"Full name of this country": info["name"]["official"],
                       "capital": info["capital"],
                       "currency of this country": {"name": info["currencies"], "international symbol": CURRENCY},
                       "international name": CURRENCY_NAME,
                       "languages": ",".join(info["languages"].values()),
                       "Region": info.get("region", "N/A")
                       }
            logging.info("making details printable for the user")
            result = str(details).replace(",", ", \n")
            return result

    def show_img_cmd(self, image_path, new_width=100):
        image = Image.open(image_path)
        image = image.convert('L')

        # Resize the image
        width, height = image.size
        aspect_ratio = height/width
        new_height = int(new_width * aspect_ratio)
        image = image.resize((new_width, new_height))

        # Define ASCII characters by brightness level
        ascii_chars = "@%#*+=-:. "
        pixels = image.getdata()
        ascii_str = "".join([ascii_chars[pixel // 32] for pixel in pixels])

        # Format the string for proper display
        ascii_str_len = len(ascii_str)
        ascii_image = "\n".join([ascii_str[index: index + new_width]
                                for index in range(0, ascii_str_len, new_width)])

        return ascii_image

    def show_weather(self, json_data):
        logging.info("starting the show_weather function")
        try:
            print("________________________________________\n")
            details = {"timezone": json_data["timezone"],
                       "datetime": json_data["days"][0]["datetime"],
                       "temp": json_data["days"][0]["temp"],
                       "humidity": json_data["days"][0]["humidity"],
                       "windspeed": json_data["days"][0]["windspeed"],
                       "description": json_data["days"][0]["description"]
                       }

            return details

        except requests.RequestException as err:
            logging.error(f"Error fetching weather data: {err}")
            return {}

    def check_exist_country(self, country) -> bool | list[str]:

        def check_exist():
            CHECK_LIST = []
            try:
                response = requests.get(r"https://restcountries.com/v3.1/all")
                response.raise_for_status()

                response_json = response.json()

                COUNTRY_DATA = [check["name"]["common"].lower()
                                for check in response_json]

                if not (country.lower() in COUNTRY_DATA):
                    for checking_name in COUNTRY_DATA:
                        if country in checking_name[:len(country)]:
                            CHECK_LIST.append(checking_name)

                else:
                    CHECK_LIST = True

                return CHECK_LIST

            except Exception as e:
                logging.exception(f"Unexpected error in get_image: {e}")
        return check_exist()


info = CountryInfo()


def main():
    if os.name == "nt":
        os_model = "cls"
    else:
        os_model = "clear"

    while True:
        logging.debug("starting the Application")

        name_country = input("which country would you like to know about : ")

        if name_country == "q":
            os.system(os_model)
            break

        try:

            result = info.check_exist_country(name_country)
            if result == True:
                response = requests.get(
                    f"https://restcountries.com/v3.1/name/{name_country}")
                response.raise_for_status()

                print("please wait")
                sleep(0.5)
                os.system(os_model)

                print(info.show_details(response.json()), "\n")

                if input("do you want to see the flag (yes/etc): ") == "yes":
                    logging.debug("fetching image and showing it")
                    sleep(0.5)
                    info.get_image(response.json(), folder_name=name_country)

                    logging.debug(
                        "ending of fetching and adding to specefic folder")
                    print("image added to folders")

                    if input("do you want to be shown on cmd?") == "yes":
                        print(info.show_img_cmd(rf"{os.getcwd()}\{
                            name_country}_img\{name_country}"))

                    sleep(6)
                os.system(os_model)

                if input("do you want to know the forecast for this country(yes/etc): ") == "yes":
                    day = int(
                        input("which upcoming day would you want to know about : "))

                    # region calculating time
                    date_now = datetime.datetime.now()
                    time_delta = datetime.timedelta(day)
                    res_data = date_now + time_delta
                    format_data = res_data.strftime("%Y-%m-%d")
                    # endregion
                    response_weather = requests.get(
                        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{name_country}/{format_data}?key=ERMW3K6222K5DZ2Y2SCJ8R3UV")

                    result = info.show_weather(response_weather.json())
                    logging.debug("printing the info!")
                    for keys, val in result.items():
                        print(f"{keys}:{val}")

                sleep(5)
                os.system(os_model)
            else:
                logging.warning("user has inputed incorectly")
                print({"Did You mean": info.check_exist_country(country=name_country)})
                continue

        except requests.HTTPError as err:
            logging.ERROR({"Http Error Has Happend": err})
        except BaseException as e:
            logging.ERROR({"Exception error": e})


main()
