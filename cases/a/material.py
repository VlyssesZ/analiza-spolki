from pathlib import Path


import pandas as pd


import plotly.graph_objects as go


import streamlit as st


ROOT = Path(__file__).parent


CUT=pd.Timestamp('2000-09-01')


PRICE=pd.read_csv(ROOT/'prices_private.csv')


PRICE['month']=pd.to_datetime(PRICE['month']+'-01')


PAST=PRICE[(PRICE.month>=pd.Timestamp('1995-10-01'))&(PRICE.month<=CUT)].copy()


FUTURE=PRICE[(PRICE.month>=CUT)&(PRICE.month<=pd.Timestamp('2001-09-01'))].copy()


FIN=pd.read_csv(ROOT/'fundamentals_private.csv')


STAGES=['Wykres i działalność','Wyniki finansowe','Branża i konkurencja','Wycena i bilans']


def chart(df,forward=False):
    base=float(PAST.iloc[0].nominal_split_adjusted)
    y=df.nominal_split_adjusted*3
    x=list(range(1,len(df)+1))
    fig=go.Figure(go.Scatter(x=x,y=y,mode='lines',line=dict(color='#427a9c',width=2.8),hovertemplate='Miesiąc %{x}<br>Wartość %{y:.2f}<extra></extra>'))
    if forward:
        fig.add_vline(x=len(PAST),line_dash='dot',line_color='#777')
        fig.add_annotation(x=len(PAST),y=max(y),text='DECYZJA',showarrow=False,yshift=12)
    else:
        fig.add_annotation(x=len(df),y=y.iloc[-1],text='TERAZ',showarrow=True,arrowhead=2,ax=-35,ay=-30)
    fig.update_layout(height=330,margin=dict(l=5,r=10,t=35,b=15),showlegend=False,template='plotly_white',xaxis_title='Kolejne miesiące (bez dat)',yaxis_title='Kurs (USD)')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#edf0f3')
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})


def show_material(i, recalled=False):
        if i==0:
            st.subheader('Poznaj przedsiębiorstwo')
            st.write('Firma projektuje i sprzedaje urządzenia oraz oprogramowanie do budowy sieci komputerowych. Jej klientami są przedsiębiorstwa, operatorzy telekomunikacyjni i instytucje publiczne. Działa na wielu rynkach i rozwija ofertę również przez przejęcia innych firm.')
            st.caption('Wykres miesięczny. Kursy uwzględniają korekty związane ze splitami. W badanym okresie spółka nie wypłacała dywidend.')
            chart(PAST)
        elif i==1:
            st.subheader('Pięć lat wyników finansowych')
            f=FIN.copy();f['Rok']=[f'Rok {j}' for j in range(1,6)]
            fig=go.Figure()
            fig.add_trace(go.Bar(x=f.Rok,y=f.revenue_musd,name='Przychody',marker_color='#477da4'))
            fig.add_trace(go.Bar(x=f.Rok,y=f.net_income_musd,name='Zysk netto',marker_color='#b6a27b'))
            fig.update_layout(barmode='group',height=300,margin=dict(l=5,r=5,t=15,b=10),template='plotly_white',legend=dict(orientation='h',y=1.17),yaxis_title='mln USD')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.dataframe(f[['Rok','revenue_musd','net_income_musd']].rename(columns={'revenue_musd':'Przychody (mln)','net_income_musd':'Zysk netto (mln)'}),hide_index=True,use_container_width=True)
            st.caption('Wartości w mln USD; nazwy lat są ukryte. Zysk netto jest raportowany, obejmuje również pozycje związane z przejęciami.')
        elif i==2:
            st.subheader('Branża i konkurencja')
            st.markdown('**Rynek.** Przedsiębiorstwa i operatorzy inwestują w rozbudowę sieci transmisji danych. Rosnący ruch internetowy zwiększa zapotrzebowanie na infrastrukturę.\n\n**Pozycja spółki.** Firma należy do liderów rynku urządzeń sieciowych i posiada szeroką bazę klientów.\n\n**Konkurencja.** O zamówienia walczą także duże koncerny komputerowe i telekomunikacyjne. Rozwój technologii wymusza inwestycje w nowe produkty.\n\n**Przejęcia.** Firma kupuje inne przedsiębiorstwa, aby rozszerzać ofertę. Taka strategia wiąże się również z ryzykiem integracji i kosztami.')
            st.markdown('**Polityka dywidendowa.** Spółka nie wypłaca dywidendy. Stopa dywidendy: **0%**. Zyski pozostają w przedsiębiorstwie i wspierają jego rozwój. Na tym etapie nie podajemy dat ani nazwy firmy.')
            st.markdown('**Komentarz prezesa do ostatnich wyników**')
            st.markdown('> „Nie dostrzegamy na rynku oznak spowolnienia radykalnej transformacji działalności przedsiębiorstw związanej z Internetem. Przeciwnie, uważamy, że proces ten przyspiesza na całym świecie”.')
            st.caption('Prezes spółki · komentarz opublikowany przy okazji ostatnich wyników rocznych, kilka tygodni przed punktem decyzji. Tłumaczenie fragmentu autentycznej wypowiedzi; nazwa spółki, nazwisko i data ukryte.')
            
        else:
            st.subheader('Rentowność, bilans i wycena')
            sales=18928;net=2668
            a,b,c=st.columns(3)
            a.metric('Marża brutto','64,4%')
            b.metric('Marża netto',f'{100*net/sales:.1f}%'.replace('.',','))
            c.metric('Wzrost przychodów r/r',f'{100*(18928/12173-1):.1f}%'.replace('.',','))
            st.markdown('**Prognozy instytucji finansowych (dostępne w chwili decyzji)**')
            st.write('Analitycy **Merrill Lynch** prognozowali na kolejny rok obrotowy **26,5 mld USD przychodów** (wcześniejsza prognoza: 24,3 mld USD) oraz **2,10 USD zysku na akcję**  (wcześniejsza prognoza: 1,98 USD). **Credit Suisse First Boston** wskazywał 12-miesięczną cenę docelową **255 USD** . Są to oczekiwania, nie wyniki ani gwarancja osiągnięcia ceny docelowej.')
            st.write('**Co jeszcze wiemy?** Firma ma bardzo duży udział płynnych aktywów w bilansie i intensywnie finansuje rozwój oraz przejęcia. W ostatnim roku odnotowała znaczące koszty związane z akwizycjami.')



            a,b=st.columns(2)
            st.caption('Marża brutto i wyniki: ostatni dostępny raport roczny')
