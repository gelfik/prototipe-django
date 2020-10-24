from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from prototipe.models import test_for_user
from prototipe.views import get_user_all_stats
from django.contrib.auth.models import User
# Create your views here.

def profile(request):
    arguments = {}
    if request.user.is_authenticated:
        if request.method == "GET":
            test_for_user_object = test_for_user.objects.filter(user_id=request.user)
            arguments.update(tests=test_for_user_object)
            arguments.update(marksCanvas_data=get_user_all_stats(request.user))
            return render(request, 'userprofile/profile.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')