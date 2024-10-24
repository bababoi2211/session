
import logging
import telebot
import requests
from api import CountryInfo
import datetime

from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove


logging.basicConfig(filename="project.log",
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode="w", level=logging.DEBUG)


user_step = dict()
user_data = dict()
user_asked_country = list()
repeated_command = dict()


commands = {
    "info_country": "get information about the country(Region/Currency/Capital/...)",
    "forcast": "get information about forecast of the country (with specefic Date)",
    "show_flag": "shows the flag of the chossen country on chat(jpeg/text)",

}


API_TOKEN = "7817179572:AAFxG-Uuf4J_isk4asYHpTjrZR3Ger8o34k"
bot = telebot.TeleBot(token=API_TOKEN)

markup = ReplyKeyboardMarkup(resize_keyboard=True)
hideout = ReplyKeyboardRemove()


# region helper function
def checking_country(message, user_data):
    logging.debug("checking the existence of the country")
    cid = message.chat.id

    if message.text in user_data.get(cid, []):
        bot.send_message(
            cid, "You have already asked About this country(data deleted)...")

        user_asked_country.remove(f"{message.text}")
        user_data[cid] = user_asked_country

        if len(user_data[cid]) == 0:
            user_data[cid].append(message.text)

        logging.warning("the country Exist")

    user_asked_country.append(message.text)
    user_data[cid] = user_asked_country

    if CountryInfo.check_exist_country(country=message.text) != False:
        refrenced_country = CountryInfo.check_exist_country(
            country=message.text)

        bot.send_message(
            cid, f"did you mean ({refrenced_country})\n please try again.\n /help")
        return True

# endregion


try:
    def listener(message):

        for m in message:
            if m.content_type == "text":
                user_data = f"{m.chat.first_name}  [{m.chat.id}]: {m.text}"
                print(user_data)
                logging.debug(user_data)

    @bot.message_handler(commands=["start"])
    def start_handler(message):
        bot.reply_to(message, f"Welcome {
                     message.chat.first_name}! 🌍\nYou can learn about countries, their flags, and their forecasts. 😉")

    @bot.message_handler(commands=["help"])
    def help_handler(message):
        logging.debug("User has Entered Command help")

        cid = message.chat.id

        markup.add("Info Country🤔", "Flags 🚩")
        markup.add("Forcast 🏞️")

        # region making info text
        text = "these are The Phone Store Command center.\n"

        help_text = "Available commands:\n" + \
            "\n".join([f"<{cmd}>:{desc}\n" for cmd, desc in commands.items()])
        # endregion

        if repeated_command.get(cid) == "help":
            bot.send_message(
                cid, "You Already clicked this command. ", reply_markup=hideout)
            repeated_command.clear()

        else:
            bot.send_message(cid, help_text, reply_markup=markup)
            repeated_command[cid] = "help"

    # this command equals () steps

    @bot.message_handler(func=lambda m: m.text == "Info Country🤔")
    def command_info_handler(message):
        logging.debug("Entering the info function")
        cid = message.chat.id

        bot.send_message(
            cid, "please Enter the Country That you want to know:", reply_markup=hideout)

        user_step[cid] = "info(A)"

    @bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "info(A)")
    def command_info_A_handler(message):
        try:
            logging.debug("Entering the part A of info")
            cid = message.chat.id

            logging.debug("checking the existence of the country")
            if message.text in user_data.get(cid, []):
                bot.send_message(
                    cid, "You have already asked About this country")
                user_step[cid] = 0
                logging.warning("the country Exist")
                return ""

            logging.debug(
                "cheking the database for the existence of this country ")
            if CountryInfo.check_exist_country(country=message.text) != False:
                refrenced_country = CountryInfo.check_exist_country(
                    country=message.text)

                bot.send_message(
                    cid, f"did you mean ({refrenced_country})\n please try again.\n /help")
                return ""

            logging.debug("message has passed all the checks")

            response = requests.get(
                f"https://restcountries.com/v3.1/name/{message.text}")

            details = CountryInfo.show_details(response.json())

            bot.send_message(cid, details, reply_markup=markup)

            user_asked_country.append(message.text)
            user_data[cid] = user_asked_country
            user_step[cid] = "None"

        except requests.HTTPError as err:
            logging.error({"Http Error Has Happend": err})

        except BaseException as err:
            bot.send_message(cid, err)
            logging.error({"Exception error": err})

    @bot.message_handler(func=lambda m: m.text == "Flags 🚩")
    def command_flag_A_handler(message):
        logging.debug("Entering command flag handler  ")
        cid = message.chat.id

        bot.send_message(cid, "Enter the Country : ", reply_markup=hideout)

        user_step[cid] = "flag(A)"

    @bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "flag(A)")
    def command_flag_A_handler(message):

        # region checking the country status
        logging.debug("Entering command flag handler (A) ")
        cid = message.chat.id

        if checking_country(message, user_data) == True:
            return ""

        # endregion
        logging.debug("message has passed all the if statment")

        # region making requests and placing the image
        try:

            response = requests.get(
                f"https://restcountries.com/v3.1/name/{message.text}")

            CountryInfo.get_image(response.json(), message.text)
            bot.send_message(cid, "image has been created.",
                             reply_markup=hideout)
            # endregion

            # region markup for cmd or img
            markup.add("Shows with symbole 📪")
            markup.add("Send Image 🗺️")

            bot.send_message(cid, "How you Want to be shown ?",
                             reply_markup=markup)

            # endregion

            user_asked_country.append(message.text)
            user_data[cid] = user_asked_country
            user_step[cid] = "flag(B)"

        except requests.HTTPError as err:
            logging.error({"Http Error": err})

    @bot.message_handler(func=lambda m: m.text == "Shows with symbole 📪")
    def command_show_chat_handler(message):
        logging.debug("Enter the show on chat option")
        cid = message.chat.id
        terminal_img = CountryInfo.show_img_cmd(
            f"images/{user_data[cid][-1]}_img/{user_data[cid][-1]}")

        bot.send_message(
            cid, f"/// \n{terminal_img}///\n for better view watch it in your pc ")

        with open(file="symbole.txt", mode="w") as f:
            f.write(terminal_img)

        with open(file="symbole.txt", mode="rb") as file:
            bot.send_document(cid, file, reply_markup=hideout)

        user_step[cid] = 0

    @bot.message_handler(func=lambda m: m.text == "Send Image 🗺️")
    def command_img_handler(message):
        try:
            logging.debug("Entering the image handler func.")

            cid = message.chat.id

            bot.send_message(cid, "Here is your image.\n")

            with open(file=f"images/{user_data[cid][-1]}_img/{user_data[cid][-1]}", mode="rb") as file:
                bot.send_photo(cid, file, reply_markup=hideout)

            user_step[cid] = 0

        except BaseException as err:
            logging.error({"Base error has happend ": err})

    @bot.message_handler(func=lambda m: m.text == "Forcast 🏞️")
    def command_forecast_handler(message):
        logging.debug("Entering forecast handler.")
        cid = message.chat.id

        bot.send_message(
            cid, "Which Forcast of Country you want to know about?", reply_markup=hideout)

        user_step[cid] = "forcast(A)"

    @bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "forcast(A)")
    def command_forcast_A_handler(message):
        logging.debug("Entering the image handler func part (A) ")
        cid = message.chat.id

        # region checking Country
        if checking_country(message, user_data) == True:
            return ""
        # endregion

        logging.debug("message has passed all the if statment")

        bot.send_message(
            cid, "Please Enter the day you want to know about the forecast(Like : 2(days) or 3,... ):")

        user_step[cid] = "forcast(B)"

    @bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "forcast(B)")
    def command_forcast_B_handler(message):
        try:
            logging.debug("Entering the forcast handler part(B)")
            cid = message.chat.id

            logging.debug("Calculating the enter day")
            # region calculating time
            date_now = datetime.datetime.now()
            time_delta = datetime.timedelta(int(message.text))
            res_data = date_now + time_delta
            format_data = res_data.strftime("%Y-%m-%d")
            # endregion

            response_weather = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{
                user_data[cid][-1]}/{format_data}?key=ERMW3K6222K5DZ2Y2SCJ8R3UV")

            result = CountryInfo.show_weather(response_weather.json())

            logging.debug("printing the info!")
            for keys, val in result.items():
                bot.send_message(cid, f"{keys}\t\t:\t\t{val}\n")

            logging.debug("Message Has been Sended")
            user_step[cid] = 0

        except BaseException as err:
            logging.error({"Base Error has happend": err})
            bot.send_message(cid, err)

        except requests.HTTPError as err:
            logging.error({"An Http Error Has Happend": err})

    @bot.message_handler(func=lambda message: True)
    def invalid_texts(message):
        bot.reply_to(message, f"""please Enter Valid Argument ('{
                     message.text}' Is Not Valid Argument)\nYou Can Start With this command:\n/help\n/start""")

    bot.set_update_listener(listener)
    bot.infinity_polling()


except BaseException as err:
    logging.error({"Exception error has happend": err})

except telebot.apihelper.ApiException as err:
    logging.error({"api error has happend": err})

except TimeoutError as err:
    logging.error({"connection error": err})

finally:
    logging.debug("telegram bot Turned Off ")
