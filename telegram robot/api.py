import requests
import logging
import os

from PIL import Image




class CountryInfo:

    def get_image(json_data, folder_name):
        logging.info("Entering get_image function")
        try:

            # Ensure folder exists
            folder_path = f"images/{folder_name}_img"
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            for info in json_data:
                image_url = info["flags"]["png"]
                file_name = folder_name
                file_path = os.path.join(folder_path, file_name)
                logging.debug(f"Flag URL: {image_url}, File Name: {file_name}")

                image_response = requests.get(image_url)
                # Save image to folder
                with open(file_path, mode="wb") as f:
                    f.write(image_response.content)
                logging.info(f"Image saved at {file_path}")
                return ""

        except requests.RequestException as err:
            logging.error(f"Error downloading image: {err}")
        except Exception as e:
            logging.exception(f"Unexpected error in get_image: {e}")

    def show_details(json_data):
        """show capital fullname currency language region"""
        logging.info("Entering the show details function")

        for info in json_data:

            # region variable
            CURRENCY = list(info["currencies"].keys())[0]
            CURRENCY_NAME = list(info["currencies"].values())[0]["name"]
            # endregion

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

    def show_img_cmd(image_path, new_width=80):
        image = Image.open(image_path)
        image = image.convert('L')
        # Resize the image
        width, height = image.size
        aspect_ratio = (height-20) / (width-20)
        new_height = int(new_width * aspect_ratio)

        # Calculate the maximum height for telegram
        max_height = 4096 // (new_width + 1)
        if new_height > max_height:
            new_height = max_height  # Adjust new_height to fit within limit

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

    def show_weather(json_data):
        logging.info("starting the show_weather function")
        try:
            details = {"timezone":      json_data["timezone"],
                       "datetime":      json_data["days"][0]["datetime"],
                       "temp":      json_data["days"][0]["temp"],
                       "humidity":          json_data["days"][0]["humidity"],
                       "windspeed":         json_data["days"][0]["windspeed"],
                       "description":       json_data["days"][0]["description"]
                       }

            return details

        except requests.RequestException as err:
            logging.error(f"Error fetching weather data: {err}")
            return {}

    def check_exist_country(country) -> bool | list[str]:

        def check_exist():

            try:
                CHECK_LIST = []
                logging.debug("accesing all of the data")
                response = requests.get(r"https://restcountries.com/v3.1/all")

                response_json = response.json()
                COUNTRY_DATA = [check["name"]["common"].lower()
                                for check in response_json]

                if not (country.lower() in COUNTRY_DATA):
                    for checking_name in COUNTRY_DATA:
                        if country in checking_name[:len(country)]:
                            CHECK_LIST.append(checking_name)
                    if len(CHECK_LIST) <= 0:
                        CHECK_LIST.append(
                            "We didnt Found this similarity of this country in our databse")
                else:
                    CHECK_LIST = False

                return CHECK_LIST
            except BaseException as err:
                logging.error(err)

        return check_exist()
