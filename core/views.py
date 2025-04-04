from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import BoiSimPoint, HistoricalDialoguesPoint
import json

@method_decorator(csrf_exempt, name='dispatch')
class BoiSimPointsView(View):
    """Class-based view to manage BoiSimPoints for the logged-in user."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            points = BoiSimPoint.objects.filter(user=request.user).values('id', 'point', 'created_at', 'updated_at')
            return JsonResponse({'points': list(points)}, safe=False)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                point = int(data.get('point', 0))
                BoiSimPoint.objects.create(user=request.user, point=point)
                return JsonResponse({'message': 'Point saved successfully'}, status=201)
            except (ValueError, TypeError, json.JSONDecodeError):
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                point_id = data.get('id')
                new_point = int(data.get('point', 0))
                point_instance = BoiSimPoint.objects.filter(id=point_id, user=request.user).first()
                if point_instance:
                    point_instance.point = new_point
                    point_instance.save()
                    return JsonResponse({'message': 'Point updated successfully'}, status=200)
                return JsonResponse({'error': 'Point not found'}, status=404)
            except (ValueError, TypeError, json.JSONDecodeError):
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class HistoricalDialoguesPointsView(View):
    """Class-based view to manage HistoricalDialoguesPoints for the logged-in user."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            points = HistoricalDialoguesPoint.objects.filter(user=request.user).values('id', 'point', 'created_at', 'updated_at')
            return JsonResponse({'points': list(points)}, safe=False)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                point = int(data.get('point', 0))
                HistoricalDialoguesPoint.objects.create(user=request.user, point=point)
                return JsonResponse({'message': 'Point saved successfully'}, status=201)
            except (ValueError, TypeError, json.JSONDecodeError):
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                point_id = data.get('id')
                new_point = int(data.get('point', 0))
                point_instance = HistoricalDialoguesPoint.objects.filter(id=point_id, user=request.user).first()
                if point_instance:
                    point_instance.point = new_point
                    point_instance.save()
                    return JsonResponse({'message': 'Point updated successfully'}, status=200)
                return JsonResponse({'error': 'Point not found'}, status=404)
            except (ValueError, TypeError, json.JSONDecodeError):
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=401)