from django.views.generic.base import TemplateView
from membership.models import Membership

class HomeView(TemplateView):
   template_name = 'home.html'

   def get_context_data(self, **kwargs):
       context = super(HomeView, self).get_context_data(**kwargs)
       # here's the difference:
       context['memberships'] = Membership.objects.all()
       return context
