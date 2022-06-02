from typing import Set
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

from SupExamDBRegistrations.forms import GenerateRollListForm, RollListsCycleHandlerForm
from SupExamDBRegistrations.models import Regulation, StudentInfo, StudentInfoResource, NotPromoted, RollLists
from .home import is_Superintendent
from tablib import Dataset
from import_export.formats.base_formats import XLSX
# from datetime import date

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def generateRollList(request):
    if request.method == 'POST':
        form = GenerateRollListForm(request.POST)
        print(request.POST)
        if(form.is_valid()):
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            # print(form.cleaned_data['regID'])
            if(form.cleaned_data['regID']!='--Choose Event--'):
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation = int(strs[5])
                ayasbybsr = (ayear,asem,byear,bsem,regulation)
                mode = strs[6]
                if(byear==1):
                    reg_rgs = StudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept)
                    reg_rgs = [(row.RegNo,row.Dept,row.Cycle) for row in reg_rgs]
                    not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')
                    not_prom_regs = [row.RegNo for row in not_prom_regs]
                    final_not_prom_regs = []
                    for reg in not_prom_regs:
                        s_info = StudentInfo.objects.get(RegNo=reg)
                        if(s_info.Cycle==dept):
                            s_info.update(Regulation=regulation)
                            final_not_prom_regs.append(reg)
                    not_prom_regs = final_not_prom_regs
                    for row in reg_rgs:
                        roll = RollLists(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                        roll.save()
                    print(not_prom_regs)
                    if(len(not_prom_regs)!=0):
                        request.session['not_prom_regs'] = (not_prom_regs,ayasbybsr)
                        return HttpResponseRedirect(reverse('FirstYearRollListsCycleHandler' )) 
                    print(reg_rgs)
                    print("here")
                    print(not_prom_regs)
                    return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
                else:
                    reg_rgs = RollLists.objects.filter(AYear=ayear-1,Dept=dept,BYear=byear-1,Regulation=regulation)
                    reg_rgs = [(row.RegNo,row.Dept,row.Cycle) for row in reg_rgs]
                    present_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=byear, PoA='R')
                    present_not_prom_regs = [row.RegNo for row in present_not_prom_regs]
                    prev_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
                    prev_not_prom_regs = [row.RegNo for row in prev_not_prom_regs]
                    final_regs = []
                    for reg in reg_rgs:
                        if(reg not in prev_not_prom_regs):
                            final_regs.append(reg)
                    for reg in present_not_prom_regs:
                        s_info = StudentInfo.objects.get(RegNo=reg)
                        if(s_info.Regulation==regulation):
                            final_regs.append(reg)
                    for row in final_regs:
                        roll = RollLists(RegNo=row[0],Dept=row[1],AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                        roll.save()
                    return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
    else:
        form = GenerateRollListForm()
    return  render(request, 'SupExamDBRegistrations/generateRollList.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def first_year_rollLists_cycle_handler(request):
    not_prom_regs = request.session.get('not_prom_regs')[0]
    (ayear,asem,byear,bsem,regulation)=request.session.get('not_prom_regs')[1]
    print(ayear)
    if(request.method == 'POST'):
        form = RollListsCycleHandlerForm(not_prom_regs,request.POST)
        print("In post")
        if(form.is_valid()):
            print("valid")
            for cIndex, sReg in enumerate(not_prom_regs):
                print(cIndex,sReg)
                if(form.cleaned_data.get('RadioMode'+str(sReg))):
                    cycle = form.cleaned_data.get('RadioMode'+str(sReg))
                    s_info = StudentInfo.objects.get(RegNo=sReg)
                    roll = RollLists(RegNo=sReg, Dept=s_info.Dept, AYear=ayear, BYear=byear, Cycle=cycle, Regulation=regulation)
                    s_info.Cycle=cycle
                    print(s_info.Dept)
                    s_info.save()
                    roll.save()
                    print(roll.Dept,roll.RegNo,roll.AYear,roll.BYear, roll.Cycle)
        return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
    else:
        form = RollListsCycleHandlerForm(Options=not_prom_regs)
    return (render(request, 'SupExamDBRegistrations/RollListsCycleHandlerForm.html',{'form':form}))

