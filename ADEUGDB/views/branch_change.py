
from django.contrib.auth.decorators import login_required, user_passes_test 
from ADAUGDB.user_access_test import is_Associate_Dean_Exams, branch_change_status_access
from django.shortcuts import render
from ADEUGDB.forms import  BranchChangeForm, BranchChangeStausForm
from ADEUGDB.models import BTBranchChanges
from BTExamStaffDB.models import BTStudentInfo
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Exams)
def branch_change(request):
    context={}
    if(request.method=='POST'):
        form = BranchChangeForm(request.POST)
        if request.POST.get('Submit'):
            if(form.is_valid()):
                regno = form.cleaned_data['RegNo']
                currentDept = form.cleaned_data['CurrentDept']
                newDept = form.cleaned_data['NewDept']
                ayear = form.cleaned_data['AYear']
                row = BTStudentInfo.objects.filter(RegNo=regno).first()
                if currentDept != newDept:
                    newRow = BTBranchChanges(student=row, CurrentDept=currentDept, NewDept=newDept, AYear=ayear)
                    newRow.save()
                    BTStudentInfo.objects.filter(RegNo=regno).update(Dept=newDept)
                    context['regno']=regno
                    context['Name'] = row.Name
                    context['dept'] = newDept
                    return render(request,'ADEUGDB/BTBranchChangeSuccess.html',context )
        else:
            student_info = BTStudentInfo.objects.filter(RegNo=request.POST.get('RegNo')).first()
            return render(request, 'ADEUGDB/BTBranchChange.html', {'form':form, 'student':student_info})
    else:
        form = BranchChangeForm()
    context['form']= form   
    return render(request,'ADEUGDB/BTBranchChange.html', context)

@login_required(login_url="/login/")
@user_passes_test(branch_change_status_access)
def branch_change_status(request):
    context={}
    if(request.method=='POST'):
        form = BranchChangeStausForm(request.POST)
        if(form.is_valid()):
            ayear = request.POST['AYear']
            results = BTBranchChanges.objects.filter(AYear=ayear)
            context['ayear'] = ayear
            context['rows'] = results
            return render(request, 'ADEUGDB/BTBranchChangeStatus.html', context)       
    else:
        form = BranchChangeStausForm()
    context['form'] = form
    return render(request, 'ADEUGDB/BTBranchChangeStatus.html', context)


def branch_change_script(file):
    import pandas as pd
    file = pd.read_csv(file)
    for _,row in file.iterrows():
        student = BTStudentInfo.objects.filter(RegNo=row['RegNo']).first()
        if not BTBranchChanges.objects.filter(student=student, CurrentDept=row['CurrentDept'], NewDept=row['NewDept'], AYear=row['AYear']).exists():
            branch_change = BTBranchChanges(student=student, CurrentDept=row['CurrentDept'], NewDept=row['NewDept'], AYear=row['AYear'])
            branch_change.save()
    return "Completed!!!"