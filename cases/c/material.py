from pathlib import Path


import streamlit as st


import pandas as pd


import plotly.graph_objects as go


R=Path(__file__).parent


P=pd.read_csv(R/'prices_private.csv',parse_dates=['date'])


S=pd.read_csv(R/'stooq_weekly_private.csv',parse_dates=['date'])


F=pd.read_csv(R/'fundamentals_private.csv')


CUT=pd.Timestamp('2021-03-31')


END=pd.Timestamp('2022-03-31')


STAGES=['Działalność i wykres','Dywidendy','Wyniki finansowe','Bilans, ryzyko i wycena']


def chart(reveal=False):
 d=P if reveal else P[P.date<=CUT]
 d=d.set_index('date').resample('W-FRI').last().dropna().reset_index()
 base=P.iloc[0]['close']; xx=(d.date-P.iloc[0].date).dt.days/30.4375+1
 fig=go.Figure(go.Scatter(x=xx,y=d.close*3,mode='lines',line=dict(color='#447c9b',width=2.5),hovertemplate='Miesiąc %{x:.0f}<br>Wartość %{y:.2f}<extra></extra>'))
 if reveal:
  xc=(CUT-P.iloc[0].date).days/30.4375+1
  fig.add_vline(x=xc,line_dash='dot',line_color='#888');fig.add_annotation(x=xc,y=float(P.iloc[(P.date-CUT).abs().argmin()].close*3),text='DECYZJA',showarrow=True,ax=-30,ay=-35)
 else:fig.add_annotation(x=float(xx.iloc[-1]),y=float(d.close.iloc[-1]*3),text='TERAZ',showarrow=True,ax=-35,ay=-35)
 fig.update_layout(template='plotly_white',height=340,margin=dict(l=5,r=10,t=15,b=10),xaxis=dict(title='Czas (daty ukryte)',tickmode='array',tickvals=list(range(1,86,12)),ticktext=[f'Miesiąc {n}' for n in range(1,86,12)]),yaxis=dict(title='Kurs (USD)',gridcolor='#edf0f3'),showlegend=False)
 st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
 st.caption('Wykres uwzględnia korekty związane ze splitami i historycznymi wypłatami dywidend.')


def material(i):
 if i==0:
  st.subheader('Czym zajmuje się spółka?')
  st.write('Duży międzynarodowy producent markowej żywności pakowanej. Sprzedaje sosy, produkty gotowe, przekąski, sery i inne artykuły spożywcze. Działa głównie poprzez sieci handlowe. Rozpoznawalne marki pomagają w sprzedaży, ale firma konkuruje z markami własnymi sklepów i innymi producentami.')
  chart()
 elif i==1:
  st.subheader('Dywidendy')
  st.write('**Historia wypłat:** po utworzeniu obecnej spółki wypłacano dywidendy kwartalne. Po wcześniejszych wyższych wypłatach dywidendę obniżono w 2019 roku. To przykład spółki wypłacającej dywidendy, ale nie podnoszącej ich nieprzerwanie.')
  a,b=st.columns(2);a.metric('Ostatnia kwartalna dywidenda','1,20 na akcję');b.metric('Roczna stawka przy utrzymaniu','4,80 na akcję')
  st.write('W przeszłości kwartalna dywidenda wynosiła **1,875 na akcję**. Następnie została obniżona do **1,20 na akcję**. Wypłaty kontynuowano, ale wcześniejszy poziom nie został przywrócony.')
  st.caption('Dane o wypłatach i obniżce: oficjalna historia dywidend spółki. Nie ma gwarancji dalszych wypłat.')
 elif i==2:
  st.subheader('Pięć lat wyników')
  f=F.copy();f['Rok']=[f'Rok {j}' for j in range(1,6)]
  fig=go.Figure();fig.add_trace(go.Bar(x=f.Rok,y=f.sales,name='Przychody',marker_color='#447c9b'));fig.add_trace(go.Bar(x=f.Rok,y=f.net_income,name='Zysk netto',marker_color='#b49d76'))
  fig.update_layout(template='plotly_white',height=300,barmode='group',margin=dict(l=5,r=5,t=15,b=10),legend=dict(orientation='h',y=1.18),yaxis_title='mln USD')
  st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
  st.dataframe(pd.DataFrame({'Rok':f.Rok,'Przychody (mln)':f.sales.map(lambda x:f'{x:,}'.replace(',',' ')),'Zysk netto (mln)':f.net_income.map(lambda x:f'{x:,}'.replace(',',' '))}),hide_index=True,use_container_width=True)
  st.caption('Zyski raportowane. Strata w trzecim roku wynikała w znacznej mierze z odpisów wartości marek i wartości firmy. Dodatni zysk w czwartym i piątym roku nie oznacza braku kolejnych odpisów.')
 else:
  st.subheader('Bilans, ryzyko i wycena')
  st.write('W ostatnim roku firma wykazała **26,2 mld** przychodów i **0,36 mld** zysku netto przypisanego akcjonariuszom. Jednocześnie skorygowany EBITDA wynosił **6,67 mld**. Wartość księgowa kapitału akcjonariuszy wynosiła **50,1 mld**.')
  st.markdown('**Oczekiwania zarządu na kolejny rok**')
  st.write('Zarząd spółki zakładał wyniki lepsze od wcześniej przyjętego planu strategicznego. Na najbliższy kwartał oczekiwał **od zerowego do dodatniego wzrostu sprzedaży organicznej** oraz **niewielkiego, jednocyfrowego wzrostu skorygowanej EBITDA przy stałych kursach walut**. Nie przedstawiono w tej wypowiedzi konkretnej rocznej prognozy EPS ani przychodów.')
  st.write('Dług długoterminowy wraz z częścią krótkoterminową wynosił około **28,3 mld**. W ostatnim roku firma rozpoznała około **3,4 mld** niegotówkowych odpisów związanych z markami i wartością firmy. Silne marki nie eliminują ryzyka spadku ich wyceny.')
