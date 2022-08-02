from django.db.models.signals import post_save
from django.dispatch import receiver
from co_ordinator.models import StudentRegistrations, Subjects
from faculty.models import BTMarks, BTMarks_Staging

@receiver(post_save, sender=StudentRegistrations)
def create_marks_instance(sender, instance, created, **kwargs):
    if not BTMarks.objects.filter(Registration=instance).exists():
        subject = Subjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        BTMarks.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
    if not BTMarks_Staging.objects.filter(Registration=instance).exists():
        subject = Subjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        BTMarks_Staging.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)

