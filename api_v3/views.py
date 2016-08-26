from common.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET'])
@login_required
def private_view(request):
    return JsonResponse({'log': 'loggedin'})
