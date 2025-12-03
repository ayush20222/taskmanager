from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Task

class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': False
        }

    def test_create_task(self):
        response = self.client.post('/api/tasks/', self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_get_tasks(self):
        Task.objects.create(user=self.user, title='Task 1', description='Desc 1')
        Task.objects.create(user=self.user, title='Task 2', description='Desc 2')
        
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_single_task(self):
        task = Task.objects.create(user=self.user, title='Single Task', description='Single Desc')
        
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Single Task')

    def test_update_task(self):
        task = Task.objects.create(user=self.user, title='Old Title', description='Old Desc')
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': True
        }
        
        response = self.client.put(f'/api/tasks/{task.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Title')
        self.assertTrue(task.completed)

    def test_delete_task(self):
        task = Task.objects.create(user=self.user, title='Delete Me', description='To be deleted')
        
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_filter_by_completed(self):
        Task.objects.create(user=self.user, title='Task 1', description='Desc 1', completed=True)
        Task.objects.create(user=self.user, title='Task 2', description='Desc 2', completed=False)
        
        response = self.client.get('/api/tasks/?completed=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['completed'])

class AuthAPITestCase(APITestCase):
    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        User.objects.create_user(username='loginuser', password='loginpass123')
        
        data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
