from django.shortcuts import render
from django.http import HttpResponseRedirect
from SAM2017.forms import PaperForm
from SAM2017.models import Paper
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext

# Create your views here.

def index(request):
    return render(request, 'SAM2017/index.html', context_instance=RequestContext(request))

def upload_paper(request):
    if request.POST:
        form = PaperForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('SAM2017/papers')
    else:
        form = PaperForm()
    args={}
    args.update(csrf(request))
    args['form']=form
    return render_to_response('SAM2017/upload-paper.html',args)

def view_papers(request):
    papers = Paper.objects.all()
    context = {'papers': papers}
    return render(request, 'SAM2017/view-papers.html', context, context_instance=RequestContext(request))

