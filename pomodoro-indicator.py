#!/usr/bin/env python
import gtk
import appindicator
import threading
import subprocess
import sys
import time
from subprocess import Popen

WAITING, POMODORO, PAUSE = range(3)
WAITING_ICO = "waiting.png"
POMODORO_ICO = "pomodoro.png"
PAUSE_ICO = "pause.png"
SOUND = "finish.ogg"
      
class AppIndicator:
  state = WAITING
  sleep = False
  remaining_sec = 0
  sound = False
  time = time.time()
  def __init__(self):
    self.ind = appindicator.Indicator("timer-pomodoro-indicator",
      POMODORO_ICO, appindicator.CATEGORY_APPLICATION_STATUS)
    self.ind.set_status (appindicator.STATUS_ACTIVE)
    self.menu = gtk.Menu()
    item = gtk.MenuItem("New Pomodoro")
    item.connect("activate", self.newPomodoro, None)
    self.menu.append(item)
    item = gtk.MenuItem("New pause")
    item.connect("activate", self.newPause, None)
    self.menu.append(item)
    item = gtk.MenuItem("New big pause")
    item.connect("activate", self.newBigPause, None)
    self.menu.append(item)
    item = gtk.MenuItem("Stop")
    item.connect("activate", self.stop, None)
    self.menu.append(item)
    item = gtk.MenuItem("sleep/continue")
    item.connect("activate", self.sleep_continue, None)
    self.menu.append(item)
    item = gtk.MenuItem("Quitter")
    item.connect("activate", self.quit, None)
    self.menu.append(item)
    self.menu.show_all()
    self.ind.set_menu(self.menu)
    self.ind.set_label(" ")
    self.th = threading.Thread(target=self.loop)
    self.th.start()
  def quit(self, *args):
    print "quit"
    self.th._Thread__stop()
    gtk.main_quit()
    sys.exit()
  def stop(self, *args):
    self.state = WAITING
    self.time = time.time()
    self.ind.set_label(" ")
    self.ind.set_icon(POMODORO_ICO)
    self.update()
  def newPomodoro(self, *args):
    self.sound = True
    self.state = POMODORO
    self.time = time.time() + 25*60
    self.ind.set_icon(POMODORO_ICO)
    self.update()
  def newBigPause(self, *args):
    self.sound = True
    self.state = PAUSE
    self.time = time.time() + 20*60
    self.ind.set_icon(PAUSE_ICO)
    self.update()
  def newPause(self, *args):
    self.sound = True
    self.state = PAUSE
    self.time = time.time() + 5*60
    self.ind.set_icon(PAUSE_ICO)
    self.update()
    
  def sleep_continue(self, *args):
    if self.sleep:
      self.sleep = False
      self.time = time.time() + self.remaining_sec
      self.update()
    else:
      self.sleep = True
      self.remaining_sec = int(self.time - time.time())
      self.update()
      
  def update(self):
    if self.sleep:
      title = "SLEEP !      "
      offset = int((time.time()/0.2) % len(title))
      title = title[offset:(offset+len(title))] + title[0:offset]
      self.ind.set_label(title)
    else:
      diff = int(self.time - time.time())
      if diff > 0:
        title = "0"
        if diff > 60:
          title = str(int(diff/60)+1)+" m"
          # title = str(int(diff))+" s"
        else :
          title = str(diff)+" s"
        if self.state == POMODORO or self.state == PAUSE:
          self.ind.set_label(title)
      else :
        if self.sound:
          Popen(['/usr/bin/mplayer',SOUND])
          self.sound = False
        if self.state == POMODORO:
          if diff % 2 == 0:
            self.ind.set_icon(WAITING_ICO)
            self.ind.set_label("   - END -    ")
          else :
            self.ind.set_icon(POMODORO_ICO)
            self.ind.set_label("POMODORO")
        if self.state == PAUSE:
          if diff % 2 == 0:
            self.ind.set_icon(WAITING_ICO)
            self.ind.set_label("END")
          else :
            self.ind.set_icon(PAUSE_ICO)
            self.ind.set_label("PAUSE")
  def loop(self):
    while 1:
      if self.sleep:
        time.sleep(0.2)
      else:
        time.sleep(1)
      self.update()
      
gtk.gdk.threads_init()
AppIndicator()
gtk.main()
