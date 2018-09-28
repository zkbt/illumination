
from IPython.display import HTML

def display(filename):
    '''
    Display files of different types in a jupyter notebook.
    '''

    if '.mp4' in filename:
        template = """<video width="80%" controls loop>
                      <source src="{}" type="video/mp4" />
                      </video>"""
    elif '.pdf' in filename:
        template = """<iframe src={} width=80%></iframe>'.format(filename)"""
    else:
        template = """<img width="80%" src={}>"""

    return HTML(template.format(filename))
