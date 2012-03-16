from djangopiston.piston.handler import AnonymousBaseHandler,BaseHandler
from give.models import *
from give.views._common import give_datalove
from django.contrib.auth.models import User

class AnonymousProfileHandler(AnonymousBaseHandler):
    model = DataloveProfile
    fields = ('received_love', 
                'username',
                'websites',
            )

    def read(self, request, username=None):
        selection = self.fields
        if username:
            return DataloveProfile.objects.get(user__username=username).\
                    get_profile_dict(selection)
        else:
            return [p.get_profile_dict(selection) for p in \
                DataloveProfile.objects.order_by('?')
            ]

class ProfileHandler(BaseHandler):
    anonymous = AnonymousProfileHandler
    allowed_methods = ('GET',)
    model = DataloveProfile
    fields = ('username',
              'received_love', 
              'websites',
            )

    def read(self, request, username=None):
        selection = self.fields
        if request.user.username == username:
            selection = selection + ('available_love',)
        if username:
            return DataloveProfile.objects.get(user__username=username).\
                    get_profile_dict(selection)
        else:
            return [p.get_profile_dict(selection) for p in \
                DataloveProfile.objects.order_by('?')
            ]

class HistoryHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, username):
        if request.user.username != username:
            return []
        sent = [h.get_history_dict() for h in \
                DataloveHistory.objects.filter(sender__user__username=username)
            ]
        received = [h.get_history_dict() for h in \
                DataloveHistory.objects.filter(
                        recipient__dataloveprofile__user__username=username
                    )
            ]
        return {'sent': sent, 'received': received}

class GiveDataloveHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = LovableObject

    def create(self, request, id):
        error = {}
        amount = int(request.POST.get('amount', 1))
        error = give_datalove(request, id, amount)
        return error
