# quizletflashcards
This project uses various Python libraries and PyQt6 for a programme that creates a txt file for mass import of flashcards to Quizlet.

Programme flow:
1. Parse an epub file using Python NLTK library to transform all words to their basic forms
2. Use only words that are above the level which was selected by a user
3. Create a txt file ready for import

The dabase of dictionaries is created using webscraping on Oxford Learner's Dictionaries and using Free Dictionary API.

You can build it up to an exe file using Auto PY to EXE https://pypi.org/project/auto-py-to-exe/.

You can also extend your built-in dictionary database using webscraping via an existing Jupyter Notebook or adapting it to your needs.



