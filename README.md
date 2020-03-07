# BTSquawk
Trying to get a voice controlled BT keyboard

Based on https://gist.github.com/ukBaz/a47e71e7b87fbc851b27cde7d1c0fcf0#file-btk_server-py for the integration to bluetooth

which was based on  http://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html

I'm going to tie in voice recognition if I get this working




Not getting picked up as input device on Fire stick but is working ok as input for phone


Install instructions:

Full Buster Raspian install

sudo apt-get update

sudo apt-get upgrade

sudo apt-get dist-upgrade

sudo apt-get install python3-dbus

sudo pip3 install evdev

sudo service bluetooth stop

modify the /lib/systemd/system/bluetooth.service file. You will need to change the Service line from:

ExecStart=/usr/lib/bluetooth/bluetoothd

to:

ExecStart=/usr/lib/bluetooth/bluetoothd -P input


Change the class of the device to a bluetooth keyboard by modifying main.conf:

sudo vi /etc/bluetooth/main.conf 

#add this line in or ammend the Class =  to this if it's already there:

Class = 0x002540

If you want it to emulate another device check this for codes:  http://domoticx.com/bluetooth-class-of-device-lijst-cod/

#now copy this file from the repo to to system.d

sudo cp org.yaptb.btkkbservice.conf /etc/dbus-1/system.d



#bounce your pi to make all the changes apply
sudo reboot now


#once it's back up run these three commands on a terminal


sudo service bluetooth stop

sudo /usr/lib/bluetooth/bluetoothd -P input &

sudo python3 btk_server.py

#on seperate terminal:

python kb_client.py 




Now you should be able to pair the device with a phone or something else as normal.  Keyboard strokes on the physical keyboard plugged into the rPi will now appear on the paired device.  Keyboard strokes from a ssh connection do appear on the kb_client output but won't be sent to the connected device.  It has to be the keyboard on the rPi.  Hope that makes sense as this tripped me up for half an hour.

