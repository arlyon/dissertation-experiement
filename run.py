#!/usr/bin/env python3

import csv
import random
from collections import namedtuple
from datetime import timedelta, datetime
from typing import Iterable, List

from psychopy import visual, core, gui, event
from psychopy.visual import movie3

# An association between a meaning, word and sign.
Association = namedtuple('Association', ['meaning', 'word', 'sign'], verbose=True)

# A phase of the experiment.
Phase = namedtuple('Test', ['meaning', 'stimulus', 'show', 'test'], verbose=True)

window = visual.Window([800, 600], monitor="testMonitor", units="deg")


def create_sign_phase(meaning_text, sign_file) -> Phase:
    def show():
        """
        Shows the given sign twice along with the meaning.
        """
        sign = movie3.MovieStim3(window, f"video/{sign_file}", pos=(0, 5), loop=True, noAudio=True, size=(200, 300))
        meaning = visual.TextStim(window, meaning_text, pos=(0, -5))
        start = datetime.now()

        while datetime.now() - start < timedelta(seconds=sign.duration * 2):
            sign.draw()
            meaning.draw()
            window.flip()

    def test():
        """
        Shows the sign on a loop, prompting for input.
        """
        input_text = input_text_old = ""
        getting_input = True

        prompt = visual.TextStim(window, "What does this sign mean?", pos=(0, -5))
        sign = movie3.MovieStim3(window, f"vids/{sign_file}", pos=(0, 5), loop=True, noAudio=True, size=(200, 300))
        answer = placeholder = visual.TextStim(window, "Type your answer. When you are done press return.", pos=(0, -7),
                                               color=(0.5, 0.5, 0.5))

        while getting_input:
            pressed_keys = event.getKeys(
                keyList=['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                         'z', 'x', 'c', 'v', 'b', 'n', 'm', 'backspace', 'space', 'return', 'escape'])
            if 'escape' in pressed_keys:
                teardown()
            for key in pressed_keys:
                if key == 'return':
                    getting_input = False
                elif key == 'backspace':
                    if len(input_text) > 0:
                        input_text = input_text[:-1]
                elif key == 'space':
                    input_text += " "
                else:
                    input_text += key

            if input_text != input_text_old:
                input_text_old = input_text
                answer = visual.TextStim(window, input_text, pos=(0, -7)) if len(input_text) > 0 else placeholder

            prompt.draw()
            sign.draw()
            answer.draw()
            window.flip()

        return input_text

    return Phase(meaning_text, sign_file, show, test)


def create_word_phase(meaning_text, word_text) -> Phase:
    def show():
        """
        Shows the given word alongside the meaning for 5 seconds.
        """
        word = visual.TextStim(window, word_text, pos=(0, 1))
        meaning = visual.TextStim(window, meaning_text, pos=(0, -1))

        word.draw()
        window.flip()
        core.wait(2)
        word.draw()
        meaning.draw()
        window.flip()
        core.wait(3)

    def test():
        """
        Shows the word and prompts for the meaning.
        """
        input_text = input_text_old = ""
        getting_input = True

        prompt = visual.TextStim(window, "What does this word mean?", pos=(0, 2))
        word = visual.TextStim(window, word_text, pos=(0, -2))
        answer = placeholder = visual.TextStim(window, "Type your answer. When you are done press return.", pos=(0, -7),
                                               color=(0.5, 0.5, 0.5))

        prompt.draw()
        word.draw()
        answer.draw()
        window.flip()

        while getting_input:
            pressed_keys = event.getKeys(
                keyList=['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                         'z', 'x', 'c', 'v', 'b', 'n', 'm', 'backspace', 'space', 'return', 'escape'])
            if 'escape' in pressed_keys:
                teardown()
            for key in pressed_keys:
                if key == 'return':
                    getting_input = False
                elif key == 'backspace':
                    if len(input_text) > 0:
                        input_text = input_text[:-1]
                elif key == 'space':
                    input_text += " "
                else:
                    input_text += key

            if input_text != input_text_old:
                input_text_old = input_text
                answer = visual.TextStim(window, input_text, pos=(0, -7)) if len(input_text) > 0 else placeholder
                prompt.draw()
                word.draw()
                answer.draw()
                window.flip()

        return input_text

    return Phase(meaning_text, word_text, show, test)


def generate_experiment(entries: List[Association], word_count, sign_count) -> Iterable[Phase]:
    """
    Creates an experiment itinerary from a count of words and signs.
    :param entries: The list of associations from input.csv
    :param word_count: The number of desired word->meaning associations
    :param sign_count: The number of desired sign->meaning associations
    :return: An iterable collection of phases.
    """
    if len(entries) < word_count + sign_count:
        teardown()

    entries_copy = entries[:]
    phases: List[Phase] = []

    for item in range(word_count):
        entry = random.choice(entries_copy)
        entries_copy.remove(entry)
        phases.append(create_word_phase(entry.meaning, entry.word))

    for item in range(sign_count):
        entry = random.choice(entries_copy)
        entries_copy.remove(entry)
        phases.append(create_sign_phase(entry.meaning, entry.sign))

    return phases


def teardown():
    """
    Performs teardown of window before quit.
    """
    window.close()
    core.quit()


def show_message(message, wait_for_input=True):
    """
    Displays a message to the user and waits for any key to continue.
    :param wait_for_input: Whether to wait for a button press.
    :param message: The message to display.
    """
    message = visual.TextStim(
        window,
        message,
        pos=(0, 0)
    )

    message.draw()
    window.flip()

    if not wait_for_input:
        time = datetime.now()
        while datetime.now() - time < timedelta(seconds=3):
            message.draw()
            window.flip()
        return

    while True:
        keys = event.getKeys()
        if any(keys):
            if 'escape' in keys:
                teardown()
            else:
                break

        message.draw()
        window.flip()


if __name__ == '__main__':

    intro_dialog = gui.Dlg(title="Experiment Info", pos=(100, 100))
    intro_dialog.addField('PID:')
    intro_dialog.addField('Hearing (yes, no):')
    intro_dialog.show()

    if not intro_dialog.OK:
        teardown()

    pid = intro_dialog.data[0]
    hearing = True if intro_dialog.data[1] == "yes" else False

    with open('input.csv', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        data = [Association(meaning, word, sign) for (meaning, word, sign) in reader]

    # no data, quit
    if not len(data) > 0:
        teardown()

    # calculate the number of sign or word based phases
    whole_data_count = len(data)
    half_data_count = int(whole_data_count / 2)
    signs = half_data_count if hearing else whole_data_count
    words = whole_data_count - half_data_count if hearing else 0

    show_message(
        "Welcome! Thank you for taking part in this experiment. It should take no more than 30 minutes. Press any key to continue.")
    show_message(
        f"You will now see {(str(signs) + ' novel signs') if signs else ''}{' and ' if signs and words else ''}{(str(words) + ' novel words') if words else ''}. {'Each sign will be shown twice. ' if signs else ''}Try to remember as many as possible. Press any key to begin.")

    phases = generate_experiment(data, words, signs)

    random.shuffle(phases)
    for phase in phases:
        phase.show()

    show_message(
        f"You have now seen all the novel {'signs' if signs else ''}{' and ' if signs and words else ''}{'words' if words else ''} once. You will see them once more. Feel free to take a short break. Press any key to continue.")

    random.shuffle(phases)
    for phase in phases:
        phase.show()

    show_message(
        f"In the next stage you will see all the novel {'signs' if signs else ''}{' and ' if signs and words else ''}{'words' if words else ''} again and be asked to recall their meaning. Type in your answer using the keyboard and press enter when finished. Press any key to begin.")

    data = []

    random.shuffle(phases)
    for phase in phases:
        result = phase.test()
        data.append((phase.meaning, phase.stimulus, result))

    with open(f"{pid}-output.csv", "w") as out:
        csv_out = csv.writer(out)
        for row in data:
            csv_out.writerow(row)

    show_message("Congratulations, you have completed the experiment. Thank you for your contribution.",
                 wait_for_input=False)
