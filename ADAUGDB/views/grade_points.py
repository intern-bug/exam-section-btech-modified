from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import redirect, render
from ADAUGDB.user_access_test import is_Associate_Dean_Academics, grade_points_status_access
from ADAUGDB.forms import GradePointsStatusForm, GradePointsUploadForm, GradePointsUpdateForm
from ADAUGDB.models import BTGradePoints
from ADAUGDB.resources import GradePointsResource
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from django.db import transaction


@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def grade_points_upload(request):
    if request.method == 'POST':
        form = GradePointsUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['Regulation'] != '-- Select Regulation --':
                regulation = float(form.cleaned_data['Regulation'])
                file = form.cleaned_data['file']
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                newDataset= Dataset()
                errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                errorDataset.headers = ['Regulation', 'Grade', 'Points']
                newDataset.headers = ['Regulation', 'Grade', 'Points']
                for i in range(len(dataset)):
                    row = dataset[i]
                    if row[0]==regulation:
                        newRow = (row[0], row[1], row[2])
                        newDataset.append(newRow)
                    else:
                        newRow = (row[0], row[1], row[2])
                        errorDataset.append(newRow)
                gradePointsResource = GradePointsResource()
                result = gradePointsResource.import_data(newDataset, dry_run=True)
                if not result.has_errors():
                    gradePointsResource.import_data(newDataset, dry_run=False)
                    if len(errorDataset)!=0:
                        errRows = [ (errorDataset[i][0],errorDataset[i][1],errorDataset[i][2]) for i in range(len(errorDataset))]
                        request.session['errRows'] = errRows
                        # request.session['currentRegEventId'] = currentRegEventId
                        return redirect('BTGradePointsUploadErrorHandler' )
                    msg = 'The data for grade points is uploaded succesfully.'
                    return(render(request,'ADAUGDB/GradePointsUpload.html', {'form':form, 'msg':msg}))
                else:
                    errors = result.row_errors()
                    indices = set([i for i in range(len(newDataset))])    
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers
                    result1 = gradePointsResource.import_data(cleanDataset, dry_run=True)
                    if not result1.has_errors():
                        gradePointsResource.import_data(cleanDataset, dry_run=False)
                    else:
                        print('Something went wrong in plain import')
                    errorData = Dataset()
                    for i in list(errorIndices):
                        newRow = (newDataset[i][0],newDataset[i][1],newDataset[i][2])
                        errorData.append(newRow)
                    for i in errorDataset:
                        errorData.append(i)
                    errRows = [ (errorData[i][0],errorData[i][1],errorData[i][2]) for i in range(len(errorData))]
                    request.session['errRows'] = errRows
                    return redirect('BTGradePointsUploadErrorHandler')
    else:
        form = GradePointsUploadForm()
    return render(request, 'ADAUGDB/GradePointsUpload.html', {'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def grade_points_upload_error_handler(request):
    errRows = request.session.get('errRows')
    if(request.method=='POST'):
        form = GradePointsUpdateForm(errRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(errRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    BTGradePoints.objects.filter(Regulation=fRow[0], Grade=fRow[1]).update(Points=fRow[2])
            return render(request, 'ADAUGDB/GradePointsUploadSuccess.html')
    else:
        form = GradePointsUpdateForm(Options=errRows)
    return(render(request, 'ADAUGDB/GradePointsUploadErrorHandler.html',{'form':form}))


@login_required(login_url="/login/")
@user_passes_test(grade_points_status_access)
def grade_points_status(request):
    if request.method == 'POST':
        form = GradePointsStatusForm(request.POST)
        if form.is_valid():
            regulation = form.cleaned_data.get('Regulation')
            grade_points_obj = BTGradePoints.objects.filter(Regulation=regulation)
            return render(request, 'ADAUGDB/GradePointsStatus.html', {'form':form, 'grade_points':grade_points_obj})
    form = GradePointsStatusForm()
    return render(request, 'ADAUGDB/GradePointsStatus.html', {'form':form})

