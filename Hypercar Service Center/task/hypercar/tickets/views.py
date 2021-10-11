from collections import deque, Counter

from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect

CLIENTS = deque()
TICKET = 'Waiting for the next client'


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


services_links = [{'title': 'Change oil', 'link': 'change_oil'},
                  {'title': 'Inflate tires', 'link': 'inflate_tires'},
                  {'title': 'Get diagnostic test', 'link': 'diagnostic'}]

SERVICES = ('change_oil', 'inflate_tires', 'diagnostic')


class MenuView(View):
    template_name = 'menu.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'menu_items': services_links})


class TicketView(View):
    template_name = 'ticket.html'

    def get(self, request, *args, **kwargs):
        work_time = {
            'change_oil': 2,
            'inflate_tires': 5,
            'diagnostic': 30,
        }
        line_len = len(CLIENTS)
        ticket_number = line_len + 1
        ticket = kwargs['ticket']
        print('t', ticket)
        estimate_minutes = 0
        if line_len > 0:
            if ticket == 'change_oil':
                works = SERVICES[:1]
            if ticket == 'inflate_tires':
                works = SERVICES[:2]
            if ticket == 'diagnostic':
                works = SERVICES[:3]
            for client in CLIENTS:
                if client['work'] in works:
                    estimate_minutes += work_time[client['work']]
        CLIENTS.append({'work': ticket, 'ticket': ticket_number})
        context = {
            'ticket_number': ticket_number,
            'minutes_to_wait': estimate_minutes,
        }
        return render(request, self.template_name, context)


class ProcessView(View):
    template_name = 'processing.html'

    def get(self, request, *args, **kwargs):
        counts = Counter(tok['work'] for tok in CLIENTS)

        return render(request, self.template_name, {'counts': counts})

    def post(self, request, *args, **kwargs):
        global TICKET
        if CLIENTS:
            for service in SERVICES:
                for client in CLIENTS:
                    if client['work'] == service:
                        TICKET = f'Next ticket #{client["ticket"]}'
                        CLIENTS.remove(client)
                        return redirect('/next')
        else:
            TICKET = 'Waiting for the next client'
            return redirect('/next')


class NextView(View):
    template_name = 'next.html'

    def get(self, request):
        context = {'ticket': TICKET}
        return render(request, self.template_name, context)
