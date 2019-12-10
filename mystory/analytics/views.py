from django.shortcuts import render
from vocastory.models import Sentence
from accounts.models import CustomUser
from django.utils import timezone
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse
import io
    
def see_sentences(request):
    users = CustomUser.objects.all().order_by('date_joined')
    start_date = users.first().date_joined.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date + timezone.timedelta(days=1)
    t_d = timezone.timedelta(hours=8)

    total_users = 0
    cumulative_users = []
    x = []
    cur_date = start_date
    while cur_date < end_date:
        total_users += Sentence.num_entries_range(cur_date, cur_date + t_d)
        cumulative_users.append(total_users)
        x.append(cur_date.strftime('%d-%H'))
        cur_date += t_d

    
    plt.xticks(range(len(x)), x, wrap=True)
    plt.xlabel('Time (Day-Hour)')
    plt.ylabel('Total Sentences')
    plt.title('Cumulative Sentence Graph')
    plt.bar(range(len(cumulative_users)), cumulative_users)

    f = matplotlib.figure.Figure()

    canvas = FigureCanvasAgg(f)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    plt.close(f)

    response = HttpResponse(buf.getvalue(), content_type='image/png')

    return response
    
def see_users(request):
    users = CustomUser.objects.all().order_by('date_joined')
    start_date = users.first().date_joined.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date + timezone.timedelta(days=1)
    t_d = timezone.timedelta(hours=8)

    total_users = 0
    cumulative_users = []
    x = []
    cur_date = start_date
    while cur_date < end_date:
        total_users += CustomUser.num_entries_range(cur_date, cur_date + t_d)
        cumulative_users.append(total_users)
        x.append(cur_date.strftime('%d-%H'))
        cur_date += t_d

    plt.xticks(range(len(x)), x, wrap=True)
    plt.xlabel('Time (Day-Hour)')
    plt.ylabel('Total Users')
    plt.title('Cumulative User Graph')
    plt.bar(range(len(cumulative_users)), cumulative_users)

    f = matplotlib.figure.Figure()
    canvas = FigureCanvasAgg(f)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    plt.close(f)
    
    response = HttpResponse(buf.getvalue(), content_type='image/png')

    return response

