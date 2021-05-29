from django.test import TestCase, Client


class Test404(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        response = self.guest_client.get('/,/')
        self.assertEqual(response.status_code, 404)
