## BTSquawk

Trying to get a voice controlled BT keyboard

Based on https://gist.github.com/ukBaz/a47e71e7b87fbc851b27cde7d1c0fcf0#file-btk_server-py for the integration to bluetooth

which was based on http://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html

Merged with https://github.com/klei22/project-keyword-spotter
by:
Kevin Kilgour (kkilgour@google.com), Google Research
Duc Dung Nguyen (ddung@google.com), Google Research
Sarah Amsellem (samsellem@google.com), Google Research
Dominik Roblek (droblek@google.com), Google Research
Michael Tyka (mtyka@google.com), Google Research



Install instructions:

Full Buster Raspian install

```
sudo apt-get update

sudo apt-get upgrade

sudo apt-get dist-upgrade

sudo apt-get install python3-dbus

sudo pip3 install evdev

sudo service bluetooth stop
```


modify the /lib/systemd/system/bluetooth.service file. You will need to change the Service line from:

```
ExecStart=/usr/lib/bluetooth/bluetoothd
```

to:

```
ExecStart=/usr/lib/bluetooth/bluetoothd -P input
```

Change the class of the device to a bluetooth keyboard by modifying main.conf:

```
sudo vi /etc/bluetooth/main.conf

#add this line in or ammend the Class = to this if it's already there:

Class = 0x002540
```


If you want it to emulate another device check this for codes: http://domoticx.com/bluetooth-class-of-device-lijst-cod/


```
#now copy this file from the repo to to system.d

sudo cp org.yaptb.btkkbservice.conf /etc/dbus-1/system.d

#bounce your pi to make all the changes apply sudo reboot now

#once it's back up run these three commands on a terminal

sudo service bluetooth stop

sudo /usr/lib/bluetooth/bluetoothd -P input &

sudo python3 btk_server.py

#on seperate terminal:

python kb_client.py
``


Now you should be able to pair the device with a phone or something else as normal. Keyboard strokes on the physical keyboard plugged into the rPi will now appear on the paired device. Keyboard strokes from a ssh connection do appear on the kb_client output but won't be sent to the connected device. It has to be the keyboard on the rPi. Hope that makes sense as this tripped me up for half an hour.

coral TPU needs setup as per the instructions :








# Install TPU:

Follow these steps taken from: https://coral.ai/docs/accelerator/get-started/#set-up-on-linux-or-raspberry-pi

```
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

sudo apt-get update

sudo apt-get install libedgetpu1-std


#plug in the TPU stick and if laready plugged in disconnect and reinsert.


#Now install 

#https://coral.ai/docs/accelerator/get-started/#2-install-the-tensorflow-lite-library

#Download the example code from GitHub:

mkdir coral && cd coral

git clone https://github.com/google-coral/tflite.git
#Download the bird classifier model, labels file, and a bird photo:

cd tflite/python/examples/classification

bash install_requirements.sh
#Run the image classifier with the bird photo (shown in figure 1):



#https://coral.ai/docs/accelerator/get-started/#2-install-the-tensorflow-lite-library
#https://www.tensorflow.org/lite/guide/python


pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
```

```
python3 classify_image.py \
--model models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--labels models/inat_bird_labels.txt \
--input images/parrot.jpg
```


#setup recording and playback devices:

https://iotbytes.wordpress.com/connect-configure-and-test-usb-microphone-and-speaker-with-raspberry-pi/



#you might have to unplug and re plug in
```
pi@piVoiceKB:~ $ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
  Subdevices: 7/7
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
card 0: ALSA [bcm2835 ALSA], device 1: bcm2835 IEC958/HDMI [bcm2835 IEC958/HDMI]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: ALSA [bcm2835 ALSA], device 2: bcm2835 IEC958/HDMI1 [bcm2835 IEC958/HDMI1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
pi@piVoiceKB:~ $ arecord -l
**** List of CAPTURE Hardware Devices ****
card 1: Microphone [Logitech USB Microphone], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0


cd
#rename your sound file if you have one
mv .asoundrc asoundrc.old

vi .asoundrc
```
Fill it with something like this: 

```
pcm.!default {
  type asym
  capture.pcm "mic"
  playback.pcm "speaker"
}
pcm.mic {
  type plug
  slave {
    pcm "hw:<card number>,<device number>"
  }
}
pcm.speaker {
  type plug
  slave {
    pcm "hw:<card number>,<device number>"
  }
}
```

So for me I did:

```
pcm.!default {
  type asym
  capture.pcm "mic"
  playback.pcm "speaker"
}
pcm.mic {
  type plug
  slave {
    pcm "hw:1,0"
  }
}
pcm.speaker {
  type plug
  slave {
    pcm "hw:0,1"
  }
}


sudo cp ~/.asoundrc /etc/asound.conf
```



```
#  https://github.com/google-coral/project-keyword-spotter

cd

git clone https://github.com/google-coral/project-keyword-spotter.git

cd project-keyword-spotter
sh install_requirements.sh


python3 run_model.py
```


If this works then you should be able to jump back to my repo and run:

```
python3 voice_kb_client.py
```

and it'll listen for these inputs (and click the key corresponding to the number):

```
  "go_forwards": 40,
  "go_backwards": 41,
  "move_down": 81,
  "go_down": 81,
  "go_left": 80,
  "move_left": 80,
  "move_right": 79,
  "go_right": 79,
  "move_up": 82,
  "go_up": 82
```

It also listens for these commands to turn off and on the listening for other commands

  Commands to act on commands it hears (default state):
```
  "begin_application"
  "begin_program"
  "begin_task"
  "start_application"
  "start_game"
  "start_program"
  "start_task"
```

  Commands to stop acting on commands till it hears command to start again
```
  "close_application"
  "close_program"
  "close_task"
  "stop_application"
  "stop_program"
  "stop_task"
```
