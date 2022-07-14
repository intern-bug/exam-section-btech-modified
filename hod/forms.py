from django import forms 
from django.contrib.auth.models import Group
from superintendent.models import RegistrationStatus
from hod.models import Coordinator
from ExamStaffDB.models import FacultyInfo



class GradesFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(GradesFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))



class CoordinatorAssignmentForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(CoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        BYEAR_CHOICES =  [('', '--------'),(2, 2),(3, 3),(4, 4)]
        self.fields['BYear'] = forms.CharField(label='BYear',  required=False, widget=forms.Select(choices=BYEAR_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
        self.fields['user'] = forms.CharField(label='User',  required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
        if self.data.get('BYear'):
            faculty= FacultyInfo.objects.filter(Working=True, Dept=Option) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
            group = Group.objects.filter(name='Co-ordinator').first()
            assigned_users = Coordinator.objects.filter(RevokeDate__isnull=True).exclude(Dept=Option,BYear=self.data.get('BYear'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.CharField(label='User', required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
            initial_coordinator = Coordinator.objects.filter(Dept=Option,BYear=self.data.get('BYear') ,RevokeDate__isnull=True).first()
            if initial_coordinator:
                self.fields['coordinator'].initial = initial_coordinator.Faculty.id
                self.fields['user'].initial = initial_coordinator.User.id


# class AttendanceShoratgeStatusForm(forms.Form):
#     def __init__(self,Option=None , *args,**kwargs):
#         super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
#         self.myFields=[]
#         depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
#         years = {1:'I',2:'II',3:'III',4:'IV'}
#         sems = {1:'I',2:'II'}
#         self.regIDs = RegistrationStatus.objects.filter(Status=1)
#         self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
#         myChoices = [(option[7], depts[option[4]-1]+':'+ \
#                 years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
#                     ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
#         myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
#         self.fields['RegEvent'] = forms.CharField(label='Choose Registration ID', \
#             max_length=26, widget=forms.Select(choices=myChoices))