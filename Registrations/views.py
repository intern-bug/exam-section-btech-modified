from django.http.response import HttpResponse, HttpResponseRedirect
from Registrations.models import CoordinatorBacklogRegNos, CoordinatorMakeupRegNos, CoordinatorMakeupSubCodesV, StudentBacklogs, StudentMakeupBacklogs, StudentMakeupBacklogsVsRegistrations, StudentMakeupMarksDetails, StudentRegistrations,CurrentAcademicYear,CoordinatorInfo, StudentMakeupMarks, Coordinator1Info
from django.urls import reverse 
from Registrations.forms  import MarksForm, RegistrationForm1, RegistrationsInsertionForm, SimpleForm, StudentIDForm, RegistrationForm, TestForm
from django.shortcuts import render
from Transcripts.models import ProgrammeModel, StudentCGPAs, StudentInfo, ProgrammeModel
from Transcripts.models import DepartmentExamEvents
from Transcripts.models import DeptExamEventStudents
from Transcripts.models import StudentGradePoints
from Transcripts.models import StudentCGPAs
from Transcripts.models import HeldIn
from Transcripts.models import StudentExamEvents
from Transcripts.models import StudentAdmissionYearDetails
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Q

@login_required(login_url="/login/")


@login_required(login_url="/login/")
def private_place(request):
    return HttpResponse("Shhh, members only!", content_type="text/plain")

def is_coordinator(user):
    if(user.groups.filter(name='Coordinators')):
        return user.groups.filter(name='Coordinators').exists()
    else:
        return user.groups.filter(name='Coordinators1').exists()
    
def logout_request(request):
    logout(request)
    return render(request, 'registration/login.html')

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def index(request):
    return render(request, 'index.html')

# Create your views here.
@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def makeup_registrations(request):
    return render(request, 'Registrations/index.html')

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def makeup_registrations1(request):
    return render(request, 'Registrations/cindex.html')


@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def gp_home(request):
    return render(request, 'GradesProcessing/gphome.html')


@login_required(login_url="/login/")
def btech_regular_registrations(request):
    return render(request,'Registrations/BTechRegularRegistrations.html')

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def btech_makeup_registrations(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    studentRegNos = CoordinatorMakeupRegNos.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechMakeupRegistrations.html',{'studentRegNos': studentRegNos}  )

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def btech_backlog_registrations(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]

    studentRegNos = CoordinatorBacklogRegNos.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechBacklogRegistrations.html',{'studentRegNos': studentRegNos}  )


@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def btech_makeup_registrations1(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorSem1Details = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    coordinatorSem2Details = Coordinator1Info.objects.filter(UserId=request.user.username)[1]
    studentRegNos = CoordinatorMakeupRegNos.objects.filter(BYear=coordinatorSem1Details.Year).filter((Q(Dept=coordinatorSem1Details.Dept) & Q(BSem=coordinatorSem1Details.Sem ))| (Q(Dept=coordinatorSem2Details.Dept) & Q(BSem=coordinatorSem2Details.Sem))).order_by("RegNo")
    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BtechMakeupRegistrationsCycles.html',{'studentRegNos': studentRegNos}  )


@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def btech_makeup_registration_status(request):
    print(request.user.username)
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    studentMakeupBacklogsVsRegistrations = StudentMakeupBacklogsVsRegistrations.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    return render(request, 'Registrations/BTechMakeupRegistrationStatus.html',
                    { 'studentMakeupBacklogsVsRegistrations':studentMakeupBacklogsVsRegistrations }  )

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def btech_makeup_registration_status1(request):
    print(request.user.username)
    coordinatorSem1Details = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    coordinatorSem2Details = Coordinator1Info.objects.filter(UserId=request.user.username)[1]
    studentMakeupBacklogsVsRegistrations = StudentMakeupBacklogsVsRegistrations.objects.filter(BYear=coordinatorSem1Details.Year).filter((Q(Dept=coordinatorSem1Details.Dept) & Q(BSem=coordinatorSem1Details.Sem ))| (Q(Dept=coordinatorSem2Details.Dept) & Q(BSem=coordinatorSem2Details.Sem)))
    return render(request, 'Registrations/BTechMakeupRegistrationStatusCycle.html',
                    { 'studentMakeupBacklogsVsRegistrations':studentMakeupBacklogsVsRegistrations }  )


@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def test_form_view(request, regNo):
    if(request.method=='POST'):
        form = RegistrationsInsertionForm(request.POST)
        print(form.cleaned_data['checkBoxes'])    
    else:
        studentInfo = StudentInfo(RegNo=regNo)
        studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(RegNo=regNo)
        form = RegistrationsInsertionForm(regNo=studentInfo.RegNo,rollNo=studentInfo.RollNo, 
                                    name=studentInfo.Name)
    return render(request, 'Registrations/BTechMakeupRegistrationPage.html',{ 'studentMakeupBacklogs':studentMakeupBacklogs, 'studentInfo': studentInfo, 'form':form}  )


@login_required(login_url="/login/")
def btech_makeup_registration_page(request, regNo):
    #regNo = 952406
    print(request.user.username)
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    if(request.method=='POST'):
        studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
         
        choices = [(studentMakeupBacklogs[i].SubCode, 
                        studentMakeupBacklogs[i].SubCode + " " + 
                        studentMakeupBacklogs[i].SubName + " " +
                        str(studentMakeupBacklogs[i].Credits) + " " ) for i in range(len(studentMakeupBacklogs))]
        
        form = RegistrationForm(regNo,choices,[], request.POST)
        if(form.is_valid()):
            AYear=CurrentAcademicYear.objects.all()
            print(form.cleaned_data['Choices'])
            StudentRegistrations.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
            StudentMakeupMarks.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
            for choice in form.cleaned_data['Choices']:
                subjectTobeInserted = studentMakeupBacklogs.filter(SubCode=choice)
                newRegistration = StudentRegistrations(RegNo=subjectTobeInserted[0].RegNo,
                            SubCode=subjectTobeInserted[0].SubCode,
                            AYear=AYear[0].AcademicYear,
                            ASem=3,
                            OfferedYear=subjectTobeInserted[0].OfferedYear,
                            Dept=subjectTobeInserted[0].Dept,
                            BYear=subjectTobeInserted[0].BYear,
                            Regulation=subjectTobeInserted[0].Regulation,
                            BSem = subjectTobeInserted[0].BSem,
                            Mode = 0)

                if(StudentMakeupMarks.objects.filter(RegNo=regNo).exists()==1):

                    newRegistration2 = StudentMakeupMarks(RegNo=subjectTobeInserted[0].RegNo,
                                SubCode=subjectTobeInserted[0].SubCode,
                                AYear=AYear[0].AcademicYear,
                                ASem=3,
                                OfferedYear=subjectTobeInserted[0].OfferedYear,
                                Dept=subjectTobeInserted[0].Dept,
                                BYear=subjectTobeInserted[0].BYear,      
                                Marks=0,
                                Status=False,
                                Grade = 'F')
                    newRegistration2.save()
                newRegistration.save()
            

            

            return render(request, 'Registrations/success_page.html')    
    else:
        studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        studentRegistrations = StudentRegistrations.objects.filter(RegNo=regNo,AYear=2020,ASem=3)
        choices = [(studentMakeupBacklogs[i].SubCode,
                        studentMakeupBacklogs[i].SubCode + " " + 
                        studentMakeupBacklogs[i].SubName + " " +
                        str(studentMakeupBacklogs[i].Credits) + " " ) for i in range(len(studentMakeupBacklogs))]

        
       
        selection=[studentRegistrations[i].SubCode for i in range(len(studentRegistrations))]
       
        form = RegistrationForm(RegNo=studentInfo[0].RegNo, Options = choices, Selection=selection )
    return render(request, 'Registrations/test.html', {'form': form, })


@login_required(login_url="/login/")
def btech_makeup_registration_page1(request, regNo):
    #regNo = 952406
    print(request.user.username)
    coordinatorSem1Details = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    coordinatorSem2Details = Coordinator1Info.objects.filter(UserId=request.user.username)[1]
    if(request.method=='POST'):
        studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(RegNo=regNo).filter(BYear=coordinatorSem1Details.Year).filter((Q(Dept=coordinatorSem1Details.Dept) & Q(BSem=coordinatorSem1Details.Sem ))| (Q(Dept=coordinatorSem2Details.Dept) & Q(BSem=coordinatorSem2Details.Sem)))
        choices = [(studentMakeupBacklogs[i].SubCode, 
                        studentMakeupBacklogs[i].SubCode + " " + 
                        studentMakeupBacklogs[i].SubName + " " +
                        str(studentMakeupBacklogs[i].Credits) + " " ) for i in range(len(studentMakeupBacklogs))]
        
        form = RegistrationForm(regNo,choices,[], request.POST)
        if(form.is_valid()):
            AYear=CurrentAcademicYear.objects.all()
            print(form.cleaned_data['Choices'])
            StudentRegistrations.objects.filter(RegNo=regNo).filter(BYear=coordinatorSem1Details.Year).filter((Q(Dept=coordinatorSem1Details.Dept) & Q(BSem=coordinatorSem1Details.Sem ))| (Q(Dept=coordinatorSem2Details.Dept) & Q(BSem=coordinatorSem2Details.Sem))).delete()
            StudentMakeupMarks.objects.filter(RegNo=regNo).filter(BYear=coordinatorSem1Details.Year).filter(Dept=coordinatorSem1Details.Dept).filter(Dept=coordinatorSem2Details.Dept).delete()
            for choice in form.cleaned_data['Choices']:
                subjectTobeInserted = studentMakeupBacklogs.filter(SubCode=choice)
                newRegistration = StudentRegistrations(RegNo=subjectTobeInserted[0].RegNo,
                            SubCode=subjectTobeInserted[0].SubCode,
                            AYear=AYear[0].AcademicYear,
                            ASem=3,
                            OfferedYear=subjectTobeInserted[0].OfferedYear,
                            Dept=subjectTobeInserted[0].Dept,
                            BYear=subjectTobeInserted[0].BYear,
                            Regulation=subjectTobeInserted[0].Regulation,
                            BSem = subjectTobeInserted[0].BSem,
                            Mode = 0)
                

                newRegistration2 = StudentMakeupMarks(RegNo=subjectTobeInserted[0].RegNo,
                                SubCode=subjectTobeInserted[0].SubCode,
                                AYear=AYear[0].AcademicYear,
                                ASem=3,
                                OfferedYear=subjectTobeInserted[0].OfferedYear,
                                Dept=subjectTobeInserted[0].Dept,
                                BYear=subjectTobeInserted[0].BYear,      
                                Marks=0,
                                Status=False,
                                Grade = 'F',
                                Regulation=subjectTobeInserted[0].Regulation)
                newRegistration2.save()
                newRegistration.save()
            

            

            return render(request, 'Registrations/success_page1.html')    
    else:
        studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(RegNo=regNo).filter(BYear=coordinatorSem1Details.Year).filter((Q(Dept=coordinatorSem1Details.Dept) & Q(BSem=coordinatorSem1Details.Sem ))| (Q(Dept=coordinatorSem2Details.Dept) & Q(BSem=coordinatorSem2Details.Sem)))
        studentRegistrations = StudentRegistrations.objects.filter(RegNo=regNo,AYear=2020,ASem=3)
        choices = [(studentMakeupBacklogs[i].SubCode,
                        studentMakeupBacklogs[i].SubCode + " " + 
                        studentMakeupBacklogs[i].SubName + " " +
                        str(studentMakeupBacklogs[i].Credits) + " " ) for i in range(len(studentMakeupBacklogs))]

        
       
        selection=[studentRegistrations[i].SubCode for i in range(len(studentRegistrations))]
       
        form = RegistrationForm(RegNo=studentInfo[0].RegNo, Options = choices, Selection=selection )
    return render(request, 'Registrations/test3.html', {'form': form, })


@login_required(login_url="/login/")
def success_view(request):
    return HttpResponse('<p> <b> Successfull </b> </p>')

@login_required(login_url="/login/")
def btech_makeup_marks(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    studentSubCodes = CoordinatorMakeupSubCodesV.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).distinct("SubCode")

    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechMakeupMarks.html',{'studentSubCodes': studentSubCodes}  )

@login_required(login_url="/login/")

def btech_makeup_marks_page(request, SubCode):
    #regNo = 952406
    print(request.user.username)
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    if(request.method=='POST'):
        studentRegistrations = StudentMakeupMarks.objects.filter(SubCode=SubCode).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        selection=[studentRegistrations[i].Marks for i in range(len(studentRegistrations))]
        form = MarksForm(SubCode, studentRegistrations,selection, request.POST)
        if(form.is_valid()):
            AYear=CurrentAcademicYear.objects.all()           
            studentRegistrations= StudentMakeupMarks.objects.filter(SubCode=SubCode).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year)
            for rec in studentRegistrations:
                StudentMakeupMarks.objects.filter(RegNo=rec.RegNo,
                            SubCode=rec.SubCode).update(Marks= form.cleaned_data['marks'+str(rec.RegNo)])                
                #studentmakeupmarks.save()       

            
            return render(request, 'Registrations/success_page.html')    
    
    else:
        #studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(SubCode=SubCode).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        studentRegistrations = StudentMakeupMarks.objects.filter(SubCode=SubCode,AYear=2020, ASem=3, Dept=coordinatorDetails.Dept)     
        selection=[studentRegistrations[i].Marks for i in range(len(studentRegistrations))]
        form = MarksForm(SubCode=SubCode, studentRegistrations=studentRegistrations, Selection= selection )
    return render(request, 'Registrations/test2.html', {'form': form, })



@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def student_makeup_mark_status(request):
    print(request.user.username)
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    Studentmakeupmarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    
    return render(request, 'Registrations/StudentMakeupMarkStatus.html',
                    { 'studentmakeupmarks':Studentmakeupmarks }  )


@login_required(login_url="/login/")
def btech_makeup_results(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    studentSubCodes = CoordinatorMakeupSubCodesV.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).distinct('SubCode','Regulation')
    print(studentSubCodes)
    Studentmakeupmarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    subCodeValues = [r.SubCode+'_' + str(r.Regulation) for r in studentSubCodes]
    subCodeTexts = [r.SubName for r in studentSubCodes]
    subCodeData = [(subCodeValues[r],subCodeTexts[r]) for r in range(len(subCodeValues))]
    
    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechMakeupResults.html',{'subCodeData': subCodeData}  )

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def student_makeup_mark_results_page(request, SubCode):
    print(request.user.username)
    subCodeRegs = SubCode.split('_')
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    #studentMakeupMarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=SubCode)
    studentMakeupMarksDetails =StudentMakeupMarksDetails.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=subCodeRegs[0]).filter(Regulation=subCodeRegs[1])
    subjectInfo = StudentMakeupBacklogs.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=subCodeRegs[0]).filter(Regulation=subCodeRegs[1]).distinct()
    dept = ProgrammeModel.objects.filter(Dept=coordinatorDetails.Dept)
    
    return render(request, 'Registrations/BTechMakeupResultsPage.html',
                    { 'studentMakeupMarks':studentMakeupMarksDetails, 'subjectInfo':subjectInfo[0], 'dept':dept[0] })

@login_required(login_url="/login/")
def btech_makeup_marks1(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    studentSubCodes = CoordinatorMakeupSubCodesV.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).distinct("SubCode")

    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechMakeupMarksCycle.html',{'studentSubCodes': studentSubCodes}  )

@login_required(login_url="/login/")

def btech_makeup_marks_page1(request, SubCode):
    #regNo = 952406
    print(request.user.username)
    coordinatorDetails = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    if(request.method=='POST'):
        studentRegistrations = StudentMakeupMarks.objects.filter(SubCode=SubCode).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        selection=[studentRegistrations[i].Marks for i in range(len(studentRegistrations))]
        form = MarksForm(SubCode, studentRegistrations,selection, request.POST)
        if(form.is_valid()):
            AYear=CurrentAcademicYear.objects.all()           
            studentRegistrations= StudentMakeupMarks.objects.filter(SubCode=SubCode).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year)
            for rec in studentRegistrations:
                StudentMakeupMarks.objects.filter(RegNo=rec.RegNo,
                            SubCode=rec.SubCode).update(Marks= form.cleaned_data['marks'+str(rec.RegNo)])                
                #studentmakeupmarks.save()       

            
            return render(request, 'Registrations/success_page1.html')    
    
    else:
        #studentMakeupBacklogs = StudentMakeupBacklogs.objects.filter(SubCode=SubCode).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        studentRegistrations = StudentMakeupMarks.objects.filter(SubCode=SubCode,AYear=2020, ASem=3, Dept=coordinatorDetails.Dept)     
        selection=[studentRegistrations[i].Marks for i in range(len(studentRegistrations))]
        form = MarksForm(SubCode=SubCode, studentRegistrations=studentRegistrations, Selection= selection )
    return render(request, 'Registrations/test4.html', {'form': form, })



@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def student_makeup_mark_status1(request):
    print(request.user.username)
    coordinatorDetails = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    Studentmakeupmarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    
    return render(request, 'Registrations/StudentMakeupMarkStatusCycle.html',
                    { 'studentmakeupmarks':Studentmakeupmarks }  )


@login_required(login_url="/login/")
def btech_makeup_results1(request):
    #programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    coordinatorDetails = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    studentSubCodes = CoordinatorMakeupSubCodesV.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).distinct('SubCode','Regulation')
    print(studentSubCodes)
    Studentmakeupmarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
    subCodeValues = [r.SubCode+'_' + str(r.Regulation) for r in studentSubCodes]
    subCodeTexts = [r.SubName for r in studentSubCodes]
    subCodeData = [(subCodeValues[r],subCodeTexts[r]) for r in range(len(subCodeValues))]
    
    #admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Registrations/BTechMakeupResultsCycle.html',{'subCodeData': subCodeData}  )

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def student_makeup_mark_results_page1(request, SubCode):
    print(request.user.username)
    subCodeRegs = SubCode.split('_')
    coordinatorDetails = Coordinator1Info.objects.filter(UserId=request.user.username)[0]
    #studentMakeupMarks=StudentMakeupMarks.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=SubCode)
    studentMakeupMarksDetails =StudentMakeupMarksDetails.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=subCodeRegs[0]).filter(Regulation=subCodeRegs[1])
    subjectInfo = StudentMakeupBacklogs.objects.filter(BYear=coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept).filter(SubCode=subCodeRegs[0]).filter(Regulation=subCodeRegs[1]).distinct()
    dept = ProgrammeModel.objects.filter(Dept=coordinatorDetails.Dept)
    
    return render(request, 'Registrations/BTechMakeupResultsPageCycle.html',
                    { 'studentMakeupMarks':studentMakeupMarksDetails, 'subjectInfo':subjectInfo[0], 'dept':dept[0] })


@login_required(login_url="/login/")
def btech_backlog_registration_page(request, regNo):
    #regNo = 952406
    print(request.user.username)
    coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
    if(request.method=='POST'):
        studentBacklogs = StudentBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
        choices = [(studentBacklogs[i].SubCode, studentBacklogs[i].SubName, studentBacklogs[i].Credits,
                        studentBacklogs[i].Grade ) for i in range(len(studentBacklogs))]
        
        form = RegistrationForm1(regNo,choices,{}, request.POST)
        
        if(form.is_valid()):
            AYear=CurrentAcademicYear.objects.all()
            #print(form.cleaned_data['Choices'])
            StudentRegistrations.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
            StudentMakeupMarks.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
            for cIndex, choice in enumerate(choices):
                print(form.cleaned_data.get('RadioMode'+choice[0]))
                if(form.cleaned_data.get('Check'+choice[0])):
                    print(form.cleaned_data.get('Check'+choice[0]))
                    print(form.cleaned_data.get('RadioMode'+choice[0]))
                    
                    subjectTobeInserted = studentBacklogs.filter(SubCode=choice[0])
                    newRegistration = StudentRegistrations(RegNo=subjectTobeInserted[0].RegNo,
                                SubCode=subjectTobeInserted[0].SubCode,
                                AYear=2021,
                                ASem=1,
                                OfferedYear=subjectTobeInserted[0].OfferedYear,
                                Dept=subjectTobeInserted[0].Dept,
                                BYear=subjectTobeInserted[0].BYear,
                                Regulation=subjectTobeInserted[0].Regulation,
                                BSem = subjectTobeInserted[0].BSem,
                                Mode = form.cleaned_data.get('RadioMode'+choice[0]))
                    newRegistration.save()          
            return render(request, 'Registrations/success_page.html')    
        else:
            print('Form not valid in POST')
    else:
        AYear=CurrentAcademicYear.objects.all()
        studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        studentBacklogs = StudentBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)

        studentRegistrations = StudentRegistrations.objects.filter(RegNo=regNo,AYear=2021,ASem=1)
        choices = [(studentBacklogs[i].SubCode,studentBacklogs[i].Grade ) for i in range(len(studentBacklogs))]

        subDetails = [ (studentBacklogs[i].SubCode,
                        studentBacklogs[i].SubName, str(studentBacklogs[i].Credits), studentBacklogs[i].Grade) for i in range(len(studentBacklogs))]
       
        selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
       
        form = RegistrationForm1(RegNo=studentInfo[0].RegNo, Options = subDetails, Selection=selection )
        #print(form)

    return render(request, 'Registrations/test.html', {'form': form, 'subjectList':subDetails,'Name':studentInfo[0].Name,'RollNo':studentInfo[0].RollNo})


def test_form(request):
    form = TestForm()
    return render(request,'Registrations/test5.html', {'form': form, })
