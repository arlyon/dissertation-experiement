#!/usr/bin/env python3

import csv
import random
from collections import namedtuple
from datetime import timedelta, datetime
from psychopy.constants import PLAYING
from typing import Iterable, List
import sys
import os
from collections import defaultdict

from psychopy import visual, core, gui, event, sound
from psychopy.visual import movie3


def app_folder(x):
    """"""
    frozen = getattr(sys, 'frozen', False)
    target_folder = os.getcwd() if not frozen else os.path.dirname(sys.executable)
    return os.path.join(target_folder, x)


# An association between a meaning, word and sign.
Association = namedtuple('Association', ['meaning', 'word', 'sign', 'word_difficulty', 'sign_difficulty'], verbose=True)

# A phase of the experiment.
Phase = namedtuple('Test', ['meaning', 'stimulus', 'show', 'test'], verbose=True)

window = visual.Window([800, 600], monitor="testMonitor", units="deg")


def create_sign_phase(meaning_text, sign_file) -> Phase:
    def show():
        """
        Shows the given sign twice along with the meaning.
        """
        sign = movie3.MovieStim3(window, app_folder(f"video/{sign_file}"), pos=(0, 5), loop=True, noAudio=True,
                                 size=(530, 300))
        meaning = visual.TextStim(window, meaning_text, pos=(0, -5))

        responsive_wait([sign, meaning], sign.duration * 2)

    def test():
        """
        Shows the sign on a loop, prompting for input.
        """
        input_text = input_text_old = ""
        getting_input = True

        prompt = visual.TextStim(window, "What does this sign mean?", pos=(0, -5))
        sign = movie3.MovieStim3(window, app_folder(f"video/{sign_file}"), pos=(0, 5), loop=True, noAudio=True,
                                 size=(530, 300))
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


def responsive_wait(drawables, seconds):
    start = datetime.now()

    while datetime.now() - start < timedelta(seconds=seconds):

        for drawable in drawables:
            drawable.draw()

        window.flip()


def create_word_phase(meaning_text, word_file) -> Phase:
    def show():
        """
        Shows the given word alongside the meaning for 5 seconds.
        """
        word = sound.Sound(value=app_folder(f"sound/{word_file}"))
        meaning = visual.TextStim(window, meaning_text, pos=(0, 0))

        responsive_wait([meaning], 1)

        for i in range(2):
            word.play()
            responsive_wait([meaning], 3)

        responsive_wait([meaning], 1)

    def test():
        """
        Shows the word and prompts for the meaning.
        """
        input_text = input_text_old = ""
        getting_input = True

        prompt = visual.TextStim(window, "What does this word mean?", pos=(0, 0))
        answer = placeholder = visual.TextStim(window, "Type your answer. When you are done press return.", pos=(0, -7),
                                               color=(0.5, 0.5, 0.5))

        word = sound.Sound(value=app_folder(f"sound/{word_file}"))
        last_played = datetime.now()
        word.play()

        prompt.draw()
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
                answer.draw()
                window.flip()

            if datetime.now() - last_played > timedelta(seconds=3):
                last_played = datetime.now()
                word.play()

        word.stop()
        return input_text

    return Phase(meaning_text, word_file, show, test)


def generate_experiment(entries: List[Association], word_count, sign_count) -> Iterable[Phase]:
    """
    Creates an experiment itinerary from a count of words and signs.
    :param entries: The list of associations from input.csv
    :param word_count: The number of desired word->meaning associations
    :param sign_count: The number of desired sign->meaning associations
    :return: An iterable collection of phases.
    """

    def pick_n_from_each_category(grouping_func, items, n):

        picked = []

        group = defaultdict(list)
        for entry in items:
            group[grouping_func(entry)].append(entry)

        if n % len(group) != 0:
            raise Exception()

        if not all(len(difficulty) >= n / len(group) for difficulty in group.values()):
            raise Exception()

        for difficulty, members in group.items():
            for item in range(int(n / len(group))):
                entry = random.choice(members)
                members.remove(entry)
                picked.append(entry)

        return picked, [item for sublist in group.values() for item in sublist]

    if len(entries) < word_count + sign_count:
        teardown()

    words, leftovers = pick_n_from_each_category(lambda x: x.word_difficulty, entries, word_count)
    signs, _ = pick_n_from_each_category(lambda x: x.sign_difficulty, leftovers, sign_count)

    return [create_word_phase(entry.meaning, entry.word) for entry in words] + \
           [create_sign_phase(entry.meaning, entry.sign) for entry in signs]


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

    if not os.path.isfile(app_folder('input.csv')):
        print(f"Could not find input.csv in {app_folder('input.csv')}\n\n", file=sys.stderr)
        exit(1)

    with open(app_folder('input.csv'), newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        data = [Association(*items) for items in reader]

    if not data:
        teardown()

    missing_videos = [association for association in data if
                      not os.path.isfile(app_folder(f"video/{association.sign}"))]
    if missing_videos:
        missing_videos = ('\n'.join(f'    - "{m.meaning}" ({m.sign})' for m in missing_videos))
        print(f"Could not find required videos for:\n{missing_videos}\nin {app_folder('video')}\n\n", file=sys.stderr)
        exit(1)

    missing_sounds = [association for association in data if
                      not os.path.isfile(app_folder(f"sound/{association.word}"))]
    if missing_sounds:
        missing_sounds = ('\n'.join(f'    - "{m.meaning}" ({m.word})' for m in missing_sounds))
        print(f"Could not find required sounds for:\n{missing_sounds}\nin {app_folder('sound')}\n\n",
              file=sys.stderr)
        exit(1)

    intro_dialog = gui.Dlg(title="Experiment Info", pos=(100, 100))
    intro_dialog.addField('PID:')
    intro_dialog.addField('Hearing:', choices=["yes", "no"])
    intro_dialog.show()

    if not intro_dialog.OK:
        teardown()

    pid = intro_dialog.data[0]
    hearing = True if intro_dialog.data[1] == "yes" else False

    count_signs = 0 if hearing else 36
    count_words = 4 if hearing else 0
    phases = generate_experiment(data, count_words, count_signs)

    show_message(
        "Welcome! Thank you for taking part in this experiment. It should take no more than 30 minutes. Press any key to continue.")
    show_message(
        f"You will now see {(str(count_signs) + ' novel signs') if count_signs else ''}{' and ' if count_signs and count_words else ''}{(str(count_words) + ' novel words') if count_words else ''}. {'Each sign will be shown twice. ' if count_signs else ''}Try to remember as many as possible. Press any key to begin.")

    random.shuffle(phases)
    for phase in phases:
        phase.show()

    show_message(
        f"You have now seen all the novel {'signs' if count_signs else ''}{' and ' if count_signs and count_words else ''}{'words' if count_words else ''} once. You will see them once more. Feel free to take a short break. Press any key to continue.")

    random.shuffle(phases)
    for phase in phases:
        phase.show()

    show_message(
        f"In the next stage you will see all the novel {'signs' if count_signs else ''}{' and ' if count_signs and count_words else ''}{'words' if count_words else ''} again and be asked to recall their meaning. Type in your answer using the keyboard and press enter when finished. Press any key to begin.")

    data = []

    random.shuffle(phases)
    for phase in phases:
        result = phase.test()
        data.append((phase.meaning, phase.stimulus, result))

    with open(app_folder(f"{pid}-output.csv"), "w") as out:
        csv_out = csv.writer(out)
        for row in data:
            csv_out.writerow(row)

    show_message("Congratulations, you have completed the experiment. Thank you for your contribution.",
                 wait_for_input=False)
