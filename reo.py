#!/usr/bin/env python3
#
# Could use just '#!/usr/bin/env python' if you're NOT on Ubuntu or any other
# distribution that has python2 as the main python version. But it has to be
# run through Python 3, not Python 2.
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Mufeed Ali
# This file is part of Reo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Mufeed Ali
#
# Now, beginning with the Imports.
import sys
import logging
import argparse  # for CommandLine-Interface (CLI).
import re  # regular expressions
import os
from os.path import expanduser  # for detecting home folder
from shutil import which  # for checks.
import subprocess  # for running dict and others in background
import random  # for Random Words
import linecache
from pathlib import Path
import threading
# logging is the most important. You have to let users know everything.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - " +
                    "[%(levelname)s] [%(threadName)s] (%(module)s:" +
                    "%(lineno)d) %(message)s")

# Readying ArgParser
parser = argparse.ArgumentParser()  # declare parser as the ArgumentParser used
mgroup = parser.add_mutually_exclusive_group()
mgroup.add_argument("-c", "--check", action="store_true",
                    help="Basic dependancy checks.")
mgroup.add_argument("-d", "--adversion", action="store_true",
                    help="Advanced Version Info")
mgroup.add_argument("-gd", "--dark", action="store_true",
                    help="Use GNOME dark theme")
mgroup.add_argument("-gl", "--light", action="store_true",
                    help="Use GNOME light theme")
parser.add_argument("-g", "--gladefile", type=str,
                    help="set custom GLADEFILE (file from which UI is taken" +
                    ", useful for testing custom UIs)")
parsed = parser.parse_args()
try:
    import gi  # this is the GObject stuff needed for GTK+
    gi.require_version('Gtk', '3.0')  # inform the PC that we need GTK+ 3.
    import gi.repository.Gtk as Gtk  # this is the GNOME depends
    if parsed.check:
        sys.exit()
except ImportError as ierr:
    logging.fatal("Importing GObject failed!")
    if not parsed.check:
        print("Confirm all dependencies by running " +
              "Reo with '--check' parameter.\n" +
              ierr)
        sys.exit(1)
    elif parsed.check:
        print("Install GObject bindings.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install python3-gobject'\n" +
              "From extra repo for Arch Linux:\n" +
              "'pacaur -S python-gobject' or 'sudo pacman -S python-gobject'" +
              "\nThanks for trying this out!")
builder = Gtk.Builder()


def darker():
    global dark
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", True)
    dark = True


def lighter():
    global dark
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", False)
    dark = False


def addbuilder():
    PATH = os.path.dirname(os.path.realpath(__file__))
    if parsed.gladefile:
        GLADEFILE = parsed.gladefile
    else:
        # GLADEFILE points to the location of the UI file.
        GLADEFILE = PATH + "/reo.ui"
    builder.add_from_file(GLADEFILE)


def windowcall():
    window = builder.get_object('window')  # main window
    window.show_all()


if not parsed.adversion and not parsed.check:
    if Gtk.Settings.get_default().get_property("gtk-application-prefer" +
                                               "-dark-theme"):
        dark = True
    else:
        dark = False
    if parsed.dark:
        darker()
    elif parsed.light:
        lighter()
    addbuilder()
    windowcall()

wnver = '3.1'
wncheckonce = False


def wncheck():
    global wnver, wncheckonce
    if not wncheckonce:
        try:
            check = subprocess.Popen(["dict", "-d", "wn", "test"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            checkt = check.stdout.read().decode()
        except Exception as ex:
            print("Error with dict. Error")
            print(ex)
        if not checkt.find('1 definition found\n\nFrom WordNet (r)' +
                           ' 3.1 (2011) [wn]:\n') == -1:
            wnver = '3.1'
        elif not checkt.find('1 definition found\n\nFrom WordNet (r)' +
                             ' 3.0 (2006) [wn]:\n') == -1:
            wnver = '3.0'
        wncheckonce = True


def adv():
    print('Reo 0.0.6 Alpha version')
    print('Copyright 2016-2019 Mufeed Ali')
    print()
    wncheck()
    if wnver == '3.1':
        print("WordNet Version 3.1 (2011) (Installed)")
    elif wnver == '3.0':
        print("WordNet Version 3.0 (2006) (Installed)")
    try:
        check2 = subprocess.Popen(["dict", "-V"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        check2t = check2.stdout.read().decode()
        print("Dict Version Info:\n" +
              check2t.strip())
    except Exception as ex:
        print("Looks like missing components. (dict)\n" + str(ex))
    print()
    try:
        check3 = subprocess.Popen(["espeak", "--version"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        check3t = check3.stdout.read().decode()
        print("eSpeak Version Info:\n" +
              check3t.strip())
    except Exception as ex:
        print("You're missing a few components. (espeak)\n" + str(ex))
    sys.exit()


def CheckBin(bintocheck):
    try:
        which(bintocheck)
        print(bintocheck + " seems to be installed. OK.")
        bincheck = True
    except Exception as ex:
        logging.fatal(bintocheck + " is not installed! Dependancy missing!" +
                      str(ex))
        bincheck = False
    return bincheck


def PrintChecks(espeak, dict, dictd, wndict):
    if (espeak and dict and dictd and wndict):
        print("Everything Looks Perfect!\n" +
              "You should be able to run it without any issues!")
    elif (espeak and dict and dictd and not wndict):
        print("WordNet's data file is missing. Re-install 'dict-wn'.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S dict-wn'\n" +
              "Everything else (NOT everything) looks fine...\n" +
              "... BUT you can't run it.")
    elif (espeak and not dict and not dictd and not wndict):
        print("dict and dictd (client and server) are missing.. install it." +
              "\nFor Ubuntu, Debian, etc:\n" +
              "'sudo apt install dictd dict-wn'\n" +
              "From community repo for Arch Linux (but WordNet from AUR):\n" +
              "'pacaur -S dictd dict-wn'\n" +
              "That should point you in the right direction to getting \n" +
              "it to work.")
    elif (not espeak and not dict and not dictd and not wndict):
        print("ALL bits and pieces are Missing...\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak dictd dict-wn'\n" +
              "From community repo for Arch Linux (but WordNet from AUR):\n" +
              "'pacaur -S espeak dictd dict-wn'\n" +
              "Go on, get it working now!")
    elif (not espeak and dict and dictd and wndict):
        print("Everything except eSpeak is working...\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak'\n" +
              "From community repo for Arch Linux:\n" +
              "'pacaur -S espeak' or 'sudo pacman -S espeak'\n" +
              "It should be alright then.")
    elif (not espeak and dict and dictd and wndict):
        print("eSpeak is missing and WordNet might not work as intended.\n" +
              "Install 'espeak' and re-install the 'dict-wn' package.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S espeak dict-wn'\n" +
              "Everything else (NOT everything) looks fine.\n" +
              "Go on, try and run it!")
    elif (not espeak and dict and dictd and not wndict):
        print("eSpeak is missing and WordNet's data file is missing." +
              "Re-install 'dict-wn'.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S espeak dict-wn'\n" +
              "Everything else (NOT everything) looks" +
              " fine BUT you can't run it.")


def syscheck():
    espeak = CheckBin('espeak')
    dict = CheckBin('dict')
    dictd = CheckBin('dictd')
    try:
        open('/usr/share/dictd/wn.dict.dz')
        print('WordNet databse seems to be installed. OK.')
        wndict = True
    except Exception as ex:
        logging.warning("WordNet database is not found! Probably won't work." +
                        "\n" + str(ex))
        wndict = False
    PrintChecks(espeak, dict, dictd, wndict)
    sys.exit()


if parsed.adversion:
    adv()
if parsed.check:
    syscheck()
homefold = expanduser('~')  # Find the location of the home folder of the user
reofold = homefold + "/.reo"
# ^ This is where stuff like settings, Custom Definitions, etc will go.
cdefold = reofold + "/cdef"
# ^ The Folder within reofold where Custom Definitions are to be kept.
if not os.path.exists(reofold):  # check for Reo folder
    os.makedirs(reofold)  # create Reo folder
if not os.path.exists(cdefold):  # check for Custom Definitions folder.
    os.makedirs(cdefold)  # create Custom Definitions folder.


class GUI:

    def on_window_destroy(self, window):
        linecache.clearcache()
        Gtk.main_quit()

    def icon_press(self, imagemenuitem4):
        about = builder.get_object('aboutReo')
        print("Loading About Window.")
        response = about.run()
        print("Done")
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.CANCEL):
            about.hide()

    def sst(self, imagemenuitem1):
        sb = builder.get_object('searchEntry')  # Search box
        viewer = builder.get_object('defView')  # Data Space
        try:
            dec, dek = viewer.get_buffer().get_selection_bounds()
            text = viewer.get_buffer().get_text(dec, dek, True)
            text = text.replace('-\n         ', '-').replace('\n', ' ')
            text = text.replace('         ', '')
            sb.set_text(text)
            if not text == '' and not text.isspace():
                self.searchClick()
                sb.grab_focus()
        except Exception as ex:
            logging.error("Searching selected text failed\n" + str(ex))
            return

    def newced(self, title, primary, secondary):
        cept = builder.get_object('cept')
        cest = builder.get_object('cest')
        ced = builder.get_object('ced')
        ced.set_title(title)
        cept.set_label(primary)
        cest.set_label(secondary)
        response = ced.run()
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.OK):
            ced.hide()

    def fortune(self):
        try:
            fortune = subprocess.Popen(["fortune", "-a"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            fortune.wait()
            ft = fortune.stdout.read().decode()
            return ft
        except Exception as ex:
            ft = "Easter Egg Fail!!! Install 'fortune' or 'fortunemod'."
            print(ft + "\n" + str(ex))
            return ft

    def cowfortune(self):
        try:
            cowsay = subprocess.Popen(["cowsay", self.fortune()],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            cowsay.wait()
            if cowsay:
                cst = cowsay.stdout.read().decode()
            return cst
        except Exception as ex:
            ft = ("Easter Egg Fail!!! Install 'fortune' or 'fortunemod'" +
                  " and also 'cowsay'.")
            print(ft + "\n" + str(ex))
            return ft

    def searchClick(self, searchButton=None):
        sb = builder.get_object('searchEntry')  # searchbox
        viewer = builder.get_object('defView')  # Data Space
        if viewer.get_monospace():
            viewer.set_monospace(False)
        viewer.get_buffer().set_text("")
        lastiter = viewer.get_buffer().get_end_iter()
        text = sb.get_text().strip().strip('<>"?`![]()/\\:;,')
        try:
            out = self.search(sb.get_text())
            if text == 'fortune -a' and text == 'cowfortune':
                viewer.set_monospace(True)
                viewer.get_buffer().insert(lastiter, out, -1)
            elif text == 'reo':
                viewer.set_monospace(True)
                viewer.get_buffer().insert_markup(lastiter, out, -1)
            else:
                viewer.get_buffer().insert_markup(lastiter, out, -1)
        except Exception as ex:
            print("Didn't work." + str(ex))

    def search(self, sb):
        if (not sb.strip('<>"?`![]()/\\:;,') == '' and
                not sb.isspace() and not sb == ''):
            text = sb.strip().strip('<>"?`![]()/\\:;,')
            return self.reactor(text)
        elif (sb.strip('<>"?`![]()/\\:;,') == '' and
              not sb.isspace() and
              not sb == ''):
            logging.error("Invalid Characters.")
            self.newced('Error: Invalid Input!', 'Invalid Characters!',
                        "Reo thinks that your input was actually \nju" +
                        "st a bunch of useless characters. \nSo, 'Inva" +
                        "lid Characters' error!")
        elif sb.isspace():
            logging.error("Empty search box!")
            self.newced("Umm..?", "Umm..?", "Reo can't find any text" +
                        " there! You sure \nyou typed something?")
        elif sb == '':
            logging.error("Empty search box!")
            self.newced("Umm..?", "Umm..?", "Reo can't find any text" +
                        " there! You sure \nyou typed something?")

    def reactor(self, text):
        global searched
        if dark:
            sencol = "cyan"  # Color of sentences in Dark mode
            wordcol = "lightgreen"  # Color of: Similar Words,
#                                     Synonyms and Antonyms.
        else:
            sencol = "blue"  # Color of sentences in regular
            wordcol = "green"  # Color of: Similar Words,
#                                Synonyms and Antonyms.
        if text == 'fortune -a':
            return self.fortune()
        elif text == 'cowfortune':
            return self.cowfortune()
        elif text == 'crash now' or text == 'close now':
            Gtk.main_quit()
        elif text == 'reo':
            reodef = str("Pronunciation: <b>/ɹˈiːəʊ/</b>\n  <b>Reo</b>" +
                         " ~ <i>Japanese Word</i>\n  <b>1:</b> Name o" +
                         "f this application, chosen kind of at rando" +
                         "m.\n  <b>2:</b> Japanese word meaning 'Wise" +
                         " Center'\n <b>Similar Words:</b>\n <i><" +
                         "span foreground=\"" + wordcol + "\">  ro, " +
                         "re, roe, redo, reno, oreo, ceo, leo, neo, " +
                         "rho, rio, reb, red, ref, rem, rep, res," +
                         " ret, rev, rex</span></i>")
            return reodef
        if text and not text.isspace():
            searched = True
            return self.generator(text, wordcol, sencol)

    def cdef(self, text, wordcol, sencol):
        with open(cdefold + '/' + text, 'r') as cdfile:
            cdefread = cdfile.read()
            cdefread = cdefread.replace("<i>($WORDCOL)</i>", wordcol)
            cdefread = cdefread.replace("<i>($SENCOL)</i>", sencol)
            cdefread = cdefread.replace("($WORDCOL)", wordcol)
            cdefread = cdefread.replace("($SENCOL)", sencol)
            cdefread = cdefread.replace("$WORDCOL", wordcol)
            cdefread = cdefread.replace("$SENCOL", sencol)
            if "\n[warninghide]" in cdefread:
                cdefread = cdefread.replace("\n[warninghide]", "")
                return cdefread
            else:
                return(cdefread + '\n<span foreground="#e6292f">N' +
                       'OTE: This is a Custom definition. No one' +
                       ' is to be held responsible for errors in' +
                       ' this.</span>')

    def defProcessor(self, proc, text, sencol, wordcol):
        soc = proc.replace('1 definition found\n\nFrom WordNet (r)' +
                           ' 3.0 (2006) [wn]:\n', '')
        soc = soc.replace('1 definition found\n\nFrom WordNet' +
                          ' (r) 3.1 (2011) [wn]:\n', '')
        try:
            imp = re.search("  " + text, soc,
                            flags=re.IGNORECASE).group(0)
        except Exception as ex:
            imp = ''
            logging.warning("Regex search failed" + str(ex))
        soc = soc.replace(imp + '\n', '')
        cleans = ['"--Thomas', '"--\n           ',
                  '-\n             ', '"; [', '      n 1',
                  '      v 1', '      adj 1', '      adv 1',
                  '\n          --',
                  '-\n           ', '-\n         ',
                  '\n           ', '\n             ',
                  '\n          ',
                  '\n           ', '           ',
                  '\n         ', '    ', '   ',
                  '[syn:', '}]', '[ant:', '"; "', '; "',
                  '"\n', '" <i>', '"- ', '", "',
                  '"<span foreground="' + sencol +
                  '"><span foreground="' + sencol +
                  '"><span foreground="' + sencol + '">',
                  '"<span foreground="' + sencol +
                  '"><span foreground="' +
                  sencol + '">', '(', ')',
                  '{', '}', ':"', '" \n      <',
                  '"; ', ', "', '; e.g. "', '"  <i>',
                  ';"', ';  "', ': "', ';   "', '"--',
                  '"-', '" -']
        cleaned = ['</span> - Thomas',
                   '</span> - ', '-', '</span> [', '<b>' + imp +
                   '</b> ~ <i>noun</i>:\n      1', '<b>' + imp +
                   '</b> ~ <i>verb</i>:\n      1',
                   '<b>' + imp + '</b> ~ <i>adjective</i>:\n    ' +
                   '  1', '<b>' + imp +
                   '</b> ~ <i>adverb</i>:\n      1',
                   '--', '-', '-', ' ', ' ', ' ',
                   '\n         ', '         ', ' ', '',
                   ' ', '<i>\n      Synonyms:',
                   '}</i>', '<i>\n      Antonyms:',
                   '</span>; <span foreground="' + sencol + '">',
                   '\n      <span foreground="' + sencol +
                   '">', '</span>\n', '</span> <i>', '</span> - ',
                   '</span>; <span foreground="' + sencol +
                   '">', '"<span foreground="' + sencol + '">',
                   '"<span foreground="' + sencol +
                   '">', '<i>(', ')</i>', '<span foreground="' +
                   wordcol + '">', '</span>',
                   '\n      <span foreground="' + sencol +
                   '">', '</span>; <',
                   '</span>; <span foreground="' + sencol + '">',
                   '\n      <span foreground="' + sencol +
                   '">', '\n      <span foreground="' +
                   sencol + '">', '</span><i>',
                   '\n      <span foreground="' + sencol +
                   '">', '\n      <span foreground="' +
                   sencol + '">',
                   '\n      <span foreground="' + sencol + '">',
                   '\n      <span foreground="' + sencol + '">',
                   '\n      <span foreground="' + sencol + '">',
                   '</span> - ', '</span> - ', '</span> - ']
        for x, y in zip(cleans, cleaned):
            soc = soc.replace(x, y)
        gsi = range(-100, 1)
        for si in gsi:
            soc = soc.replace(' ' + str(si).replace('-', '') +
                              ': ', ' <b>' +
                              str(si).replace('-', '') +
                              ': </b>')
        if not soc.find("`") == -1:
            soc = soc.replace("`", "'")
        if not soc.find("thunder started the sleeping") == -1:
            soc = soc.replace("thunder started the sleeping",
                              "thunder started, the sleeping")
        soc = soc.strip()
        return soc

    def clsfmt(self, clp, text):
        clp = clp.replace('wn:', '').rstrip()
        swbtw = re.compile("(.)  " + text.lower() + "  (.)")
        clp = swbtw.sub(r"\1  \2", clp)
        clp = clp.replace('\n  ', '  ').rstrip()
        clp = clp.replace("  " + text.lower() + "  ", "")
        clp = clp.replace("  " + '"' + text.lower() + '"' +
                          "  ", "")
        clp = clp.replace("  " + text.lower() + "  ", "")
        same_word = re.compile("  " + text.lower() + "$")
        same_term = re.compile('  "' + text.lower() +
                               '"' + "$")
        clp = same_word.sub("", clp)
        clp = same_term.sub("", clp)
        clp = clp.strip().replace("  ", ", ")
        return clp

    def dictdef(self, text, wordcol, sencol):
        strat = "lev"
        # ^ To change strategy used in 'Similar Words', change this value.
        try:
            prc = subprocess.Popen(["dict", "-d", "wn", text],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        except Exception as ex:
            print("Didnt Work! ERROR CODE: PAPAYA\n" + str(ex))
        try:
            pro = subprocess.Popen(["espeak", "-ven-uk-rp",
                                    "--ipa", "-q", text],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        except Exception as ex:
            print("Didnt Work! ERROR CODE: MANGO\n" + str(ex))
        try:
            clos = subprocess.Popen(["dict", "-m", "-d", "wn",
                                     "-s", strat, text],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except Exception as ex:
            print("Didnt Work! ERROR CODE: PAPAYA\n" + str(ex))
        prc.wait()
        try:
            proc = prc.stdout.read().decode()
            if not proc == '':
                soc = self.defProcessor(proc, text, sencol, wordcol)
                crip = 0
            else:
                soc = "Coundn't find definition for '" + text + "'."
                crip = 1
        except Exception as ex:
            print("Something went wrong while obtaining" +
                  " definitions.\n" + str(ex))
        if crip == 1:
            print("Failed")
        pro.wait()
        try:
            dcd = pro.stdout.read().decode()
            pron = " /" + dcd.strip().replace('\n ', ' ') + "/"
        except Exception as ex:
            pron = str('ERROR: Something went wrong' +
                       ' with pronunications.')
            print(ex)
        clos.wait()
        clp = clos.stdout.read().decode()
        fail = 0
        clp = self.clsfmt(clp, text)
        if clp == '':
            fail = 1
        if text == 'recursion':
            clp = 'recursion'
            fail = 0
        if pro and not crip == 1:
            pron = "Pronunciation: <b>" + pron + '</b>' + '\n'
        elif pro and crip == 1:
            pron = "Probable Pronunciation: <b>" + pron + '</b>\n'
        if fail == 0:
            cclp = clp.replace('\n  ', '  ')
            cleanclp = cclp.strip().replace('  ', ', ')
            if crip == 1:
                cleanclp = ('<b>Did you mean</b>:\n<i><span foreground="' +
                            wordcol + '">  ' + cleanclp + '</span></i>')
            else:
                cleanclp = ('<b>Similar Words</b>:\n' +
                            '<i><span foreground="' + wordcol + '">  ' +
                            cleanclp + '</span></i>')
        else:
            cleanclp = ""
        return pron.rstrip() + '\n' + soc + '\n' + cleanclp.strip()

    def generator(self, text, wordcol, sencol):
        try:
            return self.cdef(text, wordcol, sencol)
        except Exception:
            return self.dictdef(text, wordcol, sencol)

    def cedok(self, cedok):
        ced = builder.get_object('ced')
        ced.response(Gtk.ResponseType.OK)

    def randomword(self):
        try:
            wnver31 = Path(cdefold + "wnver31")
            if wnver31.is_file():
                return linecache.getline('wn3.1', random.randint(0, 147478))
            else:
                if wncheckonce:
                    return linecache.getline('wn' + wnver,
                                             random.randint(0, 147478))
                else:
                    return linecache.getline('wn3.1',
                                             random.randint(0, 147478))
                    threading.Thread(target=wncheck).start()
        except Exception as ex:
            logging.error("Random word search failed" + str(ex))

    def randword(self, mnurand):
        sb = builder.get_object('searchEntry')  # searchbox
        rw = self.randomword()
        sb.set_text(rw.strip())
        self.searchClick()
        sb.grab_focus()

    def clear(self, clearButton):
        sb = builder.get_object('searchEntry')  # searchbox
        viewer = builder.get_object('defView')  # Data Space
        sb.set_text("")
        viewer.get_buffer().set_text("")

    def audio(self, audioButton):
        sb = builder.get_object('searchEntry')  # searchbox
        speed = '120'  # To change eSpeak audio speed.
        if searched and not sb.get_text() == '':
            with open(os.devnull, 'w') as NULLMAKER:
                subprocess.Popen(["espeak", "-ven-uk-rp", "-s", speed,
                                  sb.get_text()], stdout=NULLMAKER,
                                 stderr=subprocess.STDOUT)
        elif sb.get_text() == '' or sb.get_text().isspace():
            self.newced("Umm..?", "Umm..?", "Reo can't find any text" +
                        " there! You sure \nyou typed something?")
        elif not searched:
            self.newced("Sorry!!", "Sorry!!",
                        "I'm sorry but you have to do a search" +
                        " first \nbefore trying to  listen to it." +
                        " I mean, Reo \nis <b>NOT</b> a Text-To" +
                        "-Speech Software!")

    def changed(self, searchEntry):
        sb = builder.get_object('searchEntry')  # searchbox
        global searched
        searched = False
        sb.set_text(sb.get_text().replace('\n', ' '))
        sb.set_text(sb.get_text().replace('         ', ''))

    def quitb(self, imagemenuitem10):
        Gtk.main_quit()

    def savedef(self, imagemenuitem2):
        defdiag = Gtk.FileChooserDialog("Save Definition as...",
                                        builder.get_object('window'),
                                        Gtk.FileChooserAction.SAVE,
                                        ("Save", Gtk.ResponseType.OK,
                                         "Cancel", Gtk.ResponseType.CANCEL))
        viewer = builder.get_object('defView')  # Data Space
        response = defdiag.run()
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.CANCEL):
            defdiag.hide()
        elif response == Gtk.ResponseType.OK:
            sf = open(defdiag.get_filename(), 'w')
            startiter = viewer.get_buffer().get_start_iter()
            lastiter = viewer.get_buffer().get_end_iter()
            sf.write(viewer.get_buffer().get_text(startiter,
                                                  lastiter,
                                                  'false'))
            sf.close()
            defdiag.hide()


builder.connect_signals(GUI())
Gtk.main()