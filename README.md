# discord_voice_detection
snippet for voice detection in discord

# requierements
* py-cord[voice]
  
# What is it ?

A code snippet that took me too much time to admit.
It detects when a user is speaking in a voice chat and generate a .wav file with the audio.
When user stops speaking for 0.5 sec it creates the audio file and resets to start a new recoding.

# Usage 
go to a vc channel
/join
/start
when done 
/stop
/leave

# How it works ?
Bot will start a recording on the voice channel (/join & /start)
Recording goes to a sink
The sink contains user and audio data
We then check if the audio data is present 
Then every 0.5 sec we check the size of the audio data, if it increases then user is speaking, if it stays the same then user stopped speaking
When user stops speaking we dump the data to a file and reset the audio in the sink to start fresh

# Why ?
First step towards voice assistant discord.

# Next steps
* add a call to an "api" to indicate that a file has been generated
* convert to audio file to text using whisper (probably fast-whisper or something even faster)
* (optionnal) detect word using porcupine or just parse text to detect commands or keywork like "remember this :" to save it to a RAG
* once transcribe send the text to an LLM (mistral or llama3, small model for fast inference and injecting prompt for conversationnal behavior)
* grab the response from the LLM and convert it back to audio using piper or similar
* send the audio to the bot to play it
* (target : the whole trip would take less than a second)
