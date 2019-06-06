from .models import InitLog
from utils.auth import NewModelForm

class InitLogForm(NewModelForm):

    class Meta:
        model = InitLog
        fields = ["init","hosts_list"]


