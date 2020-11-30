import json
import state

import utils
import logging

log = logging.getLogger(__name__)


class ButtonCallbackHandler:
    def __init__(self):
        self.actions = {}

    def add_action(self, id, func):
        self.actions[id] = func

    async def handle_event(self, bot, user, event, goto_if_false=None):

        action_and_args = utils.action_and_args_from_event(event)
        if action_and_args:
            if action_and_args[0] in self.actions:
                func = self.actions[action_and_args[0]]
                if func:
                    result = await func(bot, user, event, action_and_args[1])
                    await state.send_query_response(bot, event)
                    return result

        if goto_if_false:
            user.last_message_id = None
            return await goto_if_false.enter_state(bot, user, event)
        return None


class ButtonsMenuBuilder:
    def __init__(self):
        self.clear()

    def clear(self):
        self.buttons = []
        self.next_row()
        self.is_clear = True

    def next_row(self):
        self.buttons.append([])
        self.is_clear = False

    def add_action_button(self, text, action_id, args={}):
        self.add_callback_button(text, {"action": action_id, "args": args})
        self.is_clear = False

    def add_callback_button(self, text, callback_data, callback_to_json=True):
        if callback_to_json:
            callback_data = json.dumps(callback_data)
        self.buttons[len(self.buttons) - 1].append(
            {"text": text, "callbackData": callback_data}
        )
        self.is_clear = False

    def get_to_send(self, clear=False):
        if self.is_clear:
            return None

        result = self.buttons
        if clear:
            self.clear()
        return json.dumps(result)
