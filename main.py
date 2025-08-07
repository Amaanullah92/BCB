import chainlit as cl
from model_config import config
from agents import Agent ,Runner
from agent_instructions import instruction
from openai.types.responses import ResponseTextDeltaEvent

agent = Agent(
    name="Bakchod Agent", 
    instructions = instruction,
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message: cl.Message):
    history=cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    msg=cl.Message(content="")
    await msg.send()

    result=Runner.run_streamed(
        agent,
        input=history,
        run_config=config
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    
    await msg.update()

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)