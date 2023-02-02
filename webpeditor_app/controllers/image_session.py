from rest_framework import generics
from rest_framework.response import Response
from django.contrib.sessions.backends.db import SessionStore


# class ImageSessionCreateView(generics.CreateAPIView):
#     def create(self, request, *args, **kwargs):
#         # Create a new session
#         session = SessionStore()
#         session_id = session.create()
#
#         # Store the session ID in MongoDB using Djongo
#         # Replace with your MongoDB code
#         collection = connection.get_default_database()['sessions']
#         collection.insert_one({'session_id': session_id})
#
#         # Set the session expiry to 2 hours
#         session.set_expiry(7200)
#
#         # Return the session ID in the response
#         return Response({'session_id': session_id})
