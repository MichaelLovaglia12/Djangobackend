from .models import Lead
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from django.urls import reverse
from datetime import datetime

from .models import ConnectedEmail, User, Campaign, Lead
from .serializers import ConnectedEmailSerializer


# Create your tests here.
class LeadTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.lead = Lead.objects.create(name='Harsh', email='harsh@gmail.com', company='Harsh Inc', website="https://harsh.com")

    def test_get_all_leads(self):
        response = self.client.get('/api/leads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_lead(self):
        response = self.client.get('/api/leads/{}/'.format(self.lead.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lead(self):
        data = {'name': 'Jhon', 'email': 'Jhon@outlook.com', 'company': 'Jhon Inc', 'website': 'https://jhon.com'}
        response = self.client.post('/api/leads/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_lead(self):
        data = {'name': 'Jhon', 'email': 'Jhon_lead@outlook.com', 'company': 'Jhon Inc', 'website': 'https://jhon.com'}
        response = self.client.put('/api/leads/{}/'.format(self.lead.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lead(self):
        response = self.client.delete('/api/leads/{}/'.format(self.lead.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)



class ConnectedEmailIMAPViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = 'testtoken'
        self.client.force_authenticate(user=self.user, token=self.token)

    def test_create_connected_email_imap(self):
        data = {
            'email_address': 'test@example.com',
            'imap_host': 'imap.example.com',
            'imap_port': '993',
            'imap_username': 'test@example.com',
            'imap_password': 'testpass'
        }
        response = self.client.post(reverse('connected_email_imap'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConnectedEmail.objects.count(), 1)
        connected_email = ConnectedEmail.objects.first()
        self.assertEqual(connected_email.provider_name, 'IMAP')
        self.assertEqual(connected_email.email_address, 'test@example.com')
        self.assertEqual(connected_email.imap_host, 'imap.example.com')
        self.assertEqual(connected_email.imap_port, '993')
        self.assertEqual(connected_email.imap_username, 'test@example.com')
        self.assertEqual(connected_email.imap_password, 'testpass')

    def test_connected_email_serializer(self):
        connected_email = ConnectedEmail.objects.create(
            provider_name='IMAP',
            email_address='test@example.com',
            imap_host='imap.example.com',
            imap_port='993',
            imap_username='test@example.com',
            imap_password='testpass'
        )
        serializer = ConnectedEmailSerializer(instance=connected_email)
        expected_data = {
            'id': connected_email.id,
            'provider_name': 'IMAP',
            'email_address': 'test@example.com',
            'client_id': '',
            'secret_key': '',
            'access_token': '',
            'refresh_token': '',
            'token_expiry': None,
            'smtp_host': '',
            'smtp_port': '',
            'smtp_username': '',
            'smtp_password': '',
            'imap_host': 'imap.example.com',
            'imap_port': '993',
            'imap_username': 'test@example.com',
            'imap_password': 'testpass'
        }
        self.assertEqual(serializer.data, expected_data)


class CampaignModelTestCase(TestCase):
    def setUp(self):
        self.connected_email = ConnectedEmail.objects.create(
            provider_name='IMAP',
            email_address='test@example.com',
            imap_host='imap.example.com',
            imap_port='993',
            imap_username='test@example.com',
            imap_password='testpass'
        )
        self.lead1 = Lead.objects.create(name='Harsh1', email='harsh1@gmail.com', company='Harsh1 Inc', website="https://harsh1.com")
        self.lead2 = Lead.objects.create(name='Harsh2', email='harsh2@gmail.com', company='Harsh2 Inc', website="https://harsh2.com")
        self.campaign = Campaign.objects.create(
            connected_email=self.connected_email,
            message='Test message',
            scheduled_time=datetime.now()
        )
        self.campaign.leads.add(self.lead1, self.lead2)

    def test_campaign_model(self):
        self.assertEqual(self.campaign.connected_email.email_address, 'test@example.com')
        self.assertEqual(self.campaign.message, 'Test message')
        self.assertEqual(self.campaign.scheduled_time.date(), datetime.now().date())
        self.assertEqual(self.campaign.leads.count(), 2)
        self.assertIn(self.lead1, self.campaign.leads.all())
        self.assertIn(self.lead2, self.campaign.leads.all())