from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import is_Associate_Dean_Academics, cycle_coordinator_assignment_status_access
from django.shortcuts import render
from django.utils import timezone
from ADAUGDB.models import BTCycleCoordinator
from ADAUGDB.forms import CycleCoordinatorAssignmentForm
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def cycle_coordinator_assignment(request):
    if request.method == 'POST':
        form = CycleCoordinatorAssignmentForm(request.POST)
        assigned_coordinator = None
        if 'cycle' in request.POST.keys():
            assigned_coordinator = BTCycleCoordinator.objects.filter(Cycle=request.POST.get('cycle'), RevokeDate__isnull=True).first()
        if form.is_valid():
            if form.cleaned_data.get('cycle') and form.cleaned_data.get('coordinator') and form.cleaned_data.get('user') and 'submit-form' in request.POST.keys():
                if assigned_coordinator:
                    if (assigned_coordinator.Faculty.id != int(form.cleaned_data.get('coordinator'))) or (assigned_coordinator.User.id != form.cleaned_data.get('user')):
                        assigned_coordinator.RevokeDate = timezone.now()
                        assigned_coordinator.save()
                        new_coordinator = BTCycleCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), Cycle=form.cleaned_data.get('cycle'))
                        new_coordinator.save()
                        msg = 'Cycle cordinator assignment is done successfully.'
                    else:
                        msg = 'No change made in cycle coordinator assignment'
                else:
                    new_coordinator = BTCycleCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), Cycle=form.cleaned_data.get('cycle'))
                    new_coordinator.save()
                    msg = 'Cycle cordinator assignment is done successfully.'
                return render(request, 'ADAUGDB/CycleCoordinatorAssignment.html', {'form':form, 'msg':msg})
            else:
                if assigned_coordinator:
                    return render(request, 'ADAUGDB/CycleCoordinatorAssignment.html', {'form':form, 'initial_cord':assigned_coordinator.Faculty.id, 'initial_user':assigned_coordinator.User.id})
    else:
        form = CycleCoordinatorAssignmentForm()
    return render(request, 'ADAUGDB/CycleCoordinatorAssignment.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(cycle_coordinator_assignment_status_access)
def cycle_coordinator_assignment_status(request):
    cords = BTCycleCoordinator.objects.all()
    return render(request, 'ADAUGDB/CycleCoordinatorAssignmentStatus.html', {'cord':cords})