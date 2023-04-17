from django.urls import path
from .views import LeadListCreateAPIView, LeadRetrieveUpdateDestroyAPIView, CampaignListCreateView, CampaignRetrieveUpdateDestroyView, ConnectedEmailOAuth2View, ConnectedEmailSMTPView, ConnectedEmailIMAPView

urlpatterns = [
    path('leads/', LeadListCreateAPIView.as_view(), name='lead-list-create'),
    path('leads/<int:pk>/', LeadRetrieveUpdateDestroyAPIView.as_view(), name='lead-retrieve-update-destroy'),
    path('campaigns/', CampaignListCreateView.as_view(), name='campaign_list_create'),
    path('campaigns/<int:pk>/', CampaignRetrieveUpdateDestroyView.as_view(), name='campaign_retrieve_update_destroy'),
    path('connected_email/oauth/', ConnectedEmailOAuth2View.as_view(), name='connected_email_oauth'),
    path('connected_email/imap/', ConnectedEmailIMAPView.as_view(), name='connected_email_imap'),
    path('connected_email/smtp/', ConnectedEmailSMTPView.as_view(), name='connected_email_smtp'),
]