This repo hosts the experiment designed for the MSc dissertation of
Harriet Drinkald in developmental linguistics at the University of
Edinburgh. The (working) title of the paper is "The Acquisition of Novel
Words and Signs Across Modalities: the Impact of Phonetic Complexity."

To get started, create a file called `input.csv` containing comma
separated values with the format `meaning,word,video`. The
experiment then uses that file to test participants recall of meanings
based on whether they are given a word or short video to associate with
it. Videos are expected in the `video` folder in the root of the project.

Example:

meaning | word   | video
------- | ------ | ---------
ball    | freugh | ball.mp4
book    | jance  | book.mp4
cat     | breit  | cat.mp4
chair   | doile  | chair.mp4

In the context of the dissertation, the experiment is used to determine
whether participants find it more difficult to recall
meanings associated with stimulus presented in a modality different than
that of their L1 (first language). Non-hearing participants are given
novel signs as a control, while hearing participants are given a
mixture of novel words and signs and the two are compared.

The project is written for python 3.6, and relies only on psychopy.

- `python -m venv venv` - create a virtual environment
- `source venv/bin/activate` - use the virtual environment
- `pip install -r requirements.txt` - install the requirements
- `./run.py` - start the experiment

Experiment designed by Harriet Drinkald. Experiment written by Alexander Lyon
and Harriet Drinkald.