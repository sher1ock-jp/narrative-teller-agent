from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

APP_NAME = "manga-agent"

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

root_agent = Agent(
    name="漫画家",
    model=LiteLlm(model="gpt-4o"),
    description=(
        "あなたはユーザーからの要望に応じて、主人公のキャラクターを設計する"
    ),
    instruction=(
        "ユーザーの要望に応じて、主人公のキャラクターを設計してください。"
    ),
)

if root_agent:
   runner = Runner(
       agent=root_agent,
       app_name=APP_NAME,
       session_service=session_service,
       artifact_service=artifact_service
   )
   print(f"Runner created for agent '{runner.agent.name}'.")
else:
   print("❌ Runnerの作成に必要なルートエージェントが定義されていません。")

async def call_agent_async(query: str):
    if not runner:
        print("❌ Runnerが定義されていません。")
        return
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    final_response_text = "エージェントは最終的な応答を生成しませんでした。"

    try:
        async for event in runner.run_async(user_id="1", session_id="1", new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    if event.content.parts[0].text:
                        final_response_text = event.content.parts[0].text
                    elif event.content.parts[0].function_response:
                        final_response_text = f"[関数応答: {event.content.parts[0].function_response.name}]"
                    else:
                        final_response_text = "[不明な形式の最終応答]"
                elif event.actions and event.actions.escalate:
                    final_response_text = f"エージェントがエスカレーション: {event.error_message or '具体的なメッセージはありません。'}"
                else:
                    final_response_text = "[エージェントからの最終応答が空でした]"
    except Exception as e:
        final_response_text = f"エージェントの内部でエラーが発生しました: {str(e)}"
    return final_response_text  