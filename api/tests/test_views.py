from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

        self.parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category",
        )

        self.category = Category.objects.create(
            company=self.company,
            name="Test Category",
            parent_category=self.parent_category,
        )

    def test_list(self):
        url = reverse("category-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], self.category.name)
        self.assertEqual(
            str(response.data["company"]),
            str(self.company.id),
        )
        self.assertEqual(
            str(response.data["parent_category"]),
            str(self.parent_category.id),
        )

    def test_create(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Category.objects.filter(
                company=self.company,
                name="New Category",
            ).exists()
        )

        category = Category.objects.get(name="New Category")
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.parent_category, self.parent_category)

    def test_update(self):
        url = reverse("category-detail", args=[self.category.id])
        data = {
            "company": str(self.company.id),
            "name": "Updated Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.category.refresh_from_db()

        self.assertEqual(self.category.name, "Updated Category")
        self.assertEqual(self.category.company, self.company)
        self.assertEqual(
            self.category.parent_category,
            self.parent_category,
        )

    def test_destroy(self):
        url = reverse("category-detail", args=[self.category.id])

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Category.objects.filter(id=self.category.id).exists()
        )