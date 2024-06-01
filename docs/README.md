# VisualAudioOverlay
Visual Audio Overlay is an application that provides a visual representation of audio intensity and direction. It is designed to help users, especially those with hearing impairments, by displaying visual cues for audio signals. I made this app since I am hard at hearing in my left hear so its hard for me to distinguish sounds in some games. Made this program as a test to see if a concept like this can actually help me with directional audio. Basic testing shows that it does help a decent amount if configured correctly but I will continue to test and improve upon this project and concept in the future. I also want to recreate it in C# just to see what kind of differences there would be, if any, especially in regards to processing delays. Also feel like it would be a nice project for me to do in C# so I want to try that.

I believe the concept is viable to use and it does provide a lot of help to someone who has hearing issues like myself and I will continue to improve upon it. Thought I would share the code in case someone is in a similar situation and stumbles across this.

## Features
- Visualize audio intensity and direction
- Configurable thresholds, opacity modes, view modes, audio devices etc. I tried to make it as configurable as possible, will add more to the options in the future as well.
- Want to continue adding features in the future as I continue testing

## Usage
To use it I have a VB-Audio Cable setup that I pass through VB-Audio VoiceMeeter Banana, that way I can hear still hear the audio and it gives me flexibility to choose the app that is being visualized without other apps interfering with the visualization. I plan on making it easier to set up in the future as well.

## Small GIFs to showcase how it works in a nutshell
![GIF1](https://github.com/azanzu786/VisualAudioOverlay/blob/main/GIFs/VisGIF.gif)

Basic example with a sound coming from left, right, then both channels respectively

![GIF2](https://github.com/azanzu786/VisualAudioOverlay/blob/main/GIFs/VisGIF2.gif)

Another example where audio is coming from both channels but stronger in one (opacity settings are all configurable)
