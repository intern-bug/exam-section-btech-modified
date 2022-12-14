from io import open_code
from django.db import models
from django.contrib.auth import get_user_model
from BTco_ordinator.models import BTSubjects
# from ExamStaffDB.models import BTFacultyInfo
from ADAUGDB.constants import DEPARTMENTS, YEARS, SEMS
from BTco_ordinator.models import BTStudentRegistrations
from simple_history.models import HistoricalRecords

# Create your models here.

User = get_user_model()

class BTRegistrationStatus(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Regulation = models.FloatField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    RollListStatus = models.IntegerField()
    RollListFeeStatus = models.IntegerField()
    OERollListStatus = models.IntegerField()
    OERegistrationStatus = models.IntegerField()
    RegistrationStatus = models.IntegerField()
    MarksStatus = models.IntegerField()
    GradeStatus = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTRegistration_Status'
        constraints = [
            models.UniqueConstraint(fields=['AYear', 'ASem', 'BYear', 'BSem', 'Regulation', 'Dept', 'Mode'], name='unique_BTRegistrationstatus')
        ]
        managed = True

    def __str__(self):
        name =  str(DEPARTMENTS[self.Dept-1]) + ':' + str(YEARS[self.BYear]) + ':' + str(SEMS[self.BSem]) + ':' + \
            str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
        return name
    
    def __open_str__(self):
        name =  str(YEARS[self.BYear]) + ':' + str(SEMS[self.BSem]) + ':' + \
            str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
        return name



class BTRegulation(models.Model):
    AdmissionYear = models.IntegerField()
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.FloatField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTRegulation'
        constraints = [
            models.UniqueConstraint(fields=['AdmissionYear', 'AYear', 'BYear'], name='unique_BTRegulation')
        ]
        managed = True

class BTProgrammeModel(models.Model):
    PID = models.IntegerField(primary_key=True)
    ProgrammeName = models.CharField(max_length=20)
    ProgrammeType = models.CharField(max_length=10)
    Specialization = models.CharField(max_length=100)
    Dept = models.IntegerField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTProgrammeModel'
        constraints = [
            models.UniqueConstraint(fields=['PID'], name='unique_BTPID')
        ]
        managed = True

class BTCourseStructure(models.Model):
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.FloatField()
    Category = models.CharField(max_length=15)
    Type = models.CharField(max_length=10)
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    count = models.IntegerField()
    Rigid = models.BooleanField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCourseStructure'
        constraints = [
            models.UniqueConstraint(fields=['Category', 'Type', 'Creditable', 'Credits', 'Regulation', 'BYear', 'BSem', 'Dept'], name='Unique_BTCourseStructureId')
        ]
        managed = True

class BTCourses(models.Model):
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=255)
    Credits = models.IntegerField()
    OfferedBy = models.IntegerField()
    CourseStructure = models.ForeignKey('ADAUGDB.BTCourseStructure', on_delete=models.CASCADE)
    lectures = models.IntegerField()
    tutorials = models.IntegerField()
    practicals  = models.IntegerField()
    DistributionRatio = models.TextField()
    MarkDistribution = models.ForeignKey('ADAUGDB.BTMarksDistribution', on_delete=models.CASCADE)
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCourses'
        constraints = [
            models.UniqueConstraint(fields = ['SubCode', 'SubName', 'CourseStructure'], name='BTCourses_unique_course')
        ]
        managed = True

class BTCurriculumComponents(models.Model):
    Regulation = models.FloatField()
    Dept = models.IntegerField()
    Category = models.CharField(max_length=10)
    CreditsOffered = models.IntegerField()
    MinimumCredits = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCurriculumCredits'
        constraints = [
            models.UniqueConstraint(fields = ['Regulation', 'Dept', 'Category'], name='unique_BTCurriculumComponents_key')
        ]
        managed = True

class BTHOD(models.Model):
    Faculty = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE)
    Dept = models.IntegerField()
    AssignedDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    User =models.ForeignKey(User, on_delete=models.CASCADE)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTHOD'
        unique_together = (('Faculty', 'Dept', 'AssignedDate'))
        managed = True

class BTCycleCoordinator(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    User =models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE)
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    Cycle = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCycleCoordinator'
        unique_together = (('User', 'Faculty','AssignDate','RevokeDate'))
        managed = True

class BTDepartments(models.Model):
    Dept = models.IntegerField()
    Name = models.CharField(max_length=255)
    Dept_Code = models.CharField(max_length=255)
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTDepartments'
        unique_together = (('Dept', 'Name', 'Dept_Code'))
        managed = True

class BTMarksDistribution(models.Model):
    Regulation = models.FloatField()
    Distribution = models.TextField()
    DistributionNames=models.TextField()
    PromoteThreshold = models.TextField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTMarksDistribution'
        unique_together = (('Regulation', 'Distribution', 'DistributionNames', 'PromoteThreshold'))
        managed = True
    
    def __str__(self):
        return str(self.Distribution)+', '+str(self.PromoteThreshold)
    
    def distributions(self):
        distributions_names = self.DistributionNames.split(',')
        distributions_marks = self.Distribution.split(',')
        CHOICES = []
        outer_index = 0
        for names, marks in zip(distributions_names, distributions_marks):
            names = names.split('+')
            marks = marks.split('+')
            inner_index = 0
            for n,m in zip(names,marks):
                CHOICES += [(str(outer_index)+','+str(inner_index), str(n)+', '+str(m))]
                inner_index += 1
            outer_index += 1
        return CHOICES

    def get_zeroes_string(self):
        distribution_marks = self.Distribution.split(',')
        marks = [row.split('+') for row in distribution_marks]
        zero_marks = [['0' for mark in range(len(row))] for row in marks]
        zero_marks = ['+'.join(mark) for mark in zero_marks]
        zero_marks = ','.join(zero_marks)
        return zero_marks

    def get_marks_limit(self, outer, inner):
        return int(self.Distribution.split(',')[outer].split('+')[inner])

    def get_excel_column_index(self, outer, inner):
        distribution_marks = self.Distribution.split(',')
        marks = [row.split('+') for row in distribution_marks]
        index = 3
        '''
        index starts from 1 availing for the roll number(index=0) and name(index=1) rows in excel sheet.
        '''
        for num in range(outer):
            index += len(marks[num])
        index += inner
        return index


class BTGradePoints(models.Model):
    Regulation = models.FloatField()
    Grade = models.CharField(max_length=2)
    Points = models.IntegerField()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'BTGradePoints'
        unique_together = (('Regulation', 'Grade', 'Points'))
        managed = True

    
class BTCancelledStudentInfo(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.FloatField()
    Dept = models.IntegerField()
    AdmissionYear = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GuardianName = models.CharField(max_length=50)
    Phone = models.TextField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address2 = models.CharField(max_length=100, null=True)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    CancelledDate = models.DateField()
    Remarks = models.TextField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCancelledStudentInfo'
        constraints = [
            models.UniqueConstraint(fields=['RegNo'], name='unique_BTcancelled_StudentInfo_RegNo'),
            models.UniqueConstraint(fields=['RollNo'], name='unique_BTcancelled_StudentInfo_RollNo'),
        ]
        managed = True

class BTCancelledStudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId_id = models.IntegerField()
    Mode = models.IntegerField()
    sub_id_id = models.IntegerField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledStudentRegistrations'
        unique_together = (('RegNo', 'RegEventId_id', 'sub_id_id'))
        managed = True


class BTCancelledStudentGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.FloatField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_BTcancelled_StudentGrades_registration')
        ]
        managed = True

class BTCancelledRollLists(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student_id = models.IntegerField()
    RegEventId_id =models.IntegerField()
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledRollLists'
        unique_together = (('student_id', 'RegEventId_id'))
        managed = True

class BTCancelledNotRegistered(models.Model):
    RegEventId_id = models.IntegerField()
    Student_id = models.IntegerField()
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledNotRegistered'
        unique_together = (('RegEventId_id', 'Student_id'))
        managed = True

class BTCancelledNotPromoted(models.Model):
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.FloatField()
    student_id = models.IntegerField()
    PoA_sem1 = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
    PoA_sem2 = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledNotPromoted'
        unique_together=(('AYear', 'BYear', 'Regulation', 'student_id'))
        managed = True

class BTCancelledDroppedRegularCourses(models.Model):
    student_id = models.IntegerField()
    subject_id =models.IntegerField()
    RegEventId_id = models.IntegerField()
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTCancelledDroppedRegularCourses'
        unique_together = (('student_id', 'subject_id'))
        managed = True

class BTCancelledMarks(models.Model):
    Registration_id = models.IntegerField()
    Marks = models.TextField()
    TotalMarks = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTCancelledMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration_id'], name='unique_BTcancelled_marks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id).first()
        ratio = subject.DistributionRatio.split(':')
        total_parts = 0
        for part in ratio:
            total_parts += int(part)
        total = 0
        for index in range(len(marks_dis)):
            marks_row = marks_dis[index]
            sub_total = 0
            for mark in marks_row:
                sub_total += int(mark)
            total = sub_total*int(ratio[index])
        return round(total/total_parts)

class BTStudentCGPAs_Staging(models.Model):
    RegNo = models.IntegerField()
    AYASBYBS_G = models.IntegerField()
    CGP = models.IntegerField()
    CC = models.IntegerField()
    CGPA = models.FloatField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'BTStudentCGPAs_StagingMV'
        managed = False

class BTOpenElectiveRollLists(models.Model):
    student = models.ForeignKey('BTco_ordinator.BTRollLists_Staging', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    subject = models.ForeignKey('BTco_ordinator.BTSubjects', on_delete=models.CASCADE)
    Section = models.CharField(max_length=2, default='NA')
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTOpenElectiveRollLists'
        unique_together = ('student', 'RegEventId', 'subject')
        managed = True
