from pathlib import Path


import streamlit as st


import pandas as pd


import plotly.graph_objects as go


R=Path(__file__).parent


P=pd.read_csv(R/'prices_private.csv',parse_dates=['date']).sort_values('date')


CUT=pd.Timestamp('2022-12-30'); END=pd.Timestamp('2023-12-29')


CUT=pd.Timestamp('2022-12-30'); END=pd.Timestamp('2023-12-29')


STAGES=['Spółka i wykres','Wypłacone dywidendy','Otoczenie makro i fracht','Wyniki, bilans i ryzyka']


def lineplot(reveal=False):
 d=P[P.date<= (END if reveal else CUT)].copy().set_index('date').resample('W-FRI').last().dropna().reset_index()
 base=float(d.close.iloc[0]); d['month']=(d.date-d.date.iloc[0]).dt.days/30.4375+1
 fig=go.Figure(go.Scatter(x=d.month,y=d.close*3,mode='lines',line=dict(color='#477d99',width=2.6),hovertemplate='Miesiąc %{x:.0f}<br>Wartość %{y:.2f}<extra></extra>'))
 xcut=(CUT-d.date.iloc[0]).days/30.4375+1
 if reveal:
  fig.add_vline(x=xcut,line_dash='dot',line_color='#999')
  fig.add_annotation(x=xcut,y=float(P[P.date==CUT].close.iloc[0]*3),text='DECYZJA',showarrow=True,ax=-30,ay=-30)
 else: fig.add_annotation(x=float(d.month.iloc[-1]),y=float(d.close.iloc[-1]*3),text='TERAZ',showarrow=True,ax=-32,ay=-32)
 ticks=list(range(1,76 if reveal else 63,12))
 fig.update_layout(template='plotly_white',height=350,margin=dict(l=10,r=10,t=15,b=10),xaxis=dict(title='Czas (daty ukryte)',tickmode='array',tickvals=ticks,ticktext=[f'Miesiąc {t}' for t in ticks]),yaxis=dict(title='Kurs (USD)',gridcolor='#edf0f3'),showlegend=False)
 st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})


def material(i):
 if i==0:
  st.subheader('Czym zajmuje się spółka?')
  st.write('Międzynarodowy armator przewożący ładunki masowe: rudę żelaza, węgiel, zboża i inne surowce. Przychody zależą między innymi od stawek frachtowych, liczby dostępnych statków i popytu na przewozy. Firma eksploatuje flotę dużych masowców.')
  lineplot()
  st.caption('Wykres uwzględnia korekty związane ze splitami i historycznymi wypłatami dywidend.')
 elif i==1:
  st.subheader('Dywidendy, które już wypłacono')
  st.write('Poniżej przedstawiono historyczne wypłaty dywidend na akcję. Nie są one prognozą przyszłych wypłat.')
  a,b=st.columns(2);a.metric('Wypłaty w ostatnich 12 miesiącach','19,50 USD / akcję');b.metric('Ostatnia wypłata','3,60 USD / akcję')
  divs=pd.DataFrame([['Marzec','6,00','15 marca'],['Czerwiec','4,95','16 czerwca'],['Wrzesień','4,95','8 września'],['Grudzień','3,60','12 grudnia']],columns=['Okres','USD na akcję','Data wypłaty'])
  st.dataframe(divs,hide_index=True,use_container_width=True)
  st.bar_chart(pd.DataFrame({'Wypłata':['III','VI','IX','XII'],'USD/akcję':[6.,4.95,4.95,3.6]}).set_index('Wypłata'),height=180)
  st.write('**Łącznie wypłacono 19,50 USD na akcję w ostatnim roku.** W poprzednim roku wypłaty wynosiły kolejno 0,90, 2,10 i 3,75 USD (łącznie 6,75 USD). Wysokość przyszłych dywidend nie jest gwarantowana.')
  st.write('**Historia wypłat:** dywidendy wypłacano przez kilka lat we wcześniejszym okresie, następnie nastąpiła wieloletnia przerwa. Wznowiono je trzy lata przed obecną decyzją, lecz wypłaty nadal nie były regularne. Nie jest to wieloletnia historia nieprzerwanych dywidend.')
  st.write('**Polityka dywidendowa:** kwartalne wypłaty zależą od dostępnej gotówki po pozostawieniu rezerwy płynnościowej powiązanej z wielkością floty. W ostatnim roku minimalna rezerwa wynosiła 2,1 mln USD na statek. Wysokie dywidendy z okresu dobrej koniunktury nie stanowią obietnicy podobnych wypłat w przyszłości.')
 elif i==2:
  st.subheader('Otoczenie makroekonomiczne: rynek frachtowy')
  st.write('**Baltic Dry Index (BDI)** to wskaźnik stawek przewozu suchych ładunków masowych. Nie jest indeksem cen kontenerów ani bezpośrednią stawką uzyskiwaną przez tę spółkę.')
  a,b,c=st.columns(3);a.metric('Szczyt BDI w cyklu','5 650 pkt');b.metric('BDI pod koniec okresu','1 515 pkt');c.metric('Zmiana od szczytu','−73%')
  st.write('Po wyjątkowo wysokich stawkach w poprzednim roku nastąpił silny spadek. W ostatnim roku indeks ponownie przechodził duże wahania: od około 965 pkt pod koniec sierpnia do ponad 3 300 pkt w maju.')
  st.write('**Dane operacyjne spółki pokazują podobne napięcie:** średnia dzienna stawka TCE w trzecim kwartale spadła z **30 626 USD** rok wcześniej do **24 365 USD**, czyli o około **20%**.')
  st.write('**Co wpływało na rynek?** Odbicie gospodarcze i ograniczenia przepustowości portów wcześniej podbijały stawki. Następnie słabsza aktywność przemysłowa, sytuacja w Chinach oraz zmiany dostępności statków i popytu na surowce zwiększały niepewność. BDI nie pozwala samodzielnie przewidzieć zysku armatora.')
 elif i==3:
  st.subheader('Wyniki i bilans')
  st.write('**Ostatni pełny raport roczny:** przychody **1 427 mln USD**, zysk netto **681 mln USD**. Rok wcześniej: przychody **693 mln USD**, zysk netto **9,7 mln USD**.')
  st.write('**Dostępne wyniki za dziewięć miesięcy bieżącego roku:** przychody **1 142 mln USD**, zysk netto **480 mln USD**, przepływy pieniężne z działalności operacyjnej **654 mln USD**.')
  st.write('**Trzeci kwartał, porównanie rok do roku:**')
  st.dataframe(pd.DataFrame({'Wskaźnik':['Przychody (mln USD)','Zysk netto (mln USD)','Dzienna stawka TCE (USD)'], 'Rok wcześniej':['415,7','220,4','30 626'],'Ostatni kwartał':['364,1','109,7','24 365']}),hide_index=True,use_container_width=True)
  a,b,c=st.columns(3);a.metric('Kapitał własny','2,06 mld USD');b.metric('Dług bankowy i leasing','1,38 mld USD');c.metric('Liczba statków','128')
  st.markdown('**Prognozy instytucji branżowej na kolejny rok**')
  st.write('W prezentacji inwestorskiej spółki przytoczono prognozy **Clarksons Research** dla globalnego rynku przewozów suchych ładunków masowych. Oczekiwano wzrostu pracy przewozowej (tonomil) o **1,4%** w kolejnym roku, w tym przewozów **węgla o 2,8%**, **zbóż o 4,3%** i **rudy żelaza o 0,1%**. To prognozy rynku frachtowego, a nie przychodów czy zysku samej spółki.')
  st.markdown('**Wycena i ryzyka**')
  st.write('Główne ryzyka: cykliczność stawek frachtowych, popyt na surowce (w tym z Chin), koszty paliwa i finansowania, nakłady na flotę oraz możliwość obniżenia dywidend w słabszym otoczeniu.')
