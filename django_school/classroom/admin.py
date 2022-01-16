from django.contrib import admin

# Register your models here.
from .models import (User, Subject, Quiz, Question, 
    Answer, Student, TakenQuiz, AuditEntry)


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    readonly_fields = ['log_time',]
    list_display = ['action', 'username', 'log_time','ip',]
    list_filter = ['action',]
# admin.site.register(AuditEntry)

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Student)
admin.site.register(TakenQuiz)