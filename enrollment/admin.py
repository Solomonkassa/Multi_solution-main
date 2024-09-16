from django.contrib import admin
from .models import Training,  Enrollment

class TrainingAdmin(admin.ModelAdmin):
    list_display = ("training", "enrolled_trainee_count")  
    search_fields = ("training",)  
    list_filter = ("training",)  

    def enrolled_trainee_count(self, instance):
        return instance.enrolled_trainee.count()  
    enrolled_trainee_count.short_description = "Enrolled Trainees Count"  

    
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "training", "is_complete", "enrollment_date")
    search_fields = ("user__username", "is_complete", "training")  
    list_filter = ("training", "enrollment_date")  
    readonly_fields = ("enrollment_date",)  
    fieldsets = (
        (None, {
            'fields': ('user', 'training')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('enrollment_date',),
        }),
    ) 

admin.site.register(Training, TrainingAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)  





