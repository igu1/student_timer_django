from django.contrib import admin
from .models import StudentStudyDate, StudentStudyTime, Quote, Profile


class StudentStudyDateAdmin(admin.ModelAdmin):
    list_display = ("user", "date")


class StudentStudyTimeAdmin(admin.ModelAdmin):
    list_display = ("study", "time")


admin.site.register(StudentStudyDate, StudentStudyDateAdmin)
admin.site.register(StudentStudyTime, StudentStudyTimeAdmin)
admin.site.register(Quote)
admin.site.register(Profile)
