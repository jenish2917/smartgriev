from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ChangePasswordSerializer, UpdateLanguageSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        confirm_password = request.data.get('confirm_password')
        password = request.data.get('password')
        
        if confirm_password and password != confirm_password:
            return Response(
                {"password": ["Password fields didn't match."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.data.get('new_password') != request.data.get('confirm_new_password'):
            return Response({"new_password": "Password fields didn't match."})

        user = self.get_object()
        if not user.check_password(serializer.data.get('old_password')):
            return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data.get('new_password'))
        user.save()

        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

class UpdateLanguageView(APIView):
    """
    API endpoint to update user's preferred language.
    Allows authenticated users to change their interface language preference.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = UpdateLanguageSerializer(data=request.data)
        
        if serializer.is_valid():
            language = serializer.validated_data['language']
            user = request.user
            user.preferred_language = language
            user.save(update_fields=['preferred_language'])
            
            return Response({
                'message': 'Language preference updated successfully.',
                'language': language,
                'language_display': user.get_display_language()
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """Get current user's language preference"""
        user = request.user
        return Response({
            'language': user.preferred_language,
            'language_display': user.get_display_language()
        }, status=status.HTTP_200_OK)