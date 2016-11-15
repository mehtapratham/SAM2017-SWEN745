from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, get_user, \
    REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import deprecate_current_app
from django.contrib.sites.shortcuts import get_current_site
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, resolve_url, \
    get_object_or_404
from django.template.context import RequestContext
from django.template.context_processors import request
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import UpdateView
from SAM2017.forms import *
from SAM2017.models import *


SAM_login_url = reverse_lazy("login")
home_page = reverse_lazy("home")

#index page, i.e. Homepage after log-in
@login_required(login_url=SAM_login_url)
def index(request):
    return render_to_response('common/index.html')

@login_required(login_url=SAM_login_url)	
def upload_paper(request):
    if request.POST:
        form = PaperForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            notification = Notification()
            #pcc = PCC.objects.get(id=2) - will get PCC when available
            users = [request.user] # sending notification to author temporarily
            notification.save()
            notification.sendNotification('NEW_PAPER', users)
            return HttpResponseRedirect('/papers/')
    else:
        form = PaperForm()
    args={}
    args.update(csrf(request))
    args['form']=form
    return render_to_response('common/upload-paper.html',args)

@login_required(login_url=SAM_login_url)
def view_papers(request):
    papers = Paper.objects.all()
    context = {'papers': papers}
    return render(request, 'common/view-papers.html', context, context_instance=RequestContext(request))

'''
def download_paper(request,papername):
    paper_name = papername
    response = HttpResponse(paper_name,content_type='')
    response['Content-Disposition']
'''


#Registration-----------------------------------------------------------------------
def register(request):
    if request.method == 'POST':

        # create a form instance and populate it with data from the request
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # entered form-data is validated against form-class rules
            # save user and sharezone to db
            form.save()
            # redirect to home page
            return redirect("/register/success")
        # else:
            # form-data did not validate against form-class rules
            # form innerhtml now contains any password error messages

    else:
        # GET request, so make a blank form instance
        form = UserCreationForm()

    # always, assign the form into the token
    token = {}
    token.update(csrf(request))
    token['form'] = form

    return render_to_response('common/registration.html', token)	
	
def register_complete(request):
    return render_to_response("common/registration_success.html")
	
	
	
	
# LOGIN -----------------------------------------------------------------------------
@deprecate_current_app
@sensitive_post_parameters()
@csrf_protect
@never_cache	
def login(request, template_name='common/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            """
            Added following if condition to manipulate
           
            if form.get_user().is_admin:
                redirect_to = "/admin/login/"
			"""
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, 'common/login.html', context)

def view_notifications(request):
    notifications = Notification.objects.filter(recipients = request.user)
    return render(request,'common/view-notifications.html',{'notifications':notifications})
#Review and Rating
def reviewRating(request):
    papers = Paper.objects.get(id=2)
    user = SAMUser.objects.get(id=2)
    if request.method == 'POST':

        # create a form instance and populate it with data from the request
        form = ReviewRateForm(data=request.POST)

        if form.is_valid():
            ReviewRating.reviwer = user.id
            ReviewRating.paper = papers.id
            #reviewer = form.cleaned_data['reviewer']
           # paper = form.cleaned_data['paper']
            review = form.cleaned_data['review']
            rating = form.cleaned_data['rating']
            #is_final = form.cleaned_data['is_final']
            form.save()

            # redirect to home page
            return render_to_response('common/index.html')
            #return redirect('https://localhost:8000')
            # else:
            # form-data did not validate against form-class rules
            # form innerhtml now contains any password error messages
    else:
        form = ReviewRateForm()

    token = {}
    token.update(csrf(request))
    token['form'] = form
    return render_to_response('common/review-rate.html',token)
