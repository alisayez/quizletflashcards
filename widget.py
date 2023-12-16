# This Python file uses the following encoding: utf-8
import sys
import calendar
import time

from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import requests

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *

from PySide6.QtWidgets import QApplication, QProgressBar, QCheckBox, QWidget, QComboBox, QListWidget, QLineEdit, QGroupBox, QPushButton, QTextEdit, QGridLayout, QStyle, QVBoxLayout, QHBoxLayout,QFileDialog, QDialog, QLabel
from PySide6 import QtCore
from PySide6.QtGui import QIcon, QFont


import ebooklib
from ebooklib import epub

import warnings
warnings.filterwarnings("ignore")

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setWindowTitle('Quizlet Flashcards Maker')
        self.setFixedSize(400,450)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.fileName = QLineEdit()
        self.fileName.setReadOnly(True)

        #upload, select chapter and output
        self.upload_button = QPushButton('&Upload File', clicked=self.readEpub)
        self.chapter_button = QPushButton('&Select Chapter', clicked=self.selectChapter)
        self.chapter_button.setEnabled(False)
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        #level
        self.level = QComboBox()
        self.level.addItem("Show all words")
        self.level.addItem("A1 Beginner")
        self.level.addItem("A2 Elementary")
        self.level.addItem("B1 Intermediate")
        self.level.addItem("B2 Upper-Intermediate")
        self.level.addItem("C1 Advanced")
        self.level.addItem("C2 Proficiency")
        self.level.setCurrentIndex(3)
        #first dictionary
        c1_h_layout1 = QHBoxLayout()
        self.labelOxford = QLabel("Oxford Learner's Dictionaries")
        self.checkOxford = QCheckBox()
        self.checkOxford.setChecked(True)
        self.checkOxford.setEnabled(False)
        c1_h_layout1.addWidget(self.labelOxford, 8)
        c1_h_layout1.addWidget(self.checkOxford, 2)
        #second dictionary
        c2_h_layout1 = QHBoxLayout()
        self.labelFDA = QLabel("Free Dictionary API")
        self.checkFDA = QCheckBox()
        self.checkFDA.setChecked(True)
        self.checkFDA.setEnabled(False)
        c2_h_layout1.addWidget(self.labelFDA, 8)
        c2_h_layout1.addWidget(self.checkFDA, 2)

        #groupbox
        self.settings_groupbox = QGroupBox("Levels and Dictionaries")
        groupbox_vbox = QVBoxLayout()
        self.settings_groupbox.setLayout(groupbox_vbox)
        groupbox_vbox.addWidget(self.level)
        groupbox_vbox.addLayout(c1_h_layout1)
        groupbox_vbox.addLayout(c2_h_layout1)

        #generate button
        self.generate_button = QPushButton("Generate", clicked=self.generateFlashcards)
        self.generate_button.setEnabled(False)

        #qprogressbar
        global progress_bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        progress_bar.adjustSize()

        #creator label
        alisa = QLabel("Created by Alisa @ Своя кімната 2023 v1")
        alisa.setAlignment(QtCore.Qt.AlignCenter)
        alisa.setStyleSheet("QLabel { color : grey; }")
        alisa.setFont(QFont('Times', 7))

        #layout
        layout.addWidget(self.upload_button)
        layout.addWidget(self.fileName)
        layout.addWidget(self.chapter_button)
        layout.addWidget(self.output)
        layout.addWidget(self.settings_groupbox)
        layout.addWidget(progress_bar)
        layout.addWidget(self.generate_button)
        layout.addWidget(alisa)

        global qicon
        qicon = QIcon('dictionaries/quizlet.png')
        self.setWindowIcon(qicon)


    def readEpub(self):
        file_name = ''
        file_name, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open an EPUB file",
                    filter='EPUB file (*.epub)')
        print(file_name)
        if file_name != '':
            self.fileName.setText(file_name)
            try:
                book = epub.read_epub(file_name)
                chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                global texts
                global titles
                global book_title
                book_title = book.get_metadata('DC', 'title')[0][0]
                #print('book_title')
                #print(book_title)
                texts = {}
                titles = {}
                for c in chapters:
                    texts[c.get_name()], titles[c.get_name()] = chapter_to_str(c)
            except:
                self.fileName.setText('Try a different EPUB file')
                fail = QDialog()
                pixmapi = QStyle.StandardPixmap.SP_MessageBoxCritical
                fail_icon = self.style().standardIcon(pixmapi)
                fail.setWindowIcon(fail_icon)
                fail.setFixedSize(200,100)
                fail.setWindowTitle('Error Message')
                fail_layout = QGridLayout();
                textFail = QLabel('This file is unreadable.', fail)
                fail_layout.addWidget(textFail, 0,0,0,0, QtCore.Qt.AlignCenter)
                fail.setLayout(fail_layout)
                fail.exec()
            else:
                self.chapter_button.setEnabled(True)
                #print(book.get_metadata('DC', 'title'))
    def selectChapter(self):
        global texts
        global qicon
        ch_v_layout = QVBoxLayout()
        ch_h_layout = QHBoxLayout()
        global select_chapter
        select_chapter = QDialog()
        select_chapter.setWindowTitle('Select a chapter')
        select_chapter.setWindowIcon(qicon)
        global chapter_list
        chapter_list = QListWidget()
        global show_chapter
        show_chapter = QTextEdit()
        sc_button = QPushButton('Select', clicked=self.setChapterIndex)
        select_chapter.setFixedSize(700,500)
        ch_h_layout.addWidget(chapter_list,4)
        ch_h_layout.addWidget(show_chapter,7)
        ch_v_layout.addLayout(ch_h_layout)
        ch_v_layout.addWidget(sc_button)
        select_chapter.setLayout(ch_v_layout)
        for i in texts:
            if texts[i] != '':
                chapter_list.addItem(i)
        chapter_list.itemSelectionChanged.connect(self.selectionChanged)
        select_chapter.exec()
        #print('select')
        #print(book.get_metadata('DC', 'title'))
    def selectionChanged(self):
        global texts
        global chapter_list
        #print('chapter selected')
        global chapter_index
        global string_show_chapter
        string_show_chapter = ''
        chapter_index = chapter_list.currentItem().text()
        for l in titles[chapter_index]:
            if l !='':
                string_show_chapter = string_show_chapter + str(l) +'\n'
        string_show_chapter = string_show_chapter + str(texts[chapter_index])
        show_chapter.setText(string_show_chapter)
        show_chapter.setReadOnly(True)
        #show_chapter.setText(texts[chapter_list.text()])
    def setChapterIndex(self):
        global select_chapter
        global chapter_index
        global selected_chapter
        global string_show_chapter
        selected_chapter = texts[chapter_index]
        #print('final chapter selected')
        self.output.setText(string_show_chapter)
        self.generate_button.setEnabled(True)
        select_chapter.close()
    def generateFlashcards(self):

        #check connection status if fda selected
        fda_status = internet_connection()

        if fda_status == False:
            fail_fda = QDialog()
            pixmapi = QStyle.StandardPixmap.SP_MessageBoxCritical
            fail_icon = self.style().standardIcon(pixmapi)
            fail_fda.setWindowIcon(fail_icon)
            fail_fda.setFixedSize(250,150)
            fail_fda.setWindowTitle('Error Message')
            fail_fda_layout = QGridLayout();
            text_fail_fda = QLabel('You don\'t have internet connection.\n\nOr the FDA server is down.\n\nTry again later.', fail_fda)
            fail_fda_layout.addWidget(text_fail_fda, 0,0,0,0, QtCore.Qt.AlignCenter)
            fail_fda.setLayout(fail_fda_layout)
            fail_fda.exec()
        else:
            global cefr_level
            cefr_level = self.level.currentIndex()
            string_level = self.level.currentText()
            global selected_chapter

            fetched_df = create_words_to_learn(selected_chapter)
            progress_bar.setValue(100)
            fetched_length = len(fetched_df)

            success = QDialog()
            if fetched_length > 0:
                global book_title
                global chapter_index
                current_GMT = time.gmtime()
                ts = calendar.timegm(current_GMT)
                txt_name = 'Quizlet ' + book_title + ' ' + chapter_index + ' ' + string_level + ' ' + str(ts) + '.txt'
                char_remov = ["\\", "/", "\:", "*", "?", "<", ">", "|"]
                for char in char_remov:
                    # replace() "returns" an altered string
                    txt_name = txt_name.replace(char, "")
                #print('TXT_NAME')
                #print(txt_name)
                fetched_df.to_csv(txt_name,sep='\t', index=False, header=False)

                pixmapi = QStyle.StandardPixmap.SP_DialogApplyButton
                success.setWindowTitle('Success!')
                textSuccess = QLabel('Quizlet Flashcards are generated!', success)
            else:
                pixmapi = QStyle.StandardPixmap.SP_MessageBoxWarning
                success.setWindowTitle('Oops!')
                textSuccess = QLabel('This chapter is so short!\n\nNothing to generate.', success)


            success_icon = self.style().standardIcon(pixmapi)
            success.setWindowIcon(success_icon)
            success.setFixedSize(250,200)
            success_layout = QGridLayout();
            success_layout.addWidget(textSuccess, 0,0,0,0, QtCore.Qt.AlignCenter)
            success.setLayout(success_layout)
            success.exec()

        #... prevent extra load on a server
        #self.generate_button.setEnabled(False)


def create_words_to_learn(chapter):
    chapter = re.sub(r'(?<=[^a-zA-Z\s-])(?=[^\s])', r' ', chapter)
    word_tokenized = word_tokenize(chapter)
    stop_words = set(stopwords.words("english"))
    filtered_list = []
    for word in word_tokenized:
        if word.casefold() not in stop_words and word.casefold() not in filtered_list and word.count('-') < 3 and len(word)>2 and word:
            if word.casefold().isalpha() or re.findall(r'\w+(?:-\w+)+',word):
                #print(word)
                filtered_list.append(word.lower())

    filt_list=[]
    [filt_list.append(x) for x in filtered_list if x not in filt_list]
    lemmatizer = WordNetLemmatizer()
    #read csv files
    a1 = pd.read_csv("dictionaries/a1_cleaned.csv")
    a2 = pd.read_csv("dictionaries/a2_cleaned.csv")
    b1 = pd.read_csv("dictionaries/b1_cleaned.csv")
    b2 = pd.read_csv("dictionaries/b2_cleaned.csv")
    c1 = pd.read_csv("dictionaries/c1_final.csv")
    c2 = pd.read_csv("dictionaries/c2_final.csv")
    extra = pd.read_csv("dictionaries/extra.csv")
    def set_level(level):
        exclude_df = pd.DataFrame(columns=['english', 'tag', 'definition'])
        oxford_df = pd.DataFrame(columns=['english', 'tag', 'definition'])
        if level == 0:
            oxford_df = pd.concat([a1,a2,b1,b2,c1,c2])
        elif level == 1:
            exclude_df = a1
            oxford_df = pd.concat([a2,b1,b2,c1,c2])
        elif level == 2:
            exclude_df = pd.concat([a1,a2])
            oxford_df = pd.concat([b1,b2,c1,c2])
        elif level == 3:
            exclude_df = pd.concat([a1,a2,b1])
            oxford_df = pd.concat([b2,c1,c2])
        elif level == 4:
            exclude_df = pd.concat([a1,a2,b1,b2])
            oxford_df = pd.concat([c1,c2])
        elif level == 5:
            exclude_df = pd.concat([a1,a2,b1,b2,c1])
            oxford_df = c2
        elif level == 6:
            exclude_df = pd.concat([a1,a2,b1,b2,c1,c2])
        exclude_df = exclude_df.sort_values('english')
        exclude_df = exclude_df.reset_index(drop=True)
        oxford_df = pd.concat([oxford_df, extra])
        oxford_df = oxford_df.sort_values('english')
        oxford_df = oxford_df.reset_index(drop=True)
        return exclude_df, oxford_df
    global cefr_level
    exclude_df, oxford_df = set_level(cefr_level)
    #print(len(exclude_df))
    #print(len(oxford_df))
    lemmatized_words = []
    for i in range(len(filt_list)):
        word = filt_list[i]
        lemma = lemmatizer.lemmatize(word)
        lemma = lemmatizer.lemmatize(lemma, 'v')
        lemma = lemmatizer.lemmatize(lemma, 'r')
        lemma = lemmatizer.lemmatize(lemma, 'a')
        lemmatized_words.append(lemma)
    filt_lemmatized=[]
    [filt_lemmatized.append(x) for x in lemmatized_words if x not in filt_lemmatized]
    plurals = pd.read_csv("dictionaries/plurals.csv")
    for i in range(len(filt_lemmatized)):
        if filt_lemmatized[i] in plurals['plural'].values:
            index = plurals[plurals['plural'] == filt_lemmatized[i]].index
            filt_lemmatized[i] = plurals.loc[index]['singular'].tolist()[0]
        if filt_lemmatized[i][-1:] == '-':
            filt_lemmatized[i] = filt_lemmatized[i][:-1]

    status = []
    definitions = []
    excluded_values = exclude_df['english'].tolist()
    oxford_values = oxford_df['english'].tolist()
    def check_word_status(excluded_values, oxford_values, word):
        status = -1
        if word in excluded_values:
            #print('found in exclude_df')
            status_found = 0
            definition_found = ''
        else:
            if word in oxford_values:
                #print('found in oxford')
                definition_found = oxford_df[oxford_df['english'] == word]['definition'].values[0]
                status_found = 1
            else:
                #print('have to use fda')
                definition_found = ''
                status_found = 2
        return status_found, definition_found

    for i in range(len(filt_lemmatized)):
        status_found = -1
        word = filt_lemmatized[i].lower()
        definition_found = ''
        status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
        if status_found == 2:
            #adverbs
            if word[-3:] == 'ily':
                word = word[:-3] +'y'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-7:] == 'therapy':
                word = word[:-7]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-9:] == 'therapist':
                word = word[:-3] + 'y'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word[:-9]
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-9:] == 'logist':
                word = word[:-3] + 'y'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-6:] == 'ically':
                word = word[:-4]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-5:] == 'apist':
                word = word[:-5] +'y'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word == 'publicly':
                word = 'public'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-3:] == 'ity':
                word = word[:-3]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word[:-3] + 'e'
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-4:] == 'ably' or word[-4:] == 'ibly':
                word = word[:-1] + 'e'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'ly':
                word = word[:-2]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word + 'le'
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-4:] == 'like':
                word = word[:-4]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'ze':
                word = word[:-2] + 'se'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'se':
                word = word[:-2] + 'ze'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-4:] == 'ment':
                word = word[:-4]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-3:] == 'ion':
                word = word[:-3]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word[:-3] + 'e'
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'or' or word[-2:] == 'er':
                word = word[:-2]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word[:-2] + 'e'
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-3:] == 'ant' or word[-3:] == 'ent':
                word = word[:-3]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-4:] == 'ness':
                word = word[:-4]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-3:] == 'ism':
                word = word[:-3]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-4:] == 'ship':
                word = word[:-4]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'ee':
                word = word[:-2]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
                if status_found == 2:
                    word = word[:-2] + 'e'
                    status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-2:] == 'cy':
                word = word[:-2] + 't'
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)
            elif word[-1:] == 'y':
                word = word[:-1]
                status_found, definition_found = check_word_status(excluded_values, oxford_values, word)

        if status_found == 0 or status_found == 1:
            filt_lemmatized[i] = word
        status.append(status_found)
        definitions.append(definition_found)
    f_indices = []
    for i in range(len(status)):
        if status[i] == 2:
            f_indices.append(i)
    words_fda = []
    words_fda_oi = []
    for i in f_indices:
        words_fda.append(filt_lemmatized[i])
        words_fda_oi.append(i)
    stemmer = PorterStemmer()
    stems_dict = [stemmer.stem(word) for word in words_fda]
    stems_words = [stemmer.stem(str(word)) for word in exclude_df['english'].values]
    stems_words_fda = []
    stems_indeces_fda = []
    for i in range(len(stems_dict)):
        if stems_dict[i] not in stems_words:
            stems_words_fda.append(stems_dict[i])
            stems_indeces_fda.append(words_fda_oi[i])
    global count_fda_words
    count_fda_words = len(words_fda)
    step = round(count_fda_words/100)
    def get_word_API(word):
        i = 1
        url_string = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        response_API = requests.get(url_string + word)
        data = response_API.text
        parse_json = json.loads(data)
        definitions = ''
        if type(parse_json) == list:
            for p in parse_json:
                for m in p['meanings']:
                    for d in m['definitions']:
                        definition = d['definition']
                        definition = definition[0].lower() + definition[1:]
                        if len(d) > 1:
                            definitions = definitions + str(i) +'. ' + definition + ' '
                            i = i + 1
        else:
            definitions = 'NF'
        while(definitions[-1:] == ' '):
            definitions = definitions[:-1]
        if '2.' not in definitions:
            definitions = definitions[3:]
        return definitions
    definitions_api = []

    if len(stems_indeces_fda) > 0:
        cc = 0
        steps = 0
        step = 100/len(stems_indeces_fda)
        print('Words to look up:' + str(len(stems_indeces_fda)))
        global progress_bar
        for i in stems_indeces_fda:
            print('Looking up a word ' + str(cc+1))
            definitions_api.append(get_word_API(filt_lemmatized[i]))
            progress_bar.setValue(round(steps))
            if cc >0:
                steps = cc*step
            cc = cc + 1
            if cc == len(stems_indeces_fda):
                progress_bar.setValue(99)
        j = 0
        for ind in stems_indeces_fda:
            definitions[ind] = definitions_api[j]
            j +=1

    final_words = []
    final_defs = []
    for i in range(len(status)):
        if status[i] != 0:
            final_words.append(filt_lemmatized[i])
            final_defs.append(definitions[i])
    for i in range(len(final_defs)):
        if type(final_defs[i]) != float:
            if '4.' in final_defs[i] :
                index = [m.start() for m in re.finditer('4.', final_defs[i])]
                final_defs[i] = final_defs[i][:index[0]-1]

    dict = {'english': final_words, 'definition': final_defs}
    words = pd.DataFrame(dict)
    words = words[words['definition'] != '']
    return words



def chapter_to_str(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    text = ''.join(text)
    title = [para.get_text() for para in soup.find_all(['h1', 'h2', 'h3'])]
    return text,title

def internet_connection():
    try:
        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/hello", timeout=5)
        return True
    except requests.ConnectionError:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
