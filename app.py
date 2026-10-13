from pathlib import Path
import importlib.util
import random
import uuid
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Czy kupiłbyś tę spółkę?", page_icon="📈", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>.block-container{max-width:800px;padding-top:1.3rem}div.stButton>button{min-height:2.7rem;border-radius:10px}</style>",unsafe_allow_html=True)
ROOT=Path(__file__).parent
CASE_CODES=['a','b','c','d']
CONFIDENCE_LEVELS=['Bardzo niepewny/a','Raczej niepewny/a','Ani pewny/a, ani niepewny/a','Raczej pewny/a','Bardzo pewny/a']
@st.cache_resource
def get_case(code):
    path=ROOT/'cases'/code/'material.py'
    spec=importlib.util.spec_from_file_location('case_material_'+code,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

if 'order' not in st.session_state:
    st.session_state.order=random.sample(CASE_CODES,len(CASE_CODES))
    st.session_state.session_id=str(uuid.uuid4())
    st.session_state.screen='intro'
    st.session_state.current=None
    st.session_state.progress_data={}
    st.session_state.done=[]
    st.session_state.scroll_to_top=False

# Po zmianie ekranu przewijamy do początku, ale nie po zwykłym wyborze odpowiedzi.
if st.session_state.get('scroll_to_top', False):
    st.session_state.scroll_to_top = False
    components.html("""
    <script>
    (function () {
      function goTop() {
        try {
          const doc = window.parent.document;
          const scrollers = [
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('[data-testid="stMain"]'),
            doc.querySelector('section.main'),
            doc.scrollingElement
          ];
          scrollers.forEach(el => { if (el) el.scrollTop = 0; });
          window.parent.scrollTo(0, 0);
        } catch (e) { /* Nie blokuj aplikacji, jeśli przeglądarka ogranicza iframe. */ }
      }
      goTop();
      [100, 300, 700].forEach(ms => setTimeout(goTop, ms));
    })();
    </script>
    """, height=0)

def save_answer(code, stage, decision, confidence):
    """Zapis pojedynczej odpowiedzi w nowej tabeli Supabase."""
    url = str(st.secrets["SUPABASE_URL"]).rstrip("/") + "/rest/v1/decision_answers"
    key = str(st.secrets["SUPABASE_KEY"])
    payload = {
        "test_id": st.session_state.session_id,
        "case_id": code,
        "stage": stage,
        "case_order": number_for(code),
        "decision": decision == "Tak",
        "confidence": confidence,
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"Supabase HTTP {response.status}")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            code = json.loads(body).get("code")
        except (ValueError, TypeError):
            code = None
        if error.code == 409 and code == "23505":
            # Ta sama odpowiedź została już zapisana, np. po ponownej próbie.
            return
        raise RuntimeError(f"Supabase HTTP {error.code}: {body[:250]}") from error
    except URLError as error:
        raise RuntimeError(f"Błąd połączenia z bazą: {error.reason}") from error

def select_case(code):
    st.session_state.current=code
    st.session_state.screen='case'
    st.session_state.scroll_to_top=True
    st.session_state.progress_data.setdefault(code,{'stage':0,'answers':[],'finished':False})

def number_for(code):return st.session_state.order.index(code)+1

def chart_after(case):
    # Bez nazw firm i dat; pokazujemy tylko to, co stało się z kursem.
    if hasattr(case,'lineplot'):case.lineplot(reveal=True)
    elif hasattr(case,'chart'):
        if hasattr(case,'PRICE'):
            combined=case.PRICE[(case.PRICE.month>=case.PAST.iloc[0].month)&(case.PRICE.month<=pd.Timestamp('2001-09-01'))]
            case.chart(combined,forward=True)
        else:case.chart(reveal=True)

def show_finish(code,case,answers):
    st.success('Dziękuję! To był rzeczywisty przypadek giełdowy.')
    st.subheader('Jak zmieniały się Twoje decyzje?')
    a=pd.DataFrame(answers)
    st.dataframe(a,hide_index=True,use_container_width=True)
    fig=go.Figure(go.Scatter(x=a['Etap'],y=a['Poziom pewności'],mode='lines+markers',line=dict(color='#447c9b',width=3),marker=dict(size=10)))
    fig.update_layout(height=250,margin=dict(l=10,r=10,t=10,b=10),template='plotly_white',xaxis=dict(tickmode='array',tickvals=[1,2,3,4],title='Etap'),yaxis=dict(range=[0.8,5.2],tickmode='array',tickvals=[1,2,3,4,5],ticktext=['Bardzo niepewny/a','Raczej niepewny/a','Neutralnie','Raczej pewny/a','Bardzo pewny/a'],title='Pewność'))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.write('To zapis Twoich decyzji i deklarowanej pewności. Nie jest to ocena Twoich umiejętności inwestycyjnych.')
    st.subheader('Co wydarzyło się później?')
    chart_after(case)
    st.caption('Wykres przedstawia również 12 miesięcy po ostatniej decyzji. Zachowano anonimowość spółki i dat.')
    with st.container(border=True):
        st.markdown('🔒 **Informacje o spółce**')
        st.caption('Nazwa spółki i daty pozostają na razie ukryte, ponieważ te rzeczywiste przypadki wykorzystuję także w kolejnych eksperymentach. Być może w przyszłości opowiem o nich więcej.')
    st.divider()
    if len(st.session_state.done)<4:
        if st.button('Wybierz kolejny przypadek',type='primary',use_container_width=True):
            st.session_state.screen='select';st.session_state.scroll_to_top=True;st.rerun()
    if st.button('Zakończ',use_container_width=True):
        st.session_state.screen='end';st.session_state.scroll_to_top=True;st.rerun()

if st.session_state.screen=='intro':
    st.title('Czy kupiłbyś tę spółkę?')
    st.write('Za chwilę zobaczysz jeden z czterech rzeczywistych przypadków spółek giełdowych. Ich nazwy i daty zostały ukryte.')
    st.write('Będziesz stopniowo otrzymywać kolejne informacje o wybranej spółce. Na każdym etapie zdecydujesz, czy kupiłbyś jej akcje z myślą o najbliższych 12 miesiącach, i określisz, jak bardzo jesteś pewien swojej decyzji.')
    st.write('**To nie jest pełna analiza inwestycyjna.** W rzeczywistości do podjęcia takiej decyzji zapewne potrzebowałbyś znacznie więcej danych, czasu i możliwości ich weryfikacji.')
    st.write('Potraktuj więc to zadanie jako wyzwanie, grę, a może po prostu kilka minut zabawy w podejmowanie decyzji przy ograniczonej ilości informacji.')
    st.write('Możesz zmieniać zdanie w kolejnych etapach, ale nie możesz poprawiać wcześniejszych odpowiedzi.')
    st.write('Na końcu zobaczysz, co wydarzyło się później.')
    st.markdown('**Dziękuję za udział!**  \nGrzegorz Zalewski')
    if st.button('Dalej →',type='primary',use_container_width=True):st.session_state.screen='select';st.session_state.scroll_to_top=True;st.rerun()
elif st.session_state.screen=='select':
    st.title('Wybierz przypadek')
    st.write('Przygotowałem cztery różne historie giełdowe. Możesz zacząć od dowolnej z nich. Po zakończeniu zobaczysz dalszy przebieg kursu i będziesz mógł wybrać następny.')
    for row in (0,2):
        cols=st.columns(2)
        for j,col in enumerate(cols):
            n=row+j+1;code=st.session_state.order[n-1];completed=code in st.session_state.done
            with col:
                with st.container(border=True):
                    st.markdown(f'### Przypadek {n}')
                    if completed:st.caption('✓ Ukończony')
                    if st.button('Wybierz' if not completed else 'Ukończony',key=f'pick_{n}',disabled=completed,use_container_width=True):select_case(code);st.rerun()
    st.caption('Kolejność przypadków jest losowa. Możesz zakończyć po jednym lub przeanalizować wszystkie cztery.')
elif st.session_state.screen=='case':
    code=st.session_state.current
    case=get_case(code)
    data=st.session_state.progress_data[code]
    st.title(f'Przypadek {number_for(code)}')
    if data['finished']:
        show_finish(code,case,data['answers'])
    else:
        i=data['stage']
        st.progress(i/4,text=f'Etap {i+1} z 4 · {case.STAGES[i]}')
        if hasattr(case,'show_material'):case.show_material(i)
        else:case.material(i)
        if i>0:
            with st.expander('📚 Przypomnij wcześniejsze informacje'):
                st.caption('Możesz przejrzeć wcześniejsze materiały, ale nie możesz zmienić odpowiedzi.')
                for j in range(i):
                    with st.expander(f'Etap {j+1}: {case.STAGES[j]}'):
                        if hasattr(case,'show_material'):case.show_material(j,True)
                        else:case.material(j)
        st.divider()
        st.markdown('**Twoja decyzja inwestycyjna**')
        d=st.radio('Czy kupiłbyś/kupiłabyś akcje tej spółki z zamiarem utrzymania ich przez 12 miesięcy?', ['Tak','Nie'],index=None,horizontal=True,key=f'decision_{code}_{i}')
        c=st.pills('Jak bardzo jesteś pewien/pewna tej decyzji?',options=CONFIDENCE_LEVELS,selection_mode='single',default=None,key=f'confidence_{code}_{i}')
        st.caption('Oceniasz pewność decyzji, nie prawdopodobieństwo wzrostu kursu.')
        if st.button('Zapisz i przejdź dalej' if i<3 else 'Zobacz swoje odpowiedzi',type='primary',use_container_width=True,disabled=(d is None or c is None)):
            try:
                save_answer(code, i+1, d, c)
            except Exception as error:
                st.error('Nie udało się zapisać odpowiedzi. Spróbuj ponownie. Twoja decyzja pozostaje zaznaczona.')
                st.caption(f'Szczegóły techniczne: {error}')
            else:
                data['answers'].append({'Etap':i+1,'Informacje':case.STAGES[i],'Decyzja':d,'Pewność':c,'Poziom pewności':CONFIDENCE_LEVELS.index(c)+1})
                if i<3:data['stage']+=1
                else:
                    data['finished']=True
                    if code not in st.session_state.done:st.session_state.done.append(code)
                st.session_state.scroll_to_top=True
                st.rerun()
else:
    st.title('Dziękuję za udział!')
    st.write(f'Ukończone przypadki: **{len(st.session_state.done)} z 4**.')
    if len(st.session_state.done)<4:
        if st.button('Wróć do wyboru przypadków',type='primary',use_container_width=True):st.session_state.screen='select';st.session_state.scroll_to_top=True;st.rerun()
    st.caption('Odpowiedzi zostały zapisane anonimowo na potrzeby eksperymentu.')
