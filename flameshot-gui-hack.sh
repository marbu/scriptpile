#!/bin/bash
# Kill flameshot daemon and before trying to start flameshot gui (so this will
# make a flameshot daemon running after the gui is done only to be killed and
# started again next time you need to take a screenshot ...). This is not a
# nice hack ... it's a "workaround" for a desktop without a system tray, see:
# https://flameshot.org/docs/guide/faq/#flameshot-doesn-t-start-no-tray-icon
killall flameshot
exec flameshot gui
