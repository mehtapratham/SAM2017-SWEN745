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
from django.views.generic.edit import UpdateView
from SAM2017.forms import *
from SAM2017.models import *
import json
from django.utils.encoding import smart_str

import functools
import warnings

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.deprecation import (
    RemovedInDjango20Warning, RemovedInDjango110Warning,
)
from django.utils.encoding import force_text
from django.utils.http import is_safe_url, urlsafe_base64_decode
# from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters



from django.http import HttpResponse

SAM_login_url = reverse_lazy("login")
home_page = reverse_lazy("home")

#index page, i.e. Homepage after log-in
@login_required(login_url=SAM_login_url)
def index(request):
    if request.user.is_admin:
        return HttpResponseRedirect('/sam/admin/accounts/')

    u_id=request.user.id
    token={}
    if(PCC.objects.filter(id = u_id)):
        token['papers'] = Paper.objects.all()
        token['papers_assigned'] = papers_selection.objects.filter(decisions=True)
        token['papers_reviewed'] = ReviewRating.objects.all()
        return render_to_response('common/pcc_home.html',token)
    elif(PCM.objects.filter(id = u_id)):
        token['papers'] = Paper.objects.all()
        return render_to_response('common/pcm_home.html',token)
    return render_to_response('common/index.html')


@login_required(login_url=SAM_login_url)
def pcc_home(request):
    id=request.user.id
    return render_to_response('common/pcc_home.html')

@login_required(login_url=SAM_login_url)
def upload_paper(request):
    if request.POST:
        form = PaperForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            notification = Notification()
            users = PCC.objects.first()
            recipient = [users]
            notification.save()
            notification.sendNotification('NEW_PAPER', recipient)
            return HttpResponseRedirect('/papers/')
    else:
        form = PaperForm()
    args={}
    args.update(csrf(request))
    args['form']=form
    print(request.user.id)
    args['userid']=request.user.id
    return render_to_response('common/upload-paper.html',args)


@login_required(login_url=SAM_login_url)
def upload_another_version(request, paperId):
    paper = Paper.objects.get(id=paperId)
    if request.POST:
        form = VersionForm(request.POST,request.FILES)
        if form.is_valid():
            paper.file = form.cleaned_data['file']
            paper.version += 1
            paper.save()
            notification = Notification()
            users = PCC.objects.first()
            recipient = [users]
            notification.save()
            notification.sendNotification('NEW_PAPER', recipient)
            return HttpResponseRedirect('/papers/')
    else:
        form = VersionForm()
    args={}
    args.update(csrf(request))
    args['form']=form
    print(request.user.id)
    args['userid']=request.user.id
    return render_to_response('common/upload_version.html',args)


@login_required(login_url=SAM_login_url)
def paper_details_author(request,paperId):
    paper = Paper.objects.get(id=paperId)
    token={}
    reviews=ReviewRating.objects.filter(paper_id=paperId)
    author=SAMUser.objects.get(id=paper.authors_id)
    token['pcm']=PCM.objects.all()
    token['paper']=paper
    token['user_id']=request.user.id
    token['author'] = author
    token['reviews']=reviews
    return render_to_response('common/paper_details_author.html',token)

@login_required(login_url=SAM_login_url)
def view_papers(request):
    author_id=request.user.id
    paper_ids = Paper.objects.filter(authors=author_id)
    context = {'papers': paper_ids}
    return render(request, 'common/view-papers.html', context, context_instance=RequestContext(request))

@login_required(login_url=SAM_login_url)
def paper_assignment_pcc(request):
    token={}
    papers = Paper.objects.filter(numofreviewers__lte=2)
    token['papers'] = papers
    return render_to_response("common/paper_assignment_pcc.html",token)

@login_required(login_url=SAM_login_url)
def paper_selected_to_assign(request,paperId):
    token={}
    reviewers=[]
    paper = Paper.objects.get(id=paperId)
    list_of_reviewers = PCM.objects.all().exclude(id=paper.authors_id)
    for li in list_of_reviewers:
        abc = papers_selection.objects.filter(selected_paper_id=paperId).filter(pcm_id=li.id).filter(decisions=True)
        if abc:
            print('')
        else:
            reviewers.append(li)
    token['paper'] = paper
    token['reviewers'] = reviewers
    return render_to_response("common/paper_selected_to_assign.html",token)

@login_required(login_url=SAM_login_url)
def assigned_reviewer(request, paperId,reviewerId):
    token={}
    paper=Paper.objects.get(id=paperId)
    reviewer=PCM.objects.get(id=reviewerId)
    new_add = papers_selection.objects.create(decisions=True,selected_paper_id=paperId,pcm_id=reviewerId)
    paper.numofreviewers = paper.numofreviewers + 1
    paper.save()
    return render_to_response("common/assigned_reviewer.html",token)

@login_required(login_url=SAM_login_url)
def paper_selection_pcm(request):
    token={}
    new_paper_list=[]
    paper_list = Paper.objects.filter(numofreviewers__lte= 2).exclude(authors_id=request.user.id)
    for paper in paper_list:
        pap=papers_selection.objects.filter(selected_paper_id=paper.id).filter(pcm_id=request.user.id)
        if pap:
            print('')
        else:
            new_paper_list.append(paper)
    token['paper_list']=new_paper_list
    return render_to_response('common/paper_selection.html',token)

@login_required(login_url=SAM_login_url)
def request_to_review(request,paperId):
    pcm_user = request.user.id
    pap = paperId
    papers_selection.create(pcm_user,pap)
    return render_to_response('common/paper_selection_success.html')

@login_required(login_url=SAM_login_url)
def review_papers_pcm(request):
    pcm_user = request.user.id
    list_of_papers = papers_selection.objects.filter(pcm_id=pcm_user).filter(decisions=True)
    token={}
    papers=[]
    for paper in list_of_papers:
        pap = Paper.objects.get(id=paper.selected_paper_id)
        papers.append(pap)
    token['papers'] = papers
    return render_to_response('common/review_papers_pcm.html',token)

@login_required(login_url=SAM_login_url)
def selected_to_review_pcm(request,paperId):
    pap = Paper.objects.get(id=paperId)
    token={}
    token['paper']=pap
    return render_to_response("common/selected_to_review_pcm.html",token)


@login_required(login_url=SAM_login_url)
def paper_details(request,paperId):
    paper = Paper.objects.get(id=paperId)
    user_type_pcc = PCC.objects.filter(id=request.user.id)
    user_type_pcm = PCM.objects.filter(id=request.user.id)
    token={}
    author=SAMUser.objects.get(id=paper.authors_id)
    token['paper']=paper
    token['user_id']=request.user.id
    token['user_type_pcc'] = user_type_pcc
    token['author'] = author
    if user_type_pcc:
        return render_to_response('common/paper-details.html', token)
    elif user_type_pcm:
        paper_selec = papers_selection.objects.filter(pcm_id=request.user.id).filter(selected_paper_id=paperId)
        token['paper_selected']=paper_selec
    return render_to_response('common/paper-details.html',token)


def download_paper(request, papername):
    paper = open(settings.MEDIA_ROOT +'/uploaded_files/' + papername, 'rb').read()
    response = HttpResponse(paper, content_type='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % smart_str(papername)
    # response['X-Sendfile'] = smart_str(settings.MEDIA_ROOT +'/uploaded_files/' + papername)
    return response


@login_required(login_url=SAM_login_url)
def paper_details_pcc(request,paperId):
    paper = Paper.objects.get(id=paperId)
    requester = papers_selection.objects.filter(selected_paper_id=paperId).filter(decisions = False)
    print(paperId)
    token={}
    token['paper']=paper
    token['requesters']=requester
    paper_selec = papers_selection.objects.filter(pcm_id=request.user.id)
    paper_selec.filter(selected_paper_id=paperId)
    token['paper_selected']=paper_selec
    return render_to_response('common/paper-details_pcc.html',token)

@login_required(login_url=SAM_login_url)
def view_requests_pcc(request):
    token={}
    token['paper_selected'] = papers_selection.objects.filter(decisions=False)
    return render_to_response("common/view_requests_pcc.html",token)

@login_required(login_url=SAM_login_url)
def paper_approve(request,Id):
    pap = papers_selection.objects.get(id=Id)
    paper = Paper.objects.get(id=pap.selected_paper_id)
    token = {}
    token['paper'] = paper
    num_of_reviewers = paper.numofreviewers
    paper.numofreviewers = num_of_reviewers+1
    paper.save()
    pap.decisions = True
    pap.save()
    requester = papers_selection.objects.filter(selected_paper_id=pap.selected_paper_id).filter(decisions=False)
    token['requesters']=requester
    paper_selec=papers_selection.objects.filter(pcm_id=request.user.id)
    paper_selec.filter(selected_paper_id=paper.id)
    token['paper_selected']=paper_selec
    return render_to_response('common/paper-details_pcc.html',token)

@login_required(login_url=SAM_login_url)
def paper_reject(request,Id):
    pap = papers_selection.objects.get(id=Id)
    paper = Paper.objects.get(id=pap.selected_paper_id)
    pap.delete()
    token={}
    token['paper']=paper
    requester = papers_selection.objects.filter(selected_paper_id=paper.id).filter(decisions=False)
    token['requesters']=requester
    paper_selec=papers_selection.objects.filter(pcm_id=request.user.id)
    paper_selec.filter(selected_paper_id=paper.id)
    token['paper_selected']=paper_selec
    return render_to_response('common/paper-details_pcc.html',token)

@login_required(login_url=SAM_login_url)
def promote_to_pcm(request):
    allusers=SAMUser.objects.all().exclude(id=request.user.id)
    authors=[]
    for user in allusers:
        check_pcm=PCM.objects.filter(id=user.id)
        if check_pcm:
            print('')
        else:
            authors.append(user)
    token={}
    token['authors']=authors
    return render_to_response("common/promote_to_pcm.html",token)

@login_required(login_url=SAM_login_url)
def promote_author(request,uid):
    user = SAMUser.objects.get(id=uid)
    pcm = PCM(samuser_ptr_id=user.id)
    pcm.__dict__.update(user.__dict__)
    pcm.save()
    return redirect(resolve_url('promote_to_pcm'))

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
def reviewRating(request,paperId):
    papers = Paper.objects.get(id=paperId)
    user = request.user
    if request.method == 'POST':

        # create a form instance and populate it with data from the request
        form = ReviewRateForm(data=request.POST)

        if form.is_valid():
            new = ReviewRating(reviwer_id = user.id,paper_id = papers.id,review = form.cleaned_data["review"],rating = form.cleaned_data["rating"])
            new.save()
            token = {}
            author = SAMUser.objects.get(id=papers.authors_id)
            token['pcm'] = PCM.objects.all()
            token['paper'] = papers
            token['user_id'] = request.user.id
            token['author'] = author
            token['review'] = new
            return render_to_response('common/paper_details_pcm.html',token)

    else:
        form = ReviewRateForm()

    token = {}
    token['paper'] = papers
    token.update(csrf(request))
    token['form'] = form
    return render_to_response('common/review-rate.html',token)

def view_paper_details(request,paperId):
    paper = Paper.objects.get(pk = paperId)
    context = {'paper' : paper}
    return render(request,"common/view-paper-detail.html",context)

def view_deadlines(request):
    deadlines = Deadline.objects.all()
    deadline_dict={ 'PSD': "Paper Submission Deadline",
                    'RCD': "Review Choice Deadline",
                    'RSD': "Review Submission Deadline",
                    'AND': "Author notification Deadline"
                  }
    context = {'deadlines':deadlines,'mapper':deadline_dict}
    return render(request,'common/view_deadlines.html',context)

@login_required(login_url=SAM_login_url)
def update_deadlines(request):

    if request.POST:

        selectedPSDDeadline = (request.POST.get('psdDeadlineId'))
        if selectedPSDDeadline is not None:
            deadline_1 = Deadline.objects.get(deadline_type='PSD')
            deadline_1.deadline_date = selectedPSDDeadline
            deadline_1.save()
            notification = Notification()

            allusers = SAMUser.objects.all().exclude(is_admin=1)
            pcc = PCC.objects.all()
            for user in pcc:
                allusers = allusers.exclude(id=user.id)

            recipients = allusers
            notification.sendNotification("Paper_Submission_Deadline", deadline_1.id, recipients)

        selectedRCDDeadline = (request.POST.get('rcdDeadlineId'))
        if selectedRCDDeadline is not None:
            deadline_2 = Deadline.objects.get(deadline_type='RCD')
            deadline_2.deadline_date = selectedRCDDeadline
            deadline_2.save()
            notification = Notification()

            pcm = PCM.objects.all()

            recipients = pcm

            notification.sendNotification("Review_Choice_Deadline", deadline_2.id, recipients)

        selectedRSDDeadline = (request.POST.get('rsdDeadlineId'))
        if selectedRSDDeadline is not None:
            deadline_3 = Deadline.objects.get(deadline_type='RSD')
            deadline_3.deadline_date = selectedRSDDeadline
            deadline_3.save()
            notification = Notification()

            pcm = PCM.objects.all()

            recipients = pcm

            notification.sendNotification("Review_Submission_Deadline", deadline_3.id, recipients)


        selectedANDDeadline = (request.POST.get('andDeadlineId'))
        if selectedANDDeadline is not None:
            deadline_4 = Deadline.objects.get(deadline_type='AND')
            deadline_4.deadline_date = selectedANDDeadline
            deadline_4.save()
            # notification = Notification()
            # recipients = [SAMUser]
            # notification.sendNotification("Auther_Submission_Deadline", and_deadline.id, recipients)

        return HttpResponseRedirect('/deadlines/')
    else:
        deadline_1 = get_object_or_404(Deadline,deadline_type='PSD')
        deadline_2 = get_object_or_404(Deadline,deadline_type='RCD')
        deadline_3 = get_object_or_404(Deadline,deadline_type='RSD')
        deadline_4 = get_object_or_404(Deadline,deadline_type='AND')

        args={}
        args.update(csrf(request))
        args['psd_deadline_date'] = deadline_1.deadline_date
        args['rcd_deadline_date'] = deadline_2.deadline_date
        args['rsd_deadline_date'] = deadline_3.deadline_date
        args['and_deadline_date'] = deadline_4.deadline_date

    return render_to_response('common/update_deadlines.html',args, context_instance=RequestContext(request))


#Admin-----------------------------------------
@login_required(login_url=SAM_login_url)
def accounts(request):
    authors = SAMUser.objects.filter().exclude(is_admin=1)

    pcc = PCC.objects.all()
    pcm = PCM.objects.all()
    admins = SAMUser.objects.filter(is_admin=1)

    for user in pcc:
        authors = authors.exclude(id = user.id)

    for user in pcm:
        authors = authors.exclude(id = user.id)

    args = {}
    args['authors'] = authors
    args['pcc'] = pcc
    args['pcm'] = pcm
    args['admins'] = admins
    return render_to_response("common/admin_manage_accounts.html", args, context_instance=RequestContext(request) )


def deleteUser(request, userId):
    user = SAMUser.objects.filter(id = userId)
    user.delete()

    response_data = {}
    response_data['success'] = 1
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def promoteAuthor(request, userId):
    user = SAMUser.objects.get(id = userId)

    pcm = PCM(samuser_ptr_id=user.id)
    pcm.__dict__.update(user.__dict__)
    pcm.save()
    response_data = {}
    response_data['success'] = 1
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def demotePCM(request, userId):
    user = PCM.objects.get(id = userId)
    user.delete()
    response_data = {}
    response_data['success'] = 1
    return HttpResponse(json.dumps(response_data), content_type="application/json")
