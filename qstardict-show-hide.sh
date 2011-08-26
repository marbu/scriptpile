#!/bin/sh
# http://wiki.qstardict.ylsoftware.com/Hiding_and_showing_QStarDict_window_with_D-Bus
 
qdbus org.qstardict.dbus /qstardict org.freedesktop.DBus.Properties.Set \
org.qstardict.dbus mainWindowVisible  $(( ! $(qdbus org.qstardict.dbus /qstardict org.freedesktop.DBus.Properties.Get \
org.qstardict.dbus mainWindowVisible)))
