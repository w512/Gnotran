#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Gnotran - simple Gnome client for Google Translate.

Features:
    1. Very simple and easy to use.
    2. Two windows for the concurrent translate.
    3. Convenient interface.

'''

__author__ = 'Nikolay Blohin (nikolay@blohin.org)'
__version__ = '0.5.4'
__copyright__ = 'Copyright (c) 2010 Nikolay Blohin'
__license__ = 'GNU General Public License'

import os
import json
import urllib
import threading
import gtk
import gconf


GCONF_PREF_DIR = '/apps/gnotran/preferences'

ABS_Path = os.path.realpath(os.path.dirname(__file__))
IMAGES_dir = os.path.join(ABS_Path, 'images')


class MainWindow(gtk.Window):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.all_lang = {
            'afrikaans':'af',
            'albanian':'sq',
            'amharic':'am',
            'arabic':'ar',
            'armenian':'hy',
            'azerbaijani':'az',
            'basque':'eu',
            'belarusian':'be',
            'bengali':'bn',
            'bihari':'bh',
            'bulgarian':'bg',
            'burmese':'my',
            'catalan':'ca',
            'cherokee':'chr',
            'chinese':'zh',
            'chinese_simplified':'zh-cn',
            'chinese_traditional':'zh-tw',
            'croatian':'hr',
            'czech':'cs',
            'danish':'da',
            'dhivehi':'dv',
            'dutch':'nl',
            'english':'en',
            'esperanto':'eo',
            'estonian':'et',
            'filipino':'tl',
            'finnish':'fi',
            'french':'fr',
            'galician':'gl',
            'georgian':'ka',
            'german':'de',
            'greek':'el',
            'guarani':'gn',
            'gujarati':'gu',
            'hebrew':'iw',
            'hindi':'hi',
            'hungarian':'hu',
            'icelandic':'is',
            'indonesian':'id',
            'inuktitut':'iu',
            'italian':'it',
            'japanese':'ja',
            'kannada':'kn',
            'kazakh':'kk',
            'khmer':'km',
            'korean':'ko',
            'kurdish':'ku',
            'kyrgyz':'ky',
            'laothian':'lo',
            'latvian':'lv',
            'lithuanian':'lt',
            'macedonian':'mk',
            'malay':'ms',
            'malayalam':'ml',
            'maltese':'mt',
            'marathi':'mr',
            'mongolian':'mn',
            'nepali':'ne',
            'norwegian':'no',
            'oriya':'or',
            'pashto':'ps',
            'persian':'fa',
            'polish':'pl',
            'portuguese':'pt-pt',
            'punjabi':'pa',
            'romanian':'ro',
            'russian':'ru',
            'sanskrit':'sa',
            'serbian':'sr',
            'sindhi':'sd',
            'sinhalese':'si',
            'slovak':'sk',
            'slovenian':'sl',
            'spanish':'es',
            'swahili':'sw',
            'swedish':'sv',
            'tajik':'tg',
            'tamil':'ta',
            'tagalog':'tl',
            'telugu':'te',
            'thai':'th',
            'tibetan':'bo',
            'turkish':'tr',
            'ukrainian':'uk',
            'urdu':'ur',
            'uzbek':'uz',
            'uighur':'ug',
            'vietnamese':'vi',
        }

        # Read config from GConf
        self.gconf_client = gconf.client_get_default()
        try:
            self.gconf_client.get_value(GCONF_PREF_DIR + '/lang_from')
        except:
            # first run, write default settings to gconf
            self.gconf_client.set_string(GCONF_PREF_DIR + '/lang_from', 'english')
            self.gconf_client.set_string(GCONF_PREF_DIR + '/lang_to', 'russian')
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/one_direction', False)
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/hide_toolbar', False)
        self.from_lang = self.gconf_client.get_value(GCONF_PREF_DIR + '/lang_from')
        self.to_lang = self.gconf_client.get_value(GCONF_PREF_DIR + '/lang_to')
        self.one_direction = self.gconf_client.get_value(GCONF_PREF_DIR + '/one_direction')
        self.hide_toolbar = self.gconf_client.get_value(GCONF_PREF_DIR + '/hide_toolbar')

        self.set_title('Gnotran - simple Gnome client for Google Translate')
        self.set_icon_from_file(os.path.join(IMAGES_dir, 'google-32x32.png'))
        self.set_default_size(650, 550)
        self.set_resizable(True)
        self.set_position(gtk.WIN_POS_CENTER)


        # text menu ***********************************************************

        # images for menubar
        img1 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'language-16x16.png'))
        image_1 = gtk.Image()
        image_1.set_from_pixbuf(img1)

        img2 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'about-16x16.png'))
        image_2 = gtk.Image()
        image_2.set_from_pixbuf(img2)


        # file menu
        filemenu = gtk.Menu()
        filem = gtk.MenuItem('_File')
        filem.set_submenu(filemenu)

        agr = gtk.AccelGroup()
        self.add_accel_group(agr)

        m_lang = gtk.ImageMenuItem('_Language', agr)
        m_lang.set_image(image_1)
        key, mod = gtk.accelerator_parse('<Control>L')
        m_lang.add_accelerator('activate', agr, key, mod, gtk.ACCEL_VISIBLE)
        m_lang.connect('activate', self.choice_lang)
        filemenu.append(m_lang)

        sep = gtk.SeparatorMenuItem()
        filemenu.append(sep)

        m_exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse('<Control>Q')
        m_exit.add_accelerator('activate', agr, key, mod, gtk.ACCEL_VISIBLE)
        m_exit.connect('activate', self.pr_exit)
        filemenu.append(m_exit)

        # edit menu
        editmenu = gtk.Menu()
        editm = gtk.MenuItem('_Edit')
        editm.set_submenu(editmenu)

        self.m_switch = gtk.CheckMenuItem('_One direction of translation')
        self.m_switch.set_active(self.one_direction)
        self.m_switch.connect('activate', self.one_two)
        editmenu.append(self.m_switch)

        self.m_toolbar = gtk.CheckMenuItem('_Hide toolbar')
        self.m_toolbar.set_active(self.hide_toolbar)
        self.m_toolbar.connect('activate', self.show_hide_toolbar)
        editmenu.append(self.m_toolbar)

        # about menu
        aboutmenu = gtk.Menu()
        aboutm = gtk.MenuItem('_Help')
        aboutm.set_submenu(aboutmenu)

        m_about = gtk.ImageMenuItem('_About', agr)
        m_about.set_image(image_2)
        key, mod = gtk.accelerator_parse('<Control>B')
        m_about.add_accelerator('activate', agr, key, mod, gtk.ACCEL_VISIBLE)
        m_about.connect('activate', self.about)
        aboutmenu.append(m_about)


        menubar = gtk.MenuBar()
        menubar.append(filem)
        menubar.append(editm)
        menubar.append(aboutm)
        # end text menu *******************************************************

        # left up
        textview1 = gtk.TextView()
        l_u_scroll = gtk.ScrolledWindow()
        l_u_scroll.add(textview1)
        l_u_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview1.set_wrap_mode(gtk.WRAP_WORD)
        textview1.set_border_width(5)
        textview1.set_left_margin(3)
        textview1.set_right_margin(3)
        self.l_u_buffer = textview1.get_buffer()

        # left down
        textview2 = gtk.TextView()
        l_d_scroll = gtk.ScrolledWindow()
        l_d_scroll.add(textview2)
        l_d_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview2.set_wrap_mode(gtk.WRAP_WORD)
        textview2.set_border_width(5)
        textview2.set_left_margin(3)
        textview2.set_right_margin(3)
        textview2.set_editable(False)
        self.l_d_buffer = textview2.get_buffer()

        # right up
        textview3 = gtk.TextView()
        r_u_scroll = gtk.ScrolledWindow()
        r_u_scroll.add(textview3)
        r_u_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview3.set_wrap_mode(gtk.WRAP_WORD)
        textview3.set_border_width(5)
        textview3.set_left_margin(3)
        textview3.set_right_margin(3)
        self.r_u_buffer = textview3.get_buffer()

        # right down
        textview4 = gtk.TextView()
        r_d_scroll = gtk.ScrolledWindow()
        r_d_scroll.add(textview4)
        r_d_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview4.set_wrap_mode(gtk.WRAP_WORD)
        textview4.set_border_width(5)
        textview4.set_left_margin(3)
        textview4.set_right_margin(3)
        textview4.set_editable(False)
        self.r_d_buffer = textview4.get_buffer()

        # images for buttons
        img = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'clear-16x16.png'))
        img2 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'translate-16x16.png'))

        self.l_button = gtk.Button()
        image = gtk.Image()
        image.set_from_pixbuf(img2)
        layout = gtk.HBox(False, 3)
        layout.pack_start(image, False, False)
        layout.pack_start(gtk.Label('Translate'), False, False)
        alg = gtk.Alignment(0.5, 0.5)
        alg.add(layout)
        self.l_button.add(alg)
        self.l_button.set_name('Left Button')
        self.l_button.connect('clicked', self.translate)


        self.r_button = gtk.Button()
        image = gtk.Image()
        image.set_from_pixbuf(img2)
        layout = gtk.HBox(False, 3)
        layout.pack_start(image, False, False)
        layout.pack_start(gtk.Label('Translate'), False, False)
        alg = gtk.Alignment(0.5, 0.5)
        alg.add(layout)
        self.r_button.add(alg)
        self.r_button.set_name('Right Button')
        self.r_button.connect('clicked', self.translate)

        self.l_button_clear = gtk.Button()
        image = gtk.Image()
        image.set_from_pixbuf(img)
        layout = gtk.HBox(False, 3)
        layout.pack_start(image, False, False)
        layout.pack_start(gtk.Label('Clear'), False, False)
        alg = gtk.Alignment(0.5, 0.5)
        alg.add(layout)
        self.l_button_clear.add(alg)
        self.l_button_clear.set_name('Left Button')
        self.l_button_clear.connect('clicked', self.clear)

        self.r_button_clear = gtk.Button()
        image = gtk.Image()
        image.set_from_pixbuf(img)
        layout = gtk.HBox(False, 3)
        layout.pack_start(image, False, False)
        layout.pack_start(gtk.Label('Clear'), False, False)
        alg = gtk.Alignment(0.5, 0.5)
        alg.add(layout)
        self.r_button_clear.add(alg)
        self.r_button_clear.set_name('Right Button')
        self.r_button_clear.connect('clicked', self.clear)

        textview1.connect('key-press-event', self.keypressed, self.l_button)
        textview3.connect('key-press-event', self.keypressed, self.r_button)

        table_l = gtk.Table(1, 3, True)
        table_l.set_border_width(10)
        table_r = gtk.Table(1, 3, True)
        table_r.set_border_width(10)

        table_l.attach(self.l_button_clear, 0, 1, 0, 1)
        table_l.attach(self.l_button, 1, 3, 0, 1)

        table_r.attach(self.r_button_clear, 0, 1, 0, 1)
        table_r.attach(self.r_button, 1, 3, 0, 1)

        self.left_label = gtk.Label('<small>From <b>' + self.from_lang + '</b> to <b>' + self.to_lang + '</b></small>')
        self.right_label = gtk.Label('<small>From <b>' + self.to_lang + '</b> to <b>' + self.from_lang + '</b></small>')
        self.left_label.set_use_markup(True)
        self.right_label.set_use_markup(True)

        vbox_l = gtk.VBox()
        self.vbox_r = gtk.VBox()

        vbox_l.pack_start(self.left_label, False, False, 5)
        vbox_l.pack_start(l_u_scroll)
        vbox_l.pack_start(table_l, False, False)
        vbox_l.pack_start(l_d_scroll)
        self.vbox_r.pack_start(self.right_label, False, False, 5)
        self.vbox_r.pack_start(r_u_scroll)
        self.vbox_r.pack_start(table_r, False, False)
        self.vbox_r.pack_start(r_d_scroll)

        self.toolbar = gtk.Toolbar()
        self.toolbar.set_style(gtk.TOOLBAR_BOTH)

        img1 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'language-32x32.png'))
        image1 = gtk.Image()
        image1.set_from_pixbuf(img1)
        img2 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'about-32x32.png'))
        image2 = gtk.Image()
        image2.set_from_pixbuf(img2)
        img3 = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'exit-32x32.png'))
        image3 = gtk.Image()
        image3.set_from_pixbuf(img3)



        add_btn = gtk.ToolButton(image1, 'Language')
        add_btn.connect('clicked', self.choice_lang)
        about_btn = gtk.ToolButton(image2, 'About')
        about_btn.connect('clicked', self.about)
        exit_btn = gtk.ToolButton(image3, 'Exit')
        exit_btn.connect('clicked', self.pr_exit)

        self.toolbar.insert(add_btn, 0)
        self.toolbar.insert(about_btn, 1)
        self.toolbar.insert(exit_btn, -1)

        hbox = gtk.HBox(True, 20)
        hbox.pack_start(vbox_l)
        hbox.pack_start(self.vbox_r)

        self.statusbar = gtk.Statusbar()
        self.progressbar = gtk.ProgressBar()

        self.vbox = gtk.VBox()
        self.vbox.pack_start(menubar, False, True)
        self.vbox.pack_start(self.toolbar, False, True)
        self.vbox.pack_start(gtk.HSeparator(), False, True)
        self.vbox.pack_start(hbox)
        self.vbox.pack_start(self.statusbar, False, True)
        self.vbox.pack_end(self.progressbar, False, False)

        self.add(self.vbox)

        self.connect('destroy', self.pr_exit)
        self.show_all()
        self.progressbar.hide()
        if self.one_direction:
            self.vbox_r.hide()
        if self.hide_toolbar:
            self.toolbar.hide()


    def show_hide_toolbar(self, widget):
        ''' Switch from one to two directions of translate '''
        if widget.get_active():
            # remove toolbar
            self.toolbar.hide()
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/hide_toolbar', True)
        else:
            # restore toolbar
            self.toolbar.show()
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/hide_toolbar', False)

    def one_two(self, widget):
        ''' Switch from one to two directions of translate '''
        if widget.get_active():
            # remove right textviews
            self.vbox_r.hide()
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/one_direction', True)
        else:
            # restore right textviews
            self.vbox_r.show()
            self.gconf_client.set_bool(GCONF_PREF_DIR + '/one_direction', False)

    def choice_lang(self, widget):

        def change_lang(new_from_lang, new_to_lang):
            # set selected language
            self.from_lang = new_from_lang
            self.to_lang = new_to_lang
            # set new language in comboboxes
            combobox_1.set_active(keys.index(self.from_lang))
            combobox_2.set_active(keys.index(self.to_lang))
            # change labels
            self.left_label.set_text('<small>From <b>' + self.from_lang + '</b> to <b>' + self.to_lang + '</b></small>')
            self.right_label.set_text('<small>From <b>' + self.to_lang + '</b> to <b>' + self.from_lang + '</b></small>')
            self.left_label.set_use_markup(True)
            self.right_label.set_use_markup(True)
            # write selected language in config
            self.gconf_client.set_string(GCONF_PREF_DIR + '/lang_from', self.from_lang)
            self.gconf_client.set_string(GCONF_PREF_DIR + '/lang_to', self.to_lang)

        def swap_lang(widget):
            self.from_lang, self.to_lang = self.to_lang, self.from_lang
            change_lang(self.from_lang, self.to_lang)

        dialog = gtk.Dialog('Choice Language',
                           None,
                           gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))

        fix = gtk.Fixed()
        combobox_1 = gtk.combo_box_new_text()
        combobox_2 = gtk.combo_box_new_text()
        keys = self.all_lang.keys()
        keys.sort()
        for k in keys:
            combobox_1.append_text(k)
            combobox_2.append_text(k)

        combobox_1.set_active(keys.index(self.from_lang))
        combobox_2.set_active(keys.index(self.to_lang))

        button_swap = gtk.Button()
        img = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'swap-16x16.png'))
        image = gtk.Image()
        image.set_from_pixbuf(img)
        button_swap.add(image)
        button_swap.connect('clicked', swap_lang)

        fix.put(gtk.Label('From'), 10, 10)
        fix.put(gtk.Label('To'), 235, 10)
        fix.put(gtk.Label(' '), 405, 70)
        fix.put(combobox_1, 10, 30)
        fix.put(combobox_2, 235, 30)
        fix.put(button_swap, 190, 31)
        fix.show_all()


        dialog.vbox.pack_start(fix)
        dialog.set_resizable(False)
        dialog.vbox.set_border_width(20)
        dialog.set_icon_from_file(os.path.join(IMAGES_dir, 'language-32x32.png'))
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_OK:
            change_lang(keys[combobox_1.get_active()], keys[combobox_2.get_active()])

    def about(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name('Gnotran')
        img = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_dir, 'google-64x64.png'))
        about.set_logo(img)
        about.set_version(__version__)
        about.set_copyright('Copyrights © 2010 Nikolay Blohin')
        about.set_comments('Simple Gnome client for Google Translate')
        about.set_website('http://originalcoding.com')
        about.set_website_label('Original Coding')
        about.set_authors(['Author and developer:',
                           '    Nikolay Blohin <nikolay@blohin.org>',
                           '',
                           'Thanks for testing and comments:',
                           '    Pavlo Kapyshin <i@93z.org>',
                           '    Rick Vause <rvause@gmail.com>'])
        about.set_artists(['Thanks for beautiful icons:',
                           '    Schollidesign http://schollidesign.deviantart.com',
                           '    Eli http://eliburford.com'])
        about.set_icon_from_file(os.path.join(IMAGES_dir, 'about-32x32.png'))
        about.run()
        about.destroy()


    def translate(self, widget):
        ''' Translate text in tread'''
        def request_to_server(self, text, out_buffer):
            # show progressbar
            gtk.gdk.threads_enter()
            self.progressbar.show()
            fraction = 0.2
            self.progressbar.set_fraction(fraction)
            gtk.gdk.threads_leave()

            translation = ''
            lines = text.split('\n')
            step_fraction = (1-fraction)/len(lines)

            for line in lines:
                url = 'http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=' + urllib.quote(line) + '&langpair=' + c_from + '|' + c_to

                try:
                    server_response = urllib.urlopen(url)
                    response_dict = json.load(server_response)
                except:
                    response_dict = False

                gtk.gdk.threads_enter()
                self.progressbar.set_fraction(fraction)
                fraction += step_fraction
                gtk.gdk.threads_leave()

                if response_dict:
                    if response_dict['responseStatus'] == 200:
                        translation += response_dict['responseData']['translatedText'] + '\n'
                    else:
                        translation += '\n'
                    message = 'Translated successfully completed.'
                else:
                    translation = ''
                    message = 'Translation Error (error connecting to Google). Try again later.'
                    break

            gtk.gdk.threads_enter()
            translation = translation.replace('&#39;', '\'')
            translation = translation.replace('&quot;', '\"')
            translation = translation.strip()
            out_buffer.set_text(translation)
            self.progressbar.hide()
            self.statusbar.pop(bar_id)
            self.statusbar.push(bar_id, message)
            gtk.gdk.threads_leave()


        bar_id = self.statusbar.get_context_id('statusbar')
        self.statusbar.push(bar_id, 'Request to Google...')

        if widget.get_name() == 'Left Button':
            in_buffer = self.l_u_buffer
            out_buffer = self.l_d_buffer
            c_from = self.all_lang[self.from_lang]
            c_to = self.all_lang[self.to_lang]
        else:
            in_buffer = self.r_u_buffer
            out_buffer = self.r_d_buffer
            c_from = self.all_lang[self.to_lang]
            c_to = self.all_lang[self.from_lang]

        text = in_buffer.get_text(in_buffer.get_start_iter(), in_buffer.get_end_iter())

        mythread = threading.Thread(target=request_to_server, args=(self, text, out_buffer))
        mythread.start()


    def clear(self, widget):
        ''' Clear buffers '''
        if widget.get_name() == 'Left Button':
            in_buffer = self.l_u_buffer
            out_buffer = self.l_d_buffer
        else:
            in_buffer = self.r_u_buffer
            out_buffer = self.r_d_buffer

        in_buffer.set_text('')
        out_buffer.set_text('')


    def keypressed(self, widget, event, button):
        ''' Translate text when "Ctrl+Enter" pressed '''
        if 'GDK_CONTROL_MASK' in event.state.value_names:
            if event.hardware_keycode in (36, 104):
                self.translate(button)
                return True


    def pr_exit(self, widget):
        ''' Exit from program '''
        gtk.main_quit()


gtk.gdk.threads_init()
MainWindow()
gtk.main()
