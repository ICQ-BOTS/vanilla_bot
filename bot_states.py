import state
import bot_db
from button_menu import ButtonsMenuBuilder, ButtonCallbackHandler
from io import BytesIO
import xmlrpc.client

import logging
import os

log = logging.getLogger(__name__)

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# --------------------------------root state--------------------------------

RETURN_TO_ROOT_BUTTON_ACTION = "return_to_root"
CANCEL_BUTTON_ACTION = "cancel"


async def default_root_return_handler(bot, user, event, args):
    global root_state
    return state.callback_enter_state(
        root_state, bot, user, event, {"end_session": True}
    )


async def standart_buttons_callback_handler(bot, user, event, args):
    return await user.current_state.buttons_callback_handler.handle_event(
        bot, user, event, user.current_state
    )


ROOT_GEN_POSTCARD = "root:gen_postcard"
ROOT_GET_STATISTICS_BUTTON_ACTION = "root:get_statistics"
ROOT_RETURN_TO_PREV = "root:return_to_prev"
ROOT_GET_FAST_STATISTICS_BUTTON_ACTION = "root:get_fast_statistics"

current_edit_user = None


def lock_tests_edit(user):
    global current_edit_user
    if current_edit_user:
        return False

    current_edit_user = user
    return True


def unlock_tests_edit():
    global current_edit_user
    current_edit_user = None


async def on_root_enter(bot, user, event, args):
    global current_edit_user

    bmb = ButtonsMenuBuilder()

    last_image = user.state_params.get("last_image", None)
    if not last_image:
        if "image_id" in user.state_params:
            if bot_db.get_last_image(user.id):
                bmb.add_action_button("Вернуться к предыдущей", ROOT_RETURN_TO_PREV)
                bmb.next_row()
    else:
        user.state_params["image_id"] = last_image
        bot_db.push_to_history(user.id, last_image)
        del user.state_params["last_image"]

    if "image_id" in user.state_params:
        bmb.add_action_button("Получить еще одну 🌷", ROOT_GEN_POSTCARD)
    else:
        bmb.add_action_button("Получить цитату 💐", ROOT_GEN_POSTCARD)

    if user.permissions == 2:
        bmb.next_row()
        bmb.add_action_button("Статистика", ROOT_GET_STATISTICS_BUTTON_ACTION)
        bmb.next_row()
        bmb.add_action_button(
            "Быстрая статистика", ROOT_GET_FAST_STATISTICS_BUTTON_ACTION
        )

    if "image_id" in user.state_params:
        await state.show_message(
            bot=bot,
            user=user,
            text=None,
            message_image=user.state_params["image_id"],
            buttons=bmb.get_to_send(),
        )
    else:
        await state.show_message(
            bot=bot,
            user=user,
            text="🌺 Привет! В моем электронном мозгу тысячи ванильных цитат из интернета. Составлю для тебя идеальную, жми на кнопку ",
            buttons=bmb.get_to_send(),
        )

    return None


async def gen_postcard(bot, user, event, args):
    data_image = postcards_server.get_random_vanilla_postcard(user.id, 2)
    if data_image:
        byte_io = BytesIO(data_image.data)
        byte_io.seek(0)
        byte_io.name = "generated_image.jpg"
        upload_response = await bot.send_file(chat_id=state.TRASH_CHAT, file=byte_io)
        log.info(f"Upload response: {upload_response}")
        message_image = upload_response.get("fileId", None)
        log.info(f"Image id: {message_image}")
        user.state_params["image_id"] = message_image
        bot_db.push_to_history(user.id, message_image)

    bot_db.add_user_picture_gen(user.id)

    return state.callback_enter_state(root_state, bot, user, event)


async def return_to_prev(bot, user, event, args):
    last_image_id = bot_db.get_last_image(user.id)
    if last_image_id:
        user.state_params["last_image"] = last_image_id

    return state.callback_enter_state(root_state, bot, user, event)


async def get_statistics(bot, user, event, args):
    if user.permissions == 0:
        return state.callback_enter_state(root_state, bot, user, event)

    workbook = bot_db.get_statistics()
    file = os.path.join(SCRIPT_PATH, "statistics", "statistics.xlsx")
    workbook.save(file)

    bmb = ButtonsMenuBuilder()
    bmb.add_action_button("Спасибо!", RETURN_TO_ROOT_BUTTON_ACTION)
    await state.show_message(
        bot=bot,
        user=user,
        text="Статистика:",
        buttons=bmb.get_to_send(),
        file=open(file, "rb"),
    )
    if os.path.exists(file):
        os.remove(file)

    return state.callback_wait_for_input(bot, user, False)


async def get_fast_statistics(bot, user, event, args):
    if user.permissions == 0:
        return state.callback_enter_state(root_state, bot, user, event)
    return state.callback_enter_state(fast_statistics, bot, user, event)


# --------------------------------root state--------------------------------

# ----------------------------Fast statistics state-----------------------


async def on_fast_statistics_enter(bot, user, event, args):

    bmb = ButtonsMenuBuilder()

    common, users_count = bot_db.get_fast_statistics()

    message_text = "Статстика генераций открыток:"

    bmb.add_action_button("Спасибо!", CANCEL_BUTTON_ACTION)

    message_text += "\n\nВсего генераций: %d" % (common)
    message_text += "\nВсего пользователей: %d" % (users_count)
    await state.show_message(
        bot=bot, user=user, text=message_text, buttons=bmb.get_to_send()
    )
    return state.callback_wait_for_input(bot, user, False, args)


# ----------------------------Fast statistics state-----------------------


def init(postcards_ip, postcards_port, db_host, db_port):
    global root_state, fast_statistics, postcards_server
    bot_db.connect(db_host, db_port)

    postcards_server = xmlrpc.client.ServerProxy(
        f"http://{postcards_ip}:{postcards_port}"
    )

    # root state

    root_state = state.State("root", on_root_enter, standart_buttons_callback_handler)
    root_state.buttons_callback_handler = ButtonCallbackHandler()
    root_state.buttons_callback_handler.add_action(ROOT_GEN_POSTCARD, gen_postcard)
    root_state.buttons_callback_handler.add_action(ROOT_RETURN_TO_PREV, return_to_prev)

    root_state.buttons_callback_handler.add_action(
        ROOT_GET_STATISTICS_BUTTON_ACTION, get_statistics
    )
    root_state.buttons_callback_handler.add_action(
        ROOT_GET_FAST_STATISTICS_BUTTON_ACTION, get_fast_statistics
    )

    root_state.buttons_callback_handler.add_action(
        RETURN_TO_ROOT_BUTTON_ACTION, default_root_return_handler
    )

    # Fast statistics

    fast_statistics = state.State(
        "Fast statistics", on_fast_statistics_enter, standart_buttons_callback_handler
    )
    fast_statistics.buttons_callback_handler = ButtonCallbackHandler()

    fast_statistics.buttons_callback_handler.add_action(
        CANCEL_BUTTON_ACTION, default_root_return_handler
    )

    state.set_root_state(root_state)
