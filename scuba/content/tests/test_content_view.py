"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.urls import reverse
from django.test import TestCase

from scuba.content.models import FAQSection, FAQEntry


class TestContentView(TestCase):
    fixtures = ["test_users.json"]

    def test_faq_page(self):
        """
        test faq page
        """
        # create some FAQs
        for i in range(1, 12):
            title = f"Section Title {i}"
            section = FAQSection.objects.create(title=title)
            self.assertEqual(section.__str__(), title)

            for j in range(1, 12):
                title = f"Entry Title {j}"
                description = f"Description Entry {j}"

                # create an entry
                entry = FAQEntry.objects.create(faq_section=section,
                                                title=title,
                                                description=description)

                self.assertEqual(entry.__str__(), title)

        response = self.client.get(reverse('faq'))
        content = response.rendered_content

        for i in range(1, 12):
            title = f"Section Title {i}"
            self.assertIn(title, content)

            for j in range(1, 12):
                title = f"Entry Title {j}"
                self.assertIn(title, content)

        self.assertEqual(response.status_code, 200)
