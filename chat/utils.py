from .models import GroupMessage
from .serializers import GetMessageSerializer
def get_messages(group, start, end):
    start = int(start)
    end = int(end)
    end = max(start, end)
    start = min(start, end)

    messages = GroupMessage.objects.filter(group=group)
    start = min(start, len(messages))
    end = min(end, len(messages))
    serialized_messages = GetMessageSerializer(messages[start: end], many=True)
    return serialized_messages.data