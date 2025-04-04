from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Experiment, ExperimentVariable, SimulationResult, Achievement, UserAchievement

class ExperimentModelTests(TestCase):
    def test_experiment_creation(self):
        experiment = Experiment.objects.create(
            id='test_experiment',
            title='Test Experiment',
            description='This is a test experiment',
            difficulty='beginner',
            duration='5-10 min',
            icon='test-icon'
        )
        self.assertEqual(experiment.title, 'Test Experiment')
        self.assertEqual(experiment.difficulty, 'beginner')

class ExperimentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.experiment = Experiment.objects.create(
            id='test_experiment',
            title='Test Experiment',
            description='This is a test experiment',
            difficulty='beginner',
            duration='5-10 min',
            icon='test-icon'
        )
        
        self.variable = ExperimentVariable.objects.create(
            experiment=self.experiment,
            name='test_var',
            display_name='Test Variable',
            min_value=0,
            max_value=100,
            default_value=50
        )
    
    def test_get_experiments_list(self):
        response = self.client.get('/api/experiments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Experiment')
    
    def test_get_experiment_detail(self):
        response = self.client.get(f'/api/experiments/{self.experiment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Experiment')
        self.assertEqual(len(response.data['variables']), 1)
        self.assertEqual(response.data['variables'][0]['name'], 'test_var')

class SimulationResultAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.experiment = Experiment.objects.create(
            id='test_experiment',
            title='Test Experiment',
            description='This is a test experiment',
            difficulty='beginner',
            duration='5-10 min',
            icon='test-icon'
        )
    
    def test_create_simulation_result(self):
        data = {
            'experiment': self.experiment.id,
            'variables_config': {
                'light': 50,
                'co2': 50,
                'water': 50,
                'temperature': 25
            },
            'results_data': {
                'oxygenProduced': 25.5,
                'glucoseProduced': 15.3,
                'plantGrowth': 10.2,
                'efficiency': 0.85
            },
            'duration': 300,
            'notes': 'This is a test simulation'
        }
        
        response = self.client.post('/api/results/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SimulationResult.objects.count(), 1)
        self.assertEqual(SimulationResult.objects.get().user, self.user)
