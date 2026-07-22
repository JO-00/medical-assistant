import asyncio
import time,numpy as np

from fastrtc import ReplyOnPause, Stream
from fastrtc.reply_on_pause import AlgoOptions

from voice import stt_model, tts_model
from session_client import start_new_session, forward_audio_to_session_service
from context import current_doctor_id


# {doctor_id: session_id}
ACTIVE_VOICE_SESSIONS = {}

# Prevent two voice generations for the same doctor at the same time
VOICE_LOCKS = {}


def get_voice_lock(doctor_id: int):
    if doctor_id not in VOICE_LOCKS:
        VOICE_LOCKS[doctor_id] = asyncio.Lock()

    return VOICE_LOCKS[doctor_id]


def create_voice_pipeline_with_context():

    async def process_voice_call(audio):

        loop = asyncio.get_running_loop()
        doctor_id = current_doctor_id.get()

        lock = get_voice_lock(doctor_id)

        async with lock:

            print(
                f"\n[START] Processing voice call for Doctor ID: {doctor_id}"
            )

            # -------------------------
            # Session initialization
            # -------------------------

            if doctor_id not in ACTIVE_VOICE_SESSIONS:

                print("[SESSION] Creating new session...")

                start = time.time()

                session_id = await start_new_session(
                    doctor_id
                )

                ACTIVE_VOICE_SESSIONS[doctor_id] = session_id

                print(
                    f"[SESSION] Created ID={session_id} "
                    f"({time.time()-start:.2f}s)"
                )

            else:
                print(
                    f"[SESSION] Using ID={ACTIVE_VOICE_SESSIONS[doctor_id]}"
                )


            # -------------------------
            # STT
            # -------------------------

            print("[STT] Processing audio...")

            start = time.time()

            transcript = await loop.run_in_executor(
                None,
                stt_model.stt,
                audio
            )

            stt_time = time.time() - start


            if not transcript or not transcript.strip():

                print(
                    f"[STT] Empty transcript ({stt_time:.2f}s)"
                )

                return


            print(
                f"[STT] OK ({stt_time:.2f}s): {transcript}"
            )


            # -------------------------
            # LLM
            # -------------------------

            print("[LLM] Sending request...")

            start = time.time()
            reply_text = await forward_audio_to_session_service(
                doctor_id=doctor_id,
                session_id=ACTIVE_VOICE_SESSIONS[doctor_id],
                message=transcript
            )

            print(
                f"[LLM] OK ({time.time()-start:.2f}s): {reply_text}"
            )


            if not reply_text:
                return


            # -------------------------
            # TTS
            # -------------------------

            print("[TTS] Generating audio...")

            start = time.time()

            # Do NOT list() the generator.
            # Generate and yield progressively.
            audio_generator = await loop.run_in_executor(
                None,
                lambda: tts_model.stream_tts_sync(reply_text)
            )
            print(type(audio_generator))

            print(
                f"[TTS] Generator ready ({time.time()-start:.2f}s)"
            )


            chunk_count = 0

            for chunk in audio_generator:

                chunk_count += 1

                yield chunk

                if chunk_count == 1:
                    print("[STREAM] First audio chunk sent")

                elif chunk_count % 5 == 0:
                    print(
                        f"[STREAM] Sent {chunk_count} chunks"
                    )

                await asyncio.sleep(0.01)


            print(
                f"[END] Completed ({chunk_count} chunks)\n"
            )


    return Stream(
        ReplyOnPause(
            process_voice_call,

            algo_options=AlgoOptions(
                audio_chunk_duration=1.0,
                started_talking_threshold=0.4,
                speech_threshold=0.3            
            ),

            can_interrupt=True
        ),

        modality="audio",
        mode="send-receive"
    )