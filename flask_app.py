from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import models
import plotly as plt
import plotly.graph_objs as go
import json
import pandas as pd
import numpy as np
import time


def conv_gb(val):
    val = round(val/1024,3)
    return val

# Busca programas que causam lentidão
def prog_lentidao(instalados):
    # lista de programas que podem causar lentidão
    progs_exc = ['Steam','Origin','GOG Galaxy','Total Security','Avira','AVG',
                'Avast','Kaspersky','Bitdefender','F-Secure','McAfee','ESET','G-Lock',
                'Symantec','SpyHunter','Ad-Aware','Panda Antivirus','Norton AntiVirus',
                'ESET NOD32','Microsoft Security Essentials','PW Clean','Comodo','NANO',
                'Dr.Web','Baidu','ClamWin','Protector Plus','PC Tools','Mx One','Emco',
                'ADinf32','F-Prot','PSafe','G DATA','Abacre','CS Anti-Virus','CMC Antivirus',
                'Sophos','Forefront Client','IObit','RemoveIT','Multi Virus','Zillya',
                'Rising','Naevius','Safety Scanner','RegRun','Trend Micro','eScan','Agnitum',
                'Autorun Virus','VIPRE','Standalone System Sweeper','Moon Secure','NoVirus',
                'Bittorrent','Utorrent','Adobe']

    excluir = []
    for i in range(len(instalados)):
        if any(prog in str(instalados[i].prog_nome) for prog in progs_exc):
            excluir.append(instalados[i])
    return excluir

 # Busca navegadores
def prog_naveg(instalados):
    # lista navegadores
    navegadores = ['Google Chrome','Mozilla Firefox','Microsoft Edge',
                   'Opera','Apple Safari','Pale Moon']
    clt_naveg = []

    for i in range(len(instalados)):
        if any(nav in str(instalados[i].prog_nome) for nav in navegadores):
            clt_naveg.append(instalados[i])
    return clt_naveg

# Busca programas de uso de determinada empresa
def prog_emp(instalados,ocor_id):

    uso_emp = ['Java','IdManager','PostgreSQL','Microsoft']

    clt_progEmp = []

    for i in range(len(instalados)):
        if any(prog in str(instalados[i].prog_nome) for prog in uso_emp):
            clt_progEmp.append(instalados[i])

    clt_progEmp = pd.DataFrame(clt_progEmp)
    if len(clt_progEmp)>0:
        clt_progEmp['status'] = 'Parado'
        clt_progEmp = clt_progEmp.rename(columns={0:'programa',1:'versao',2:'status'})
        # verifica se programas estão com serviço ativo
        for i in range(len(clt_progEmp)):
            validaExecucao(clt_progEmp.loc[i,'programa'],ocor_id)
        if True:
            clt_progEmp.loc[i,'status'] = 'Em Execução'
            
    return clt_progEmp

# Verifica se determinado processo está em execução
def validaExecucao(processName,ocor_id):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    
    ds_processos = pd.read_sql(
        models.Ocor_proc.query
        .filter(models.Ocor_proc.ocor_id == ocor_id)
        .statement, db.engine)
    
    #Iterate over the all the running process
    for proc in ds_processos['proc_nome']:
        try:
            # Check if process name contains the given name string.
            if any(processName.lower() == proc.lower()):
                return True
        except:
            pass
    return False


# cria figura de histórico de consumo de memoria
def fig_statusMemo(ocor_id):
    
    maq_id = pd.read_sql(
        models.Ocor_bios.query
        .with_entities(models.Ocor_bios.id_maq)
        .filter(models.Ocor_bios.ocor_id==ocor_id)
        .statement, db.engine).values[0][0]
    
    tab_memoGeral =pd.read_sql(
        db.session.query(models.Ocor_bios) \
        .with_entities(models.Ocor_bios.data_ocor,
                       models.Ocor_bios.memo_total,
                       models.Ocor_bios.memo_disp) \
        .filter(models.Ocor_bios.id_maq == maq_id) \
        .statement, db.engine)   # utiliza-se '.statement' para que
                                 # se utilize apenas o comando sql gerado

    # define configuração das linhas de total de memo
    # e memoria disponivel
    trace0 = go.Scatter(x=tab_memoGeral['data_ocor'],
                        y=tab_memoGeral['memo_total'],
                        name='Memoria Total')
    trace1 = go.Scatter(x=tab_memoGeral['data_ocor'],
                        y=tab_memoGeral['memo_disp'],
                        line={'color':'rgb(95,158,160)'},
                        name='Memoria Disponível')
    # define dados das linhas que servirão de referência
    # para status de memória
    trace2 = go.Scatter(x=tab_memoGeral['data_ocor'],
                     y=(tab_memoGeral['memo_total']*0.2),
                     line={'color':'rgb(255,69,0)',
                           'width': 1,'dash':'dot'},
                     mode='lines',name='Status Baixo')
    trace3 = go.Scatter(x=tab_memoGeral['data_ocor'],
                     y=(tab_memoGeral['memo_total']*0.1),
                     line={'color':'rgb(255,0,0)',
                           'width': 1,'dash':'dot'},
                     mode='lines',name='Status Crítico')

    data = [trace0,trace1,trace2,trace3]
    layout = go.Layout(title=' Histórico de Memoria total vs Memoria disponivel',
                       yaxis={'title':'Valores em Mb'},
                       height = 500,
                       width = 1200)
    fig = dict(data=data, layout=layout)
    # gera gráfico em json
    figMemo_json = json.dumps(fig,cls=plt.utils.PlotlyJSONEncoder)
    return figMemo_json

def fig_statusHd(ocor_id):

    ds_hd = pd.read_sql(
        db.session.query(models.Ocor_bios) \
        .with_entities(models.Ocor_bios.data_ocor) \
        .filter(models.Ocor_bios.ocor_id == ocor_id) \
        .add_columns(models.Ocor_hd.hd_nome,
                     models.Ocor_hd.hd_tamanho,
                     models.Ocor_hd.hd_livre) \
        .filter(models.Ocor_hd.ocor_id == ocor_id) \
        .statement, db.engine)   # utiliza-se '.statement' para que
                                 # se utilize apenas o comando sql gerado
    # calcula qtd de uso do hd e referencia valores em gb
    ds_hd['hd_tamanho'] = round((ds_hd['hd_tamanho'] - ds_hd['hd_livre'])/1024/1024,2)
    ds_hd['hd_livre'] = round(ds_hd['hd_livre']/1024/1024,2)

    ds_hd = ds_hd.pivot(
        index='data_ocor',
        columns='hd_nome',
        values=['hd_tamanho','hd_livre'])
    # seleciona as diferentes referências de HDs
    unic_hds = ds_hd.columns.get_level_values(1).unique()
    rotulos = ['Espaço Ocupado', 'Espaço Livre']
    layout = go.Layout(title='Análise e Discos Rígidos (HD) - valores de referência em Gb',
                       height = 400,
                       width = 600
                       )

    if len(unic_hds) == 1:
        data = [go.Pie(labels=rotulos,values=ds_hd.values[0])]
        fig = go.Figure(data=data,layout=layout)

    elif len(unic_hds) == 2:
        domains=[{'x':[0, 0.55], 'y':[0.2,0.8]},
                 {'x':[0.55, 1], 'y':[0.2,0.8]}]

        data=[]   # armazena os valores utilizados no gráfico 
        for hd,d in zip(unic_hds,domains):  # é necessário usar a função zip para fazer loop simultaneo
            valores = ds_hd.loc[:,ds_hd.columns.get_level_values(1) == hd].values[0]
            data.append({'labels':rotulos,
                         'values':valores,
                         'name': 'Unidade '+ hd,
                         'type':'pie',
                         'domain':d
                        })
        
        fig = dict(data=data,layout=layout)
        
    elif len(unic_hds) == 3:
        domains=[{'x':[0, 0.25], 'y':[0,0.5]},
                 {'x':[0.25, 0.65], 'y':[0,0.5]},
                 {'x':[0.6,1], 'y':[0,0.5]}]

        data=[]  # armazena os valores utilizados no gráfico
        for hd,d in zip(unic_hds,domains):  # é necessário usar a função zip para fazer loop simultaneo
            valores = ds_hd.loc[:,ds_hd.columns.get_level_values(1) == hd].values[0]
            data.append({'labels':rotulos,
                         'values':valores,
                         'name': 'Unidade '+ hd,
                         'type':'pie',
                         'domain':d
                        })   
        fig = dict(data=data,layout=layout)
    else:
        # estabelece limite máximo de 4 hds a serem considerados
        unic_hds = [unic_hds[:4]] 
        domains=[{'x':[0, 0.33], 'y':[0.6,1]},     #cell(1,1)
                 {'x':[0.66, 1], 'y':[0.6,1]},     #cell (1,2)
                 {'x':[0, 0.33], 'y':[0,0.45]},     #cell (2,1)
                 {'x': [0.66, 1], 'y':[0,0.45]}]    #cell (2,1)    
        data=[]  # armazena os valores utilizados no gráfico
        for hd,d in zip(unic_hds,domains):  # é necessário usar a função zip para fazer loop simultaneo
            valores = ds_hd.loc[:,ds_hd.columns.get_level_values(1) == hd].values[0]
            data.append({'labels':rotulos,
                         'values':valores,
                         'name': 'Unidade '+ hd,
                         'type':'pie',
                         'domain':d
                        })
     
        fig = dict(data=data,layout=layout)

    # gera gráfico em json
    figHd_json = json.dumps(fig,cls=plt.utils.PlotlyJSONEncoder)
    
    return figHd_json

    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
# database teste -> so1teste | user -> rocknguns | psw -> masterkey
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://rocknguns:masterkey@db4free.net:3306/so1teste'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

@app.route('/')
def index():
    user=''
    loja=''
    return render_template('index.html', user=user,loja=loja)

    
@app.route('/lista_db')
def lista_db():
     # instancia modelo de ocorrencia
    col_bios = ['Id Ocorrencia','Id Maquina','Processador',
                'Qtd Núcleos','Memo Total','Memo Disp.',
                'Nome Maquina','Data Ocorencia']
    
    # armazena dados do banco ref a bios
    dic_bios = db.session.query(models.Ocor_bios).all()
    titulo_pag = 'Servidor Id_Diag  -  Consulta banco de dados'

    return render_template('lista_db.html',
                           titlo_pag = titulo_pag,
                           col_bios=col_bios,
                           dic_bios=dic_bios)

@app.route('/lista_db/<ocor_id>')
def detalha_ocor(ocor_id):
    
    col_proc = ['Processo Nome','Consumo Memoria','Consumo CPU']

    #busca ocorrencia pelo id passado
    det_ocor = db.session.query(models.Ocor_bios).get(ocor_id)

    dic_proc = db.session.query(models.Ocor_proc
    ).with_entities(models.Ocor_proc.proc_nome,
                    func.sum(models.Ocor_proc.proc_memo).label('proc_memo'),
                    func.sum(models.Ocor_proc.proc_cpu).label('proc_cpu')
    ).filter(models.Ocor_proc.ocor_id == ocor_id
    ).group_by(models.Ocor_proc.proc_nome
    ).all()
    
    instalados = det_ocor.instalados
    # busca programas que podem causar lentidão
    excluir = prog_lentidao(instalados)
    clt_naveg = prog_naveg(instalados)
    # busca programas relacionados à determinada empresa
    clt_progEmp = prog_emp(instalados,ocor_id)
    
    # busca impressoras
    imp = det_ocor.impressoras
    ping = det_ocor.teste_ping
    net = det_ocor.teste_net
    
    # renderiza grafico de status de memoria que leva
    # em consideração o histórico de chamados do clt                  
    figMemo = fig_statusMemo(ocor_id)
    # renderiza grafico de status de HD                 
    figHd = fig_statusHd(ocor_id)
        
    return render_template('detalha_ocor.html',col_proc=col_proc,
                           det_ocor=det_ocor,dic_proc=dic_proc,
                           figMemo=figMemo,figHd=figHd,excluir=excluir,
                           clt_naveg=clt_naveg,clt_progEmp=clt_progEmp,
                           imp=imp,ping=ping,net=net)   

#@app.teardown_request
#def finaliza_sessao(exception=None):
#    db.session.remove()

if __name__ == '__main__':
    app.run(debug=True)
    
