from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from smart_selects.db_fields import ChainedForeignKey

# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.email


class PeriodType(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class InterestType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Contact(models.Model):
    message = models.CharField(max_length=500, default="SAMPLE MESSAGE")
    message_type_id = models.ForeignKey(InterestType, on_delete=models.CASCADE)
    receiver_id = models.ForeignKey(
        Profile, related_name="receiver", on_delete=models.CASCADE
    )
    sender_id = models.ForeignKey(
        Profile, related_name="sender", on_delete=models.CASCADE
    )


class Degree(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CurriculumPlan(models.Model):
    impl_year = models.IntegerField()
    name = models.CharField(max_length=10, default="PLAN X")
    degree_id = models.ForeignKey(Degree, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}-{self.degree_id.name}"


class Subject(models.Model):
    name = models.CharField(max_length=50)
    period = models.IntegerField()
    period_type = models.ForeignKey(PeriodType, on_delete=models.CASCADE)
    plan_id = models.ForeignKey(CurriculumPlan, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}-{self.plan_id.name}"


class Student(models.Model):
    admission_year = models.IntegerField()
    personal_mail = models.EmailField(blank=True, null=True)
    phone_number = models.IntegerField(blank=True, null=True)
    pfp = models.ImageField(null=True)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    degree_id = models.ForeignKey(Degree, on_delete=models.CASCADE)
    curriculum_plan_id = ChainedForeignKey(
        CurriculumPlan,
        chained_field="degree_id",
        chained_model_field="degree_id",
        show_all=False,
        auto_choose=True,
        sort=True,
    )

    def __str__(self):
        return self.user_id.user.email


class Interest(models.Model):
    interest_type_id = models.ForeignKey(InterestType, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)


class History(models.Model):
    year = models.IntegerField(null=False, blank=False)
    period = models.IntegerField(null=False, blank=False)
    interest_type_id = models.ForeignKey(InterestType, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
