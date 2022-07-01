from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from ..forms import DeptElectiveRegsForm
from ..models import RegistrationStatus, RollLists_Staging, Subjects, StudentRegistrations_Staging
from SupExamDBRegistrations.user_access_test import registration_access

@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_all(request):
    subjects=[]
    if(request.method == "POST"):
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
        regId = request.POST['regID']
        subId = request.POST['subId']
        data = {'regID':regId, 'subId':subId}
        form = DeptElectiveRegsForm(subjects,data)
        if regId != '--Choose Event--' and subId != '--Select Subject--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id

            rolls = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
            for i in rolls:
                reg = StudentRegistrations_Staging(RegNo=i.student.RegNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            rolls = rolls.values_list('student__RegNo', flat=True)
            StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId).exclude(RegNo__in=rolls).delete()
            return render(request, 'SupExamDBRegistrations/Dec_Regs_success.html')
        elif regId != '--Choose Event--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            subjects = Subjects.objects.filter(RegEventId=currentRegEventId, Category='DEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            form = DeptElectiveRegsForm(subjects,data)
    else:
        form = DeptElectiveRegsForm()
    return render(request, 'SupExamDBRegistrations/Dec_register_all.html',{'form':form})