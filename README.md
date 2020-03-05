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
to
ExecStart=/usr/lib/bluetooth/bluetoothd -P input

sudo cp org.yaptb.btkkbservice.conf /etc/dbus-1/system.d

sudo service bluetooth stop
sudo /usr/lib/bluetooth/bluetoothd -P input &
sudo python3 btk_server.py

on seperate terminal:

python kb_client.py 






