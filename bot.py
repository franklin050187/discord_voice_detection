import io
import asyncio
import discord # pip install py-cord[voice]
from discord.sinks import WaveSink
import datetime
import wave


bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def finished_callback(sink: WaveSink, channel: discord.TextChannel):
    asyncio.run_coroutine_threadsafe(channel.send("Recording finished!"), bot.loop)
    global is_speaking
    is_speaking = False
    print("Recording finished, no more audio frames detected.")
    await sink.vc.disconnect()
    await channel.send("Recording finished, no more audio frames detected.")
    


@bot.command()
async def join(ctx: discord.ApplicationContext):
    """Join the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    await voice.channel.connect()

    await ctx.respond("Joined!")


@bot.command()
async def start(ctx: discord.ApplicationContext):
    """Record the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond(
            "I'm not in a vc right now. Use `/join` to make me join!"
        )

    vc.start_recording(
        WaveSink(),
        finished_callback,
        ctx.channel,
        sync_start=False,  # WARNING: This feature is very unstable and may break at any time.
    )
    # check if audio is present in the sink (not an empty frame)
    print("The recording has started!")
    is_speaking = True

    async def monitor_audio():
        global is_speaking
        is_speaking = True
        prev_file_size = 0
        was_speaking = False
        while vc.recording:
            for user_id, audio_data in vc.sink.audio_data.items():
                curr_file_size = audio_data.file.tell()

                if curr_file_size > prev_file_size:
                    is_speaking = True
                    was_speaking = True
                    prev_file_size = audio_data.file.tell()
                else:
                    is_speaking = False

                print("is_speaking:", is_speaking)

                # When user stops speaking, export the audio segment to a file
                if not is_speaking and was_speaking:
                    was_speaking = False

                    # Extract the audio segment
                    audio_data.file.seek(0)  # Go to the beginning of the file
                    data_to_write = audio_data.file.read()  # Read the entire content

                    # Write the audio segment to a file
                    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    filename = f"{user_id}_{timestamp}_last_speech.wav"
                    with wave.open(filename, 'wb') as wf:
                        wf.setnchannels(2)  # Set the number of channels
                        wf.setsampwidth(2)  # Set the sample width (in bytes)
                        wf.setframerate(48000)  # Set the frame rate (samples per second)
                        wf.writeframes(data_to_write)
                    
                    # Reset the BytesIO object for the next speech segment
                    audio_data.file = io.BytesIO()
                    prev_file_size = 0

                        
                
            await asyncio.sleep(0.5)  # Adjust the interval as needed

    bot.loop.create_task(monitor_audio())
    await ctx.respond("Started!")


@bot.command()
async def stop(ctx: discord.ApplicationContext):
    """Stop the recording"""
    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond("There's no recording going on right now")

    vc.stop_recording()

    await ctx.respond("The recording has stopped!")


@bot.command()
async def leave(ctx: discord.ApplicationContext):
    """Leave the voice channel!"""
    vc: discord.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond("I'm not in a vc right now")

    await vc.disconnect()

    await ctx.respond("Left!")


        
        
bot.run('TOKEN')
