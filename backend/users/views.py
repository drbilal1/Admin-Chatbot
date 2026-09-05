from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.6-flash")


@api_view(['POST'])
def login_view(request):
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response({"status": "fail", "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()

    if user:
        request.session['user_email'] = user.email
        return Response({"status": "success", "message": f"Welcome, {user.name or user.email}!"})

    return Response({"status": "fail", "message": "Email not found"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def chat_command(request):
    user_message = request.data.get('message', '')

    if not user_message:
        return Response({"reply": "Please enter a command."}, status=status.HTTP_400_BAD_REQUEST)

    system_prompt = """
    You are an admin assistant that manages users in a database.
    Convert the user's request into ONLY valid JSON in this exact format:
    {"action": "add" or "delete" or "update", "email": "...", "name_lookup": "...", "field": "...", "value": "...", "phone": "...", "name": "..."}

    Rules:
    - For "add": include email, and phone/name if mentioned.
    - For "delete": include email if given, otherwise name_lookup (first name).
    - For "update": include email if given, otherwise name_lookup (first name), 
      plus "field" (e.g. "city", "phone", "name") and "value" (the new value).
    - Omit any keys that are not relevant to the action.
    - Respond with JSON only, no explanation text.
    """

    try:
        full_prompt = f"{system_prompt}\n\nUser request: {user_message}"
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        action_data = json.loads(response.text)
    except Exception as e:
        return Response({"reply": f"AI processing error: {str(e)}"}, status=500)

    result = execute_action(action_data)
    return Response(result)


def resolve_user(data):
    email = data.get("email")
    name_lookup = data.get("name_lookup")

    if email:
        return User.objects.filter(email__iexact=email).first()
    elif name_lookup:
        return User.objects.filter(name__icontains=name_lookup).first()
    return None


def execute_action(data):
    # Handle case where the AI returns a list of multiple actions
    # (e.g. a command asking to update two fields at once)
    if isinstance(data, list):
        replies = [execute_action(item) for item in data]
        combined = " ".join([r.get("reply", "") for r in replies])
        return {"reply": combined}

    action = data.get("action")

    if action == "add":
        email = data.get("email")
        if not email:
            return {"reply": "I need an email to add a user."}
        if User.objects.filter(email__iexact=email).exists():
            return {"reply": f"A user with email {email} already exists."}
        user = User.objects.create(
            email=email,
            phone=data.get("phone", ""),
            name=data.get("name", "")
        )
        return {"reply": f"✅ User {user.email} added successfully."}

    elif action == "delete":
        user = resolve_user(data)
        if user:
            email = user.email
            user.delete()
            return {"reply": f"🗑️ User {email} removed."}
        return {"reply": "I couldn't find that user to delete."}

    elif action == "update":
        user = resolve_user(data)
        field = data.get("field")
        value = data.get("value")
        if user and field and value:
            if hasattr(user, field):
                setattr(user, field, value)
                user.save()
                return {"reply": f"✅ Updated {field} to '{value}' for {user.email}."}
            return {"reply": f"'{field}' is not a valid field."}
        return {"reply": "I couldn't find that user or the update details were incomplete."}

    return {"reply": "Sorry, I couldn't understand that command."}