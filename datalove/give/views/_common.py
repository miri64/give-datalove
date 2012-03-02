from django.shortcuts import get_list_or_404
from give.models import DataloveHistory

def get_history(**args):
    send_history = [m.__dict__ for m in get_list_or_404(
            DataloveHistory, 
            **args
        )]
    for h in send_history:
        del h['_state']
        del h['id']
        h['timestamp'] = str(h['timestamp'])
    return send_history 
