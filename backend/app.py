import json
import os
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError


bedrock = boto3.client("bedrock-runtime")
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")
ALLOWED_ENERGY = {"low", "medium", "high"}
ALLOWED_TONE = {"gentle", "direct", "playful"}


def response(status: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body),
    }


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return response(204, {})

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Please send valid JSON."})

    thoughts = payload.get("thoughts", "").strip()
    energy = payload.get("energy", "medium")
    tone = payload.get("tone", "gentle")

    if not thoughts or len(thoughts) > 4000:
        return response(400, {"error": "Tell me what is on your mind (up to 4,000 characters)."})
    if energy not in ALLOWED_ENERGY or tone not in ALLOWED_TONE:
        return response(400, {"error": "Please choose one of the available energy and tone options."})

    prompt = f"""You are Small Wins, a warm and practical next-step coach.
The user has shared a messy thought dump. Return exactly one realistic action that
can be started in about 10 minutes. Never give medical, legal, financial, or crisis
advice. Do not shame the user. Do not invent facts. Keep the action concrete and
small enough for the user's energy level.

User energy: {energy}
Requested tone: {tone}
Thought dump:
{thoughts}

Return ONLY valid JSON with these string/number keys:
headline, next_step, minutes, why_it_matters, permission_slip, when_done.
The minutes value must be an integer from 2 to 15. The permission_slip must
reassure the user that stopping after this step is allowed."""

    try:
        result = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": "You produce concise, kind, valid JSON and nothing else."}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 450, "temperature": 0.6},
        )
        text = result["output"]["message"]["content"][0]["text"]
        plan = json.loads(text)
        required = {"headline", "next_step", "minutes", "why_it_matters", "permission_slip", "when_done"}
        if not required.issubset(plan) or not isinstance(plan["minutes"], int):
            raise ValueError("The model returned an incomplete plan.")
        plan["minutes"] = max(2, min(15, plan["minutes"]))
        return response(200, {"plan": plan})
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Invalid Bedrock response: {error}")
        return response(502, {"error": "I could not shape that into a safe next step. Please try again."})
    except (BotoCoreError, ClientError) as error:
        print(f"Bedrock request failed: {error}")
        return response(502, {"error": "The agent is taking a breather. Please try again in a moment."})
