import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_client import slack_client
from Slack_MCP_Agent.agent import root_agent  # importa tu agente real
from Slack_MCP_Agent.utils import extract_intent_from_json

app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))

# Simula base de datos temporal
previous_bot_threads = {}  # thread_ts → user_id (quien fue preguntado)

@app.event("message")
def handle_message_events(body, say, event):
    user_id = event.get("user")
    text = event.get("text", "")
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")
    channel = event.get("channel")

    # Ignorar mensajes del bot
    if event.get("subtype") == "bot_message":
        return

    # Registrar si el bot inicia un hilo
    if "can you attend" in text.lower() and user_id:  # <- personaliza esta lógica
        previous_bot_threads[ts] = user_id
        return

    # Si es respuesta en un hilo iniciado por el bot
    if thread_ts in previous_bot_threads:
        target_user = previous_bot_threads[thread_ts]

        prompt = f"""
        You asked <@{target_user}> if they can attend a meeting tomorrow at 10AM.
        They replied: "{text}"

        Classify the intent as:
        - accepts
        - rejects
        - proposes_alternative
        - unclear

        Respond strictly in JSON like:
        {{"intent": "accepts", "reason": "The user confirmed availability."}}
        """

        response = root_agent.run(prompt)
        intent = extract_intent_from_json(response)

        if intent == "accepts":
            reply = "✅ Perfect, I've added the meeting to your calendar!"
        elif intent == "rejects":
            reply = "❌ Thanks, we'll look for a better time."
        elif intent == "proposes_alternative":
            reply = "🔄 Thanks, let me check your proposed time."
        else:
            reply = "🤔 I didn't quite get that. Could you clarify your availability?"

        say(channel=channel, thread_ts=thread_ts, text=reply)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_BOT_TOKEN"))
    handler.start()
