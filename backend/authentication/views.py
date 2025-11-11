from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ChangePasswordSerializer, UpdateLanguageSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer that allows login with email"""
    
    def validate(self, attrs):
        # Check if username is actually an email
        username = attrs.get('username', '')
        if '@' in username:
            # Try to find user by email
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass  # Let parent handle the error
        
        return super().validate(attrs)

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
        
        # Create user
        response = super().create(request, *args, **kwargs)
        
        # Generate JWT tokens for the new user
        if response.status_code == status.HTTP_201_CREATED:
            user_data = response.data
            user = User.objects.get(username=user_data['username'])
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Return in the format frontend expects: {access, refresh, user}
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        
        return response

class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Add user data to the response
        if response.status_code == 200:
            # Get the user from the validated token
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            # Serialize user data
            user_serializer = UserSerializer(user)
            
            # Add user data to response
            response.data['user'] = user_serializer.data
        
        return response

class LogoutView(APIView):
    """
    Logout endpoint with token blacklisting.
    Blacklists the refresh token to prevent reuse.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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

class AuthCheckView(APIView):
    """
    Fast authentication check endpoint for frontend
    Returns authentication status and basic user info
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        if request.user and request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'phone': getattr(request.user, 'phone', None),
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'is_verified': getattr(request.user, 'is_verified', False),
                    'preferred_language': getattr(request.user, 'preferred_language', 'en'),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'authenticated': False,
                'user': None
            }, status=status.HTTP_200_OK)