from django.shortcuts import render
from vocastory.models import Sentence
from django.utils import timezone
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse
import io

# Create your views here.
def sentences_per_day(earliest):
    per_day = []
    d1 = timezone.timedelta(days=1)
                            
    delta = timezone.now() - earliest
    
    prev = earliest
    for i in range(delta.days+1):
        per_day.append(Sentence.num_entries_range(prev,prev+d1))
        prev+=d1
    
    return per_day
    
def see_sentences(request):
    f = matplotlib.figure.Figure()
    
    sentences=Sentence.objects.all().order_by('creation_date')    
    earliest=sentences.first().creation_date
    
    y_vals = sentences_per_day(earliest)
    x_vals=list(range(1,len(y_vals)+1))   
    
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals)
    
    ax.set(xlabel='Day', ylabel='Sentences written',
           title='Sentences written over time')
    ax.grid()
    
    canvas = FigureCanvasAgg(f)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(f)
    
    response = HttpResponse(buf.getvalue(), content_type = 'image/png')
    
    return response