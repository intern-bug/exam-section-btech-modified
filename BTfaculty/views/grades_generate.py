from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from ADAUGDB.user_access_test import grades_threshold_access, grades_status_access
from ADAUGDB.models import BTRegistrationStatus, BTOpenElectiveRollLists
from ADAUGDB.models import BTCycleCoordinator, BTHOD
from BThod.models import BTFaculty_user, BTCoordinator
from BTco_ordinator.models import BTFacultyAssignment, BTRollLists, BTStudentRegistrations, BTSubjects
from BTfaculty.models import BTAttendance_Shortage, BTGradesThreshold, BTMarks_Staging, BTStudentGrades_Staging
from BTExamStaffDB.models import BTIXGradeStudents
from BTfaculty.forms import MarksStatusForm
from django.db import transaction
from django.db.models import Q

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_generate(request):

    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, GradesStatus=1, RegEventId__Status=1, RegEventId__GradeStatus=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            if regEvent.startswith('OE'):
                regEvent = regEvent[2:].split(',')
                regEvent = [int(_) for _ in regEvent]
                subject = subject.split(',')
                subject = [int(_) for _ in subject]
                oe_rolls = BTOpenElectiveRollLists.objects.filter(RegEventId__in=regEvent, subject_id__in=subject, Section=section)
                marks_objects = BTMarks_Staging.objects.filter(Registration__student__student__id__in=oe_rolls.values_list('student__student__id', flat=True),\
                    Registration__sub_id_id__in=subject, Registration__RegEventId_id__in=regEvent)
                subject_obj = BTSubjects.objects.get(id=subject[0])
                regEvent = BTRegistrationStatus.objects.get(id=regEvent[0])
            else:
                regEvent = BTRegistrationStatus.objects.get(id=regEvent)
                marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId_id=regEvent.id, Registration__sub_id__course_id=subject, \
                    Registration__student__Section=section).order_by('Registration__student__student__RegNo')
                subject_obj = marks_objects.first().Registration.sub_id
            
            promote_thresholds = subject_obj.course.MarkDistribution.PromoteThreshold
            promote_thresholds = promote_thresholds.split(',')
            promote_thresholds = [thr.split('+') for thr in promote_thresholds]

            attendance_shortage = BTAttendance_Shortage.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
            grades_objects = BTStudentGrades_Staging.objects.filter(RegId_id__in=marks_objects.values_list('Registration', flat=True))
            
            for att in attendance_shortage:
                if grades_objects.filter(RegId_id=att.Registration.id):
                    grades_objects.filter(RegId_id=att.Registration.id).update(Grade='R', AttGrade='X')
                else:
                    grade = BTStudentGrades_Staging(RegId_id=att.Registration.id, RegEventId=att.Registration.RegEventId.id, Regulation=att.Registration.RegEventId.Regulation, \
                        Grade='R', AttGrade='X') 
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=att.Registration)
            
            ix_grades = BTIXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))

            for ix_grade in ix_grades:
                if grades_objects.filter(RegId=ix_grade.Registration.id):
                    grades_objects.filter(RegId=ix_grade.Registration.id).update(Grade=ix_grade.Grade, AttGrade='P')
                else:
                    grade = BTStudentGrades_Staging(RegId_id=ix_grade.Registration.id, RegEventId=att.Registration.RegEventId.id, Regulation=att.Registration.RegEventId.Regulation, \
                        Grade=ix_grade.Grade, AttGrade='P')
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
            
            if BTGradesThreshold.objects.filter(Subject_id=subject_obj.id, RegEventId=regEvent).exists():
                thresholds_study_mode = BTGradesThreshold.objects.filter(Subject_id=subject_obj.id, RegEventId=regEvent, Exam_Mode=False).order_by('-Threshold_Mark')
                thresholds_exam_mode = BTGradesThreshold.objects.filter(Subject_id=subject_obj.id, RegEventId=regEvent, Exam_Mode=True).order_by('-Threshold_Mark')
            
            if not thresholds_study_mode or not thresholds_exam_mode:
                msg = 'Grade Threshold(study/exam) is not updated for this subject.'
                return render(request, 'BTfaculty/GradesGenerate.html', {'form':form, 'msg':msg})

            for mark in marks_objects:
                if mark.Registration.Mode == 1:
                    marks_list = mark.Marks.split(',')
                    marks_list = [m.split('+') for m in marks_list]
                    graded = False
                    for outer_index in range(len(promote_thresholds)):
                        for inner_index in range(len(promote_thresholds[outer_index])):
                            if float(marks_list[outer_index][inner_index]) < float(promote_thresholds[outer_index][inner_index]):
                                graded = True
                                if grades_objects.filter(RegId_id=mark.Registration.id):
                                    grades_objects.filter(RegId_id=mark.Registration.id).update(Grade='F', AttGrade='P')
                                    break
                                else:
                                    grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                        Grade='F', AttGrade='P')
                                    grade.save()
                                    break
                        if graded:
                            break
                    if not graded:
                        for threshold in thresholds_study_mode:
                            if mark.TotalMarks >= threshold.Threshold_Mark:
                                if grades_objects.filter(RegId_id=mark.Registration.id):
                                    grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='P')
                                    break
                                else:
                                    grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                        Grade=threshold.Grade.Grade, AttGrade='P')
                                    grade.save()
                                    break
                else:
                    for threshold in thresholds_exam_mode:
                        if mark.TotalMarks >= threshold.Threshold_Mark:
                            if grades_objects.filter(RegId_id=mark.Registration.id):
                                grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='X')
                                break
                            else:
                                grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                        Grade=threshold.Grade.Grade, AttGrade='X')
                                grade.save()
                                break
            
            msg = 'Grades generated successfully.'
            return render(request, 'BTfaculty/GradesGenerate.html', {'form':form, 'msg':msg})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'BTfaculty/GradesGenerate.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(grades_status_access)
def grades_status(request):
    
    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    subjects = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    elif 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter((Q(RegEventId__Dept=co_ordinator.Dept)|Q(Faculty__Dept=co_ordinator.Dept)), RegEventId__BYear=co_ordinator.BYear, RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter((Q(RegEventId__Dept=co_ordinator.Dept)|Q(Faculty__Dept=co_ordinator.Dept)), RegEventId__Status=1)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__BYear=1, RegEventId__Dept=cycle_cord.Cycle)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            if regEvent.startswith('OE'):
                regEvent = regEvent[2:].split(',')
                regEvent = [int(_) for _ in regEvent]
                subject = subject.split(',')
                subject = [int(_) for _ in subject]
                oe_rolls = BTOpenElectiveRollLists.objects.filter(RegEventId_id__in=regEvent, subject_id__in=subject, Section=section)
                grades = BTStudentGrades_Staging.objects.filter(RegId__sub_id_id__in=subject, RegId__student__student__in=oe_rolls.values_list('student__student', flat=True))
                grades = list(grades)
            else:
            # roll_list = BTRollLists.objects.filter(RegEventId=regEvent, Section=section)
            # student_registrations = BTStudentRegistrations.objects.filter(RegEventId_id=regEvent.id, sub_id_id=subject, \
            #     student__student__RegNo__in=roll_list.values_list('student__RegNo', flat=True))
                grades = BTStudentGrades_Staging.objects.filter(RegEventId=regEvent, RegId__sub_id__course_id=subject, RegId__student__Section=section)
                grades = list(grades)
            for grade in grades:
                grade.RegNo = grade.RegId.student.student.RegNo
                grade.regEvent = grade.RegId.RegEventId.__str__()
                grade.Marks = BTMarks_Staging.objects.filter(Registration_id=grade.RegId_id).first().TotalMarks
            import operator
            grades = sorted(grades, key=operator.attrgetter('RegNo'))
            return render(request, 'BTfaculty/GradesStatus.html', {'form':form, 'grades':grades})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'BTfaculty/GradesStatus.html', {'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_hod_submission(request):
    
    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, GradesStatus=1, RegEventId__Status=1, RegEventId__GradeStatus=1)
    msg = ''
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            if regEvent.startswith('OE'):
                regEvent = regEvent[2:].split(',')
                regEvent = [int(_) for _ in regEvent]
                subject = subject.split(',')
                subject = [int(_) for _ in subject]
                fac_assign_objs = subjects.filter(Subject_id__in=subject, RegEventId_id__in=regEvent, Section=section)
            else:
               fac_assign_objs = subjects.filter(Subject__course_id=subject, RegEventId_id=regEvent, Section=section)
            for fac_assign_obj in fac_assign_objs:
                fac_assign_obj.GradesStatus = 0
                fac_assign_obj.save()
            msg = 'Grades have been submitted to HOD successfully.'
    else:
        form = MarksStatusForm(subjects)
    return render(request, 'BThod/GradesFinalize.html', {'form':form, 'msg':msg})

def generate_grades(**kwargs):
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
            return "No Events!!!!"
    error_events=[]
    for event in regEvents:
        marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId_id=event.id)
        subject_objects = BTSubjects.objects.filter(id__in=marks_objects.values_list('Registration__sub_id_id', flat=True))
        attendance_shortage = BTAttendance_Shortage.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
        grades_objects = BTStudentGrades_Staging.objects.filter(RegId_id__in=marks_objects.values_list('Registration', flat=True))
        for att in attendance_shortage:
            if grades_objects.filter(RegId_id=att.Registration.id):
                grades_objects.filter(RegId_id=att.Registration.id).update(Grade='R', AttGrade='X')
            else:
                grade = BTStudentGrades_Staging(RegId_id=att.Registration.id, RegEventId=att.Registration.RegEventId.id, Regulation=att.Registration.RegEventId.Regulation, \
                    Grade='R', AttGrade='X') 
                grade.save()
            marks_objects = marks_objects.exclude(Registration=att.Registration)
        ix_grades = BTIXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
        for ix_grade in ix_grades:
                if grades_objects.filter(RegId_id=ix_grade.Registration.id):
                    grades_objects.filter(RegId_id=ix_grade.Registration.id).update(Grade=ix_grade.Grade, AttGrade='P')
                else:
                    grade = BTStudentGrades_Staging(RegId_id=ix_grade.Registration.id, RegEventId=ix_grade.Registration.RegEventId.id, Regulation=ix_grade.Registration.RegEventId.Regulation, \
                        Grade=ix_grade.Grade, AttGrade='P')
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
        
        for mark in marks_objects:
            subject = subject_objects.filter(id=mark.Registration.sub_id.id).first()
            if mark.Registration.Mode == 1:
                thresholds = BTGradesThreshold.objects.filter(Subject_id=subject.id, RegEventId=mark.Registration.RegEventId, Exam_Mode=False).order_by('-Threshold_Mark', 'Grade_id')
            else:
                thresholds = BTGradesThreshold.objects.filter(Subject_id=subject.id, RegEventId=mark.Registration.RegEventId, Exam_Mode=True).order_by('-Threshold_Mark', 'Grade_id')
            if not thresholds:
                error_events.append((event, subject.course.SubCode))
            if mark.Registration.Mode == 1:
                promote_thresholds = subject.course.MarkDistribution.PromoteThreshold
                promote_thresholds = promote_thresholds.split(',')
                promote_thresholds = [thr.split('+') for thr in promote_thresholds]
                marks_list = mark.Marks.split(',')
                marks_list = [m.split('+') for m in marks_list]
                graded = False
                for outer_index in range(len(promote_thresholds)):
                    for inner_index in range(len(promote_thresholds[outer_index])):
                        if float(marks_list[outer_index][inner_index]) < float(promote_thresholds[outer_index][inner_index]):
                            graded = True
                            if grades_objects.filter(RegId_id=mark.Registration.id):
                                grades_objects.filter(RegId_id=mark.Registration.id).update(Grade='F', AttGrade='P')
                                break
                            else:
                                grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                    Grade='F', AttGrade='P')
                                grade.save()
                                break
                    if graded:
                        break
                if not graded:
                    for threshold in thresholds:
                        if mark.TotalMarks >= threshold.Threshold_Mark:
                            if grades_objects.filter(RegId_id=mark.Registration.id):
                                grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='P')
                                break
                            else:
                                grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                    Grade=threshold.Grade.Grade, AttGrade='P')
                                grade.save()
                                break
            else:
                for threshold in thresholds:
                    if mark.TotalMarks >= threshold.Threshold_Mark:
                        if grades_objects.filter(RegId_id=mark.Registration.id):
                            grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='X')
                            break
                        else:
                            grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                    Grade=threshold.Grade.Grade, AttGrade='X')
                            grade.save()
                            break
    print(set(error_events))
            
