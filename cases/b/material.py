from pathlib import Path


import pandas as pd


import plotly.graph_objects as go


import streamlit as st


ROOT = Path(__file__).parent


STAGES = ['Biznes i kurs', 'Dywidenda i zarząd', 'Wyniki finansowe', 'Ryzyko, branża i wycena']


F = pd.read_csv(ROOT / 'fundamentals_private.csv')


P = pd.read_csv(ROOT / 'prices_private.csv', parse_dates=['date'])


def fmt(v): return f'{v:,.0f}'.replace(',',' ')


def chart(reveal=False):
    # Weekly last observation; source adjusted price series. Display factor x3.
    cutoff=pd.Timestamp('2022-12-30')
    shown=P if reveal else P[P.date<=cutoff]
    # Ostatnie notowanie każdego tygodnia, bez interpolacji.
    shown=shown.set_index('date').resample('W-FRI').last().dropna(subset=['close']).reset_index()
    y=shown['close']*3
    x=(shown['date']-P.iloc[0]['date']).dt.days / 30.4375 + 1
    fig=go.Figure(go.Scatter(x=x,y=y,mode='lines',line=dict(color='#447c9b',width=2.5),hovertemplate='Miesiąc %{x:.0f}<br>Wartość %{y:.2f}<extra></extra>'))
    decision_x=float(((cutoff-P.iloc[0]['date']).days / 30.4375)+1)
    if reveal:
        fig.add_vline(x=decision_x,line_dash='dot',line_color='#888')
        v=float(P.loc[P.date==cutoff,'close'].iloc[0])*3
        fig.add_annotation(x=decision_x,y=v,text='DECYZJA',showarrow=True,ax=-35,ay=-35)
    else:
        fig.add_annotation(x=float(x.iloc[-1]),y=float(y.iloc[-1]),text='TERAZ',showarrow=True,ax=-35,ay=-35)
    tickvals=list(range(1,74,12)) if reveal else list(range(1,62,12))
    fig.update_layout(template='plotly_white',height=350,margin=dict(l=5,r=10,t=20,b=10),xaxis=dict(tickmode='array',tickvals=tickvals,ticktext=[f'Miesiąc {t}' for t in tickvals],title='Czas (daty ukryte)'),yaxis=dict(title='Kurs (USD)',gridcolor='#edf0f3'),showlegend=False)
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})


def show_material(i, recalled=False):
        if i==0:
            st.subheader('Czym zajmuje się spółka?')
            st.write('Międzynarodowa grupa zajmuje się dystrybucją gazu ziemnego i energii elektrycznej, sprzedażą gazu płynnego (LPG), infrastrukturą energetyczną i usługami związanymi z dostarczaniem energii. Obsługuje klientów indywidualnych i przedsiębiorstwa. Część działalności podlega regulacji taryfowej; pozostała jest bardziej zależna od konkurencji, cen surowców i pogody.')
            chart()
            st.caption('Wykres uwzględnia korekty związane ze splitami i historycznymi wypłatami dywidend.')
        elif i==1:
            st.subheader('Dywidendy i komentarz zarządu')
            st.write('**Historia dywidend:** spółka wypłacała je nieprzerwanie przez ponad 130 lat, a do momentu decyzji podnosiła roczną dywidendę przez 35 kolejnych lat. Jest to historia regularnych wypłat, nie gwarancja na przyszłość.')
            a,b=st.columns(2)
            a.metric('Lata nieprzerwanych wypłat','138')
            b.metric('Kolejne lata podwyżek','35')
            st.write('Ostatnio zadeklarowana kwartalna dywidenda: **1,08 USD na akcję**, czyli **4,32 USD rocznie** przy utrzymaniu tej stawki. W ostatniej podwyżce kwartalna kwota wzrosła o **4,3%**.')
            st.markdown('**Komentarz prezesa do podwyżki dywidendy**')
            st.markdown('> „Ta podwyżka odzwierciedla nasz mocny bilans i utrzymującą się pewność co do zdolności spółki do generowania gotówki”.')
            st.caption('Tłumaczenie fragmentu autentycznej wypowiedzi, opublikowanej przed punktem decyzji. Nazwisko, data i nazwa spółki ukryte.')
            st.caption('Historyczne wypłaty nie gwarantują przyszłych dywidend.')
        elif i==2:
            st.subheader('Pięć lat wyników')
            f=F.copy();f['Rok']=[f'Rok {j}' for j in range(1,6)]
            fig=go.Figure()
            fig.add_trace(go.Bar(x=f.Rok,y=f.revenue_musd,name='Przychody',marker_color='#447c9b'))
            fig.add_trace(go.Bar(x=f.Rok,y=f.net_income_attributable_musd,name='Zysk netto',marker_color='#b49d76'))
            fig.update_layout(template='plotly_white',height=300,barmode='group',margin=dict(l=5,r=5,t=15,b=10),legend=dict(orientation='h',y=1.18),yaxis_title='mln USD')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.dataframe(pd.DataFrame({'Rok':f.Rok,'Przychody (mln)':f.revenue_musd.map(fmt),'Zysk netto (mln)':f.net_income_attributable_musd.map(fmt)}),hide_index=True,use_container_width=True)
            st.caption('Zysk netto (mln USD). Wynik może uwzględniać zmiany wyceny instrumentów finansowych.')
        else:
            st.subheader('Co jeszcze wiemy?')
            a,b=st.columns(2)
            a.metric('Marża netto (ostatni rok)',f'{100*1073/10106:.1f}%'.replace('.',','))
            b.metric('Przychody r/r',f'{100*(10106/7447-1):+.1f}%'.replace('.',','))
            st.markdown('**Prognozy zarządu (dostępne w chwili decyzji)**')
            st.write('Zarząd spółki podtrzymywał prognozę **skorygowanego zysku na akcję na kolejny rok obrotowy w przedziale 8,55–9,45 USD** . Długoterminowe cele obejmowały wzrost skorygowanego EPS o **6–10% rocznie** i wzrost dywidendy o **4% rocznie**. To deklarowane cele, nie gwarantowane wyniki.')
            st.markdown('**Działalność.** Część grupy to regulowane sieci energetyczne, część to sprzedaż LPG i usługi energetyczne. Wyniki zależą m.in. od pogody, cen energii, regulacji i kosztów finansowania.\n\n**Nakłady inwestycyjne.** Spółka rozbudowuje infrastrukturę i inwestuje w modernizację sieci oraz wybrane projekty energetyczne.\n\n**Bilans.** To kapitałochłonny biznes korzystający z finansowania dłużnego. W ocenie ryzyka ważne są zarówno dług, jak i zdolność do finansowania dywidend i inwestycji z przepływów pieniężnych.')
