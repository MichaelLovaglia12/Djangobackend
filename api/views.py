from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from django.http import JsonResponse
from .models import Lead, Campaign, ConnectedEmail
from .serializers import LeadSerializer, CampaignSerializer, ConnectedEmailSerializer
from .utils import read_emails, send_emails

from allauth.socialaccount.models import SocialToken, SocialApp
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



class LeadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class CampaignRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

class ConnectedEmailOAuth2View(generics.CreateAPIView):
    serializer_class = ConnectedEmailSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the provider name and email address from the request data
        provider_name = request.data.get('provider_name')
        email_address = request.data.get('email_address')

        # Get the social app associated with the provider name
        social_app = get_object_or_404(SocialApp, provider=provider_name)

        # Get the social token for the authenticated user and social app
        social_token = SocialToken.objects.filter(
            account__user=request.user,
            account__provider=provider_name,
            app=social_app
        ).first()

        # Create a new ConnectedEmail object with the provided data and social token
        connected_email = ConnectedEmail(
            provider_name=provider_name,
            email_address=email_address,
            client_id=social_app.client_id,
            secret_key=social_app.secret,
            access_token=social_token.token,
            refresh_token=social_token.token_secret,
            token_expiry=social_token.expires_at
        )
        connected_email.save()

        # Serialize the ConnectedEmail object and return the response
        serializer = self.serializer_class(connected_email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ConnectedEmailIMAPView(generics.CreateAPIView):
    serializer_class = ConnectedEmailSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the email address, IMAP host, IMAP port, IMAP username, and IMAP password from the request data
        email_address = request.data.get('email_address')
        imap_host = request.data.get('imap_host')
        imap_port = request.data.get('imap_port')
        imap_username = request.data.get('imap_username')
        imap_password = request.data.get('imap_password')

        # Create a new ConnectedEmail object with the provided data
        connected_email = ConnectedEmail(
            provider_name='IMAP',
            email_address=email_address,
            imap_host=imap_host,
            imap_port=imap_port,
            imap_username=imap_username,
            imap_password=imap_password
        )
        connected_email.save()

        # Serialize the ConnectedEmail object and return the response
        serializer = self.serializer_class(connected_email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ConnectedEmailSMTPView(generics.CreateAPIView):
    serializer_class = ConnectedEmailSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the email address, IMAP host, IMAP port, IMAP username, and IMAP password from the request data
        email_address = request.data.get('email_address')
        smtp_host = request.data.get('smtp_host')
        smtp_port = request.data.get('smtp_port')
        smtp_username = request.data.get('smtp_username')
        smtp_password = request.data.get('smtp_password')

        # Create a new ConnectedEmail object with the provided data
        connected_email = ConnectedEmail(
            provider_name='SMTP',
            email_address=email_address,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password
        )
        connected_email.save()

        # Serialize the ConnectedEmail object and return the response
        serializer = self.serializer_class(connected_email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ConnectedEmailSendEmailAPIView(generics.CreateAPIView):
    serializer_class = CampaignSerializer

    def post(self, request, *args, **kwargs):
        connected_email = get_object_or_404(
            ConnectedEmail, pk=kwargs['connected_email_id'])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        leads = serializer.validated_data['leads']
        message = serializer.validated_data['message']
        scheduled_time = serializer.validated_data['scheduled_time']
        campaign = Campaign.objects.create(
            connected_email=connected_email,
            message=message,
            scheduled_time=scheduled_time
        )
        campaign.leads.set(leads)
        send_emails(connected_email, message, leads, scheduled_time)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConnectedEmailReadEmailAPIView(generics.ListAPIView):
    serializer_class = CampaignSerializer

    def get_queryset(self):
        connected_email = get_object_or_404(
            ConnectedEmail, pk=self.kwargs['connected_email_id'])
        campaigns = Campaign.objects.filter(
            connected_email=connected_email).order_by('-scheduled_time')
        return campaigns

    def list(self, request, *args, **kwargs):
        connected_email = get_object_or_404(
            ConnectedEmail, pk=self.kwargs['connected_email_id'])
        read_emails(connected_email)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)