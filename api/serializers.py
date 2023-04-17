from rest_framework import serializers
from .models import Lead, Campaign, ConnectedEmail


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'company', 'website']
        
class CampaignSerializer(serializers.ModelSerializer):
    leads = LeadSerializer(many=True)

    class Meta:
        model = Campaign
        fields = '__all__'

class ConnectedEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedEmail
        fields = ['id', 'provider_name', 'email_address', 'client_id', 'secret_key', 'access_token', 'refresh_token', 'token_expiry', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'imap_host', 'imap_port', 'imap_username', 'imap_password']