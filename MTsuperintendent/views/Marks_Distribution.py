from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404 
from MTsuperintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from MTsuperintendent.forms import MarksDistributionForm
from MTsuperintendent.models import MTMarksDistribution


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_add(request):
    if request.method == 'POST':
        form = MarksDistributionForm(request.POST)
        if(form.is_valid()):
            Distribution = form.cleaned_data['Distribution']
            marksDistribution = form.cleaned_data['DistributionName']
            mark_distribution = MTMarksDistribution(Distribution=Distribution, DistributionNames=marksDistribution)
            mark_distribution.save()
            msg = 'Mark Distribution Added Successfully'
        return render(request, 'MTsuperintendent/MarksDistribution.html', {'form':form, 'msg':msg})
    else:
        form = MarksDistributionForm()
    return render(request, 'MTsuperintendent/MarksDistribution.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    mark_distribution = MTMarksDistribution.objects.all()
    if request.method == 'POST':
        if not 'Superintendent' in groups:
            raise Http404('You are not authorized to view this page.')
        if request.POST.get('delete'):
            id = request.POST['delete']
            mark_distribution.filter(id=id).delete()
            mark_distribution = MTMarksDistribution.objects.all()

    return render(request, 'MTsuperintendent/MarkDistributionStatus.html', {'distributions':mark_distribution})
