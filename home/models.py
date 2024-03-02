from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class StudentStudyDate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{str(self.user.username)} = > {str(self.date)}"


class StudentStudyTime(models.Model):
    study = models.ForeignKey(StudentStudyDate, on_delete=models.CASCADE)
    time = models.TimeField()

    def __str__(self):
        return str(self.study.user.username)


class Quote(models.Model):
    quote = models.CharField(max_length=1000)

    def __str__(self):
        return self.quote

    class Meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"

    def get_random_quote():
        return Quote.objects.order_by("?").first()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    premium_user = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, related_name="friends", blank=True)
    first_name = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to="profile_pics", null=True, blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
