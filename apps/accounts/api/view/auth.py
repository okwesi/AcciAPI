from django.contrib.auth import get_user_model, authenticate, logout as user_logout
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.accounts.api.serializers.auth import UserSerializer, ProfileVerificationSerializer, \
    UserWithTokenSerializer, \
    ProfileVerificationResendSerializer, LoginSerializer, PasswordChangeSerializer, LogoutSerializer, \
    MemberCheckSerializer, MemberLoginSerializer, MemberUserWithTokenSerializer
from apps.shared.general import GENERAL_SUCCESS_RESPONSE

User = get_user_model()


class UserAuthViewSet(viewsets.GenericViewSet):
    """
    A viewset for handling user account management: login, logout, change password, reset_password, update profile.
    """

    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update_profile', 'change_password', 'logout']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=['POST'])
    def verify_account(self, request):
        """
        Verify user's profile using the code sent via WhatsApp.
        """
        serializer = ProfileVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserWithTokenSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def resend_verification(self, request):
        """
        Verify user's profile using the code sent via WhatsApp.
        """
        serializer = ProfileVerificationResendSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(**serializer.validated_data)
            if user is not None:
                return Response(UserWithTokenSerializer(user).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['PUT'])
    def update_profile(self, request):
        serializer = UserSerializer(self.request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PATCH'])
    def change_password(self, request, pk=None):
        user = self.request.user
        serializer = PasswordChangeSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        """
        Blacklist token on logout.
        """
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_logout(request)
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='check-member-phone-number')
    def check_member_phone_number(self, request):
        """
        Check if member's phone number exists
        """
        serializer = MemberCheckSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Account Created successfully, Verify your account'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='mobile-login')
    def mobile_login(self, request):
        serializer = MemberLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(MemberUserWithTokenSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
