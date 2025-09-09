import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken

class ChatbotView(APIView):
    """
    API View to handle chatbot messages for PSAssist.
    Forwards messages from authenticated users to the Rasa server.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')
        if not user_message:
            return Response({'error': 'Message not provided'}, status=400)

        # Generate a short-lived JWT token for the user.
        # This allows the Rasa Action Server to make authenticated API calls
        # to your Django backend on the user's behalf.
        try:
            token = AccessToken.for_user(request.user)
            auth_token = str(token)
        except Exception as e:
            print(f"CRITICAL: Could not generate JWT token for bot action: {e}")
            return Response({'error': 'Internal authentication error.'}, status=500)

        rasa_server_url = 'http://rasa:5005/webhooks/rest/webhook'
        rasa_payload = {
            'sender': str(request.user.id),
            'message': user_message,
            'metadata': {
                'token': auth_token
            }
        }

        try:
            response = requests.post(rasa_server_url, json=rasa_payload, timeout=100)
            response.raise_for_status()
            print("\n\n\n\n\n\n\tsfdfsdfsdf",response)
            bot_responses = response.json()
            print("\n\n\n\n\n\n\tsfdfsdfsdf",bot_responses)
            return Response(bot_responses)
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Rasa server: {e}")
            error_response = [{"text": "Sorry, PSAssist is unavailable right now. Please try again later."}]
            return Response(error_response, status=503)

