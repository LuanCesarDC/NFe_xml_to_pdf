import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from datetime import date
import requests
import json
from pandas import json_normalize


####### GERA UM PDF NO FORMATO DE NFe de SP, USANDO COMO ENTRADA UM ARQUIVO XML
####### PARA USAR A FUNÇÃO, BASTA CHAMAR A FUNÇÃO:  xml_para_pdf('''dados do arquivo xml''')
####### OS DADOS DEVEM ESTAR ENTRE ASPAS SIMPLES TRIPLAS '''dados'''
####### OS DADOS SÃO O CONTEUDO DO XML, BASTA COPIAR E COLAR
####### NAO ESQUECER DE INSTALAR AS BIBLIOTECAS ANTERIORES (reportlab, pandas, ...)

CNPJ_EMISSOR = ''  # 'xx.xxx.xxx/xxxx-xx' CNPJ do emissor da NFe NO FORMATO INDICADO ANTERIORMENTE


# tipo_dado = 0 para extrair os dados do Prestador
# tipo_dado = 1 para extrair os dados do Tomador
# tipo_dado = 2 para extrair os dados gerais
def extrair_dados_xml(data, tipo_dado):
    myroot = ET.fromstring(data)
    cdata = myroot[0][0][0].text
    root = ET.fromstring(cdata);
    inf_prestador = {}
    inf_tomador = {}
    inf_gerais = {}
    if(tipo_dado == 0):
        #COLETA DE DADOS DO PRESTADOR
        for x in root[1].findall('CPFCNPJPrestador'):
            inf_prestador[x.find('CNPJ').tag] = x.find('CNPJ').text
        inf_prestador[root[1].find('RazaoSocialPrestador').tag] = root[1].find('RazaoSocialPrestador').text
        inf_prestador[root[1].find('EmailPrestador').tag] = root[1].find('EmailPrestador').text
        for x in root[1].findall('EnderecoPrestador'):
            for y in x:
                inf_prestador[y.tag] = y.text
        for x in root[1].findall('ChaveRPS'):
            for y in x:
                inf_prestador[y.tag] = y.text
        for x in root[1].findall('ChaveNFe'):
            for y in x:
                inf_prestador[y.tag] = y.text
        return inf_prestador
    elif(tipo_dado == 1):
        #COLETA DE DADOS DO TOMADOR
        for x in root[1].findall('CPFCNPJTomador'):
            inf_tomador[x.find('CNPJ').tag] = x.find('CNPJ').text
        inf_tomador[root[1].find('RazaoSocialTomador').tag] = root[1].find('RazaoSocialTomador').text
        inf_tomador[root[1].find('EmailTomador').tag] = root[1].find('EmailTomador').text
        for x in root[1].findall('EnderecoTomador'):
            for y in x:
                inf_tomador[y.tag] = y.text
        inf_tomador[root[1].find('InscricaoMunicipalTomador').tag] = root[1].find('InscricaoMunicipalTomador').text
        return inf_tomador
    elif(tipo_dado == 2):
        #COLETA DE OUTROS DADOS
        inf_gerais[root[1].find('StatusNFe').tag] = root[1].find('StatusNFe').text
        inf_gerais[root[1].find('TributacaoNFe').tag] = root[1].find('TributacaoNFe').text
        inf_gerais[root[1].find('OpcaoSimples').tag] = root[1].find('OpcaoSimples').text
        inf_gerais[root[1].find('NumeroGuia').tag] = root[1].find('NumeroGuia').text
        inf_gerais[root[1].find('ValorServicos').tag] = root[1].find('ValorServicos').text
        inf_gerais[root[1].find('ValorPIS').tag] = root[1].find('ValorPIS').text
        inf_gerais[root[1].find('ValorCOFINS').tag] = root[1].find('ValorCOFINS').text
        inf_gerais[root[1].find('ValorIR').tag] = root[1].find('ValorIR').text
        inf_gerais[root[1].find('ValorCSLL').tag] = root[1].find('ValorCSLL').text
        inf_gerais[root[1].find('CodigoServico').tag] = root[1].find('CodigoServico').text
        inf_gerais[root[1].find('AliquotaServicos').tag] = root[1].find('AliquotaServicos').text
        inf_gerais[root[1].find('ValorISS').tag] = root[1].find('ValorISS').text
        inf_gerais[root[1].find('ValorCredito').tag] = root[1].find('ValorCredito').text
        inf_gerais[root[1].find('ISSRetido').tag] = root[1].find('ISSRetido').text
        inf_gerais[root[1].find('DataEmissaoNFe').tag] = root[1].find('DataEmissaoNFe').text
        inf_gerais[root[1].find('NumeroLote').tag] = root[1].find('NumeroLote').text
        inf_gerais[root[1].find('TipoRPS').tag] = root[1].find('TipoRPS').text
        inf_gerais[root[1].find('DataEmissaoRPS').tag] = root[1].find('DataEmissaoRPS').text
        inf_gerais[root[1].find('Discriminacao').tag] = root[1].find('Discriminacao').text
        return inf_gerais

def xml_para_pdf(data):
    #VARIAVEIS NECESSARIAS PARA A CONSTRUÇÃO DO PDF
    #Prestador:
    inf_prestador = extrair_dados_xml(data, 0)

    cpf_cnpj_prestador = inf_prestador['CNPJ'];
    cpf_cnpj_prestador_formatado = str(cpf_cnpj_prestador[:2] + '.' + cpf_cnpj_prestador[2:5] + '.' + cpf_cnpj_prestador[5:8] + '/' + cpf_cnpj_prestador[8:12] + '-' + cpf_cnpj_prestador[12:])
    nome_razao_social_prestador = inf_prestador['RazaoSocialPrestador'];
    tipo_logradouro_prestador = inf_prestador['TipoLogradouro'];
    logradouro_prestador = inf_prestador['Logradouro'];
    num_endereco_prestador = inf_prestador['NumeroEndereco'];
    bairro_prestador = inf_prestador['Bairro'];
    cod_cidade_prestador = inf_prestador['Cidade']; #API que retorna o nome da cidade através do seu código
    cidade_prestador_req = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{}".format(cod_cidade_prestador))
    cidade_prestador_json = str(cidade_prestador_req.json())
    cidade_prestador_json = cidade_prestador_json.replace("'","\"")
    dados = json.loads(cidade_prestador_json)
    DF = json_normalize(dados)
    cidade_prestador = DF['microrregiao.mesorregiao.UF.nome'].values[0]
    uf_prestador = inf_prestador['UF']
    cep_prestador = str(inf_prestador['CEP']).zfill(8)
    cep_prestador_formatado = str('{}-{}'.format(cep_prestador[:5], cep_prestador[5:]))
    insc_municipal_prestador = inf_prestador['InscricaoPrestador']
    insc_municipal_prestador_formatada = str('{}.{}.{}-{}'.format(insc_municipal_prestador[:1], insc_municipal_prestador[1:4], insc_municipal_prestador[4:7], insc_municipal_prestador[7:]))
    num_rps = inf_prestador['NumeroRPS']
    serie_rps = inf_prestador['SerieRPS']

    #Tomador:
    inf_tomador = extrair_dados_xml(data, 1)

    cpf_cnpj_tomador = inf_tomador['CNPJ']
    cpf_cnpj_tomador_formatado = str(cpf_cnpj_tomador[:2] + '.' + cpf_cnpj_tomador[2:5] + '.' + cpf_cnpj_tomador[5:8] + '/' + cpf_cnpj_tomador[8:12] + '-' + cpf_cnpj_tomador[12:])
    nome_razao_social_tomador = inf_tomador['RazaoSocialTomador']
    tipo_logradouro_tomador = inf_tomador['TipoLogradouro']
    logradouro_tomador = inf_tomador['Logradouro']
    num_endereco_tomador = inf_tomador['NumeroEndereco']
    bairro_tomador = inf_tomador['Bairro']
    cod_cidade_tomador = inf_tomador['Cidade']
    cidade_tomador_req = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{}".format(cod_cidade_tomador))
    cidade_tomador_json = json.dumps(cidade_prestador_req.json());
    cidade_tomador_json = cidade_tomador_json.replace("'", "\"")
    dados = json.loads(cidade_tomador_json)
    DF = json_normalize(dados)
    cidade_tomador = DF['microrregiao.mesorregiao.UF.nome'].values[0]
    uf_tomador = inf_tomador['UF']
    cep_tomador = str(inf_tomador['CEP']).zfill(8)
    cep_tomador_formatado = str('{}-{}'.format(cep_tomador[:5], cep_tomador[5:]))
    insc_municipal_tomador = inf_tomador['InscricaoMunicipalTomador']
    insc_municipal_tomador_formatada = str('{}.{}.{}-{}'.format(insc_municipal_tomador[:1], insc_municipal_tomador[1:4], insc_municipal_tomador[4:7], insc_municipal_tomador[7:]))
    email_tomador = inf_tomador['EmailTomador']

    #Gerais:
    inf_gerais = extrair_dados_xml(data, 2)

    num_nota = str(inf_prestador['NumeroNFe'])
    data_emiss = str(inf_gerais['DataEmissaoNFe'])[:10]
    hora_emiss = str(inf_gerais['DataEmissaoNFe'])[11:]
    data_emiss = data_emiss[8:] + '/' + data_emiss[5:7] + '/' + data_emiss[:4]
    cod_verif = str(inf_prestador['CodigoVerificacao'])
    cod_verif_formatado = cod_verif[:4] + '-' + cod_verif[4:]
    data_emiss_rps = str(inf_gerais['DataEmissaoRPS'])[:10]
    data_emiss_rps = data_emiss_rps[8:] + '/' + data_emiss_rps[5:7] + '/' + data_emiss_rps[:4]
    mes_emiss_rps = int(data_emiss_rps[3:5])
    ano_emiss_rps = int(data_emiss_rps[6:])
    discrim_servicos = inf_gerais['Discriminacao']
    val_servicos = str('{:.2f}'.format(float(inf_gerais['ValorServicos'])))
    irrf = str('{:.2f}'.format(float(inf_gerais['ValorIR'])))
    csll = str('{:.2f}'.format(float(inf_gerais['ValorCSLL'])))
    cofins = str('{:.2f}'.format(float(inf_gerais['ValorCOFINS'])))
    pis_pasep = str('{:.2f}'.format(float(inf_gerais['ValorPIS'])))
    val_tot_deducoes = '0,00'
    base_calculo = val_servicos
    aliquota = float(inf_gerais['AliquotaServicos'])
    aliquota = str('{:.2f}'.format(100*aliquota)) + '%'
    val_iss = str('{:.2f}'.format(float(inf_gerais['ValorISS'])))
    credito = float(inf_gerais['ValorCredito'])
    credito = str('{:.2f}'.format(credito))
    if(mes_emiss_rps != 12):
        vencimento_rps = data_emiss_rps[:2] + '/' + str(mes_emiss_rps + 1).zfill(2) + '/' + str(ano_emiss_rps)
    else:
        vencimento_rps = data_emiss_rps[:2] + '/01' + '/' + str(ano_emiss_rps+1)
    cod_servico = '06564 - Cobranças e recebimentos por conta de terceiros e congêneres.'
    outras_inf = '(1) Esta NFS-e foi emitida com respaldo na Lei nº 14.097/2005; (2) Esta NFS-e não gera crédito; (3) Esta NFS-e substitui o RPS' \
                 ' Nº {} Série {}, emitido em {}; (4) Data de Vencimento do ISS desta NFS-e: {}'.format(num_rps, serie_rps, data_emiss_rps, vencimento_rps)
    confirmacao = str('https://nfe.prefeitura.sp.gov.br/contribuinte/notaprint.aspx?inscricao={}&nf={}&verificacao={}'.format(insc_municipal_prestador, int(num_nota), cod_verif))
    data_hoje = date.today()
    dia_hoje = data_hoje.strftime("%d/%m/%Y")
    inf_nota_cabecalho = str('Usuário: {} - NF-e - Nota Fiscal Eletrônica de Serviços - São Paulo'.format(CNPJ_EMISSOR))


    ### GERAR O PDF ###
    pdf = canvas.Canvas(str('NFS-e_' + num_nota + '.pdf'))
    num_nota = num_nota.zfill(8)
    pdf.drawInlineImage('back.jpg', 56, 202, 487, 597)
    pdf.setTitle(str('NFS-e_' + num_nota))

    #CABEÇALHO
    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(460, 777, num_nota)
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(445, 757, str(data_emiss + ' ' + hora_emiss))
    pdf.drawString(460, 736, cod_verif_formatado)
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(189, 735, 'RPS Nº {} Série {}, emitido em {}'.format(num_rps, serie_rps, data_emiss_rps))

    #PRESTADOR DE SERVIÇOS
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(164, 709, cpf_cnpj_prestador_formatado)
    pdf.drawString(192, 699, nome_razao_social_prestador)
    pdf.drawString(158, 688, str(tipo_logradouro_prestador + ' ' + logradouro_prestador + ' ' + num_endereco_prestador) + ' - ' + bairro_prestador + ' - CEP: ' + cep_prestador_formatado)
    pdf.drawString(159, 677, cidade_prestador)
    pdf.drawString(415, 710, insc_municipal_prestador_formatada)
    pdf.drawString(356, 678, uf_prestador)

    #TOMADOR DE SERVIÇOS
    pdf.drawString(138, 643, nome_razao_social_tomador)
    pdf.drawString(108, 633, cpf_cnpj_tomador_formatado)
    pdf.drawString(105, 622, str(tipo_logradouro_tomador + ' ' + logradouro_tomador + ' ' + num_endereco_tomador) + ' - ' + bairro_tomador + ' - CEP: ' + cep_tomador_formatado)
    pdf.drawString(104, 611, cidade_tomador)
    pdf.drawString(416, 633, insc_municipal_tomador_formatada)
    pdf.drawString(272, 611, uf_tomador)
    pdf.drawString(327, 611, email_tomador)

    #INTERMEDIARIO DE SERVICOS
    pdf.drawString(109, 586, '---')
    pdf.drawString(265, 586, '---')

    #DISCRIMINAÇÃO DOS SERVIÇOS
    pdf.setFont('Helvetica', 8)
    pdf.drawString(61, 557, discrim_servicos[:92])
    pdf.drawString(68, 547, discrim_servicos[92:])

    #VALORES SERVIÇO
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(105, 323, '-')
    pdf.drawString(193, 323, irrf)
    pdf.drawString(286, 323, csll)
    pdf.drawString(385, 323, cofins)
    pdf.drawString(477, 323, pis_pasep)
    pdf.drawString(62, 305, cod_servico)
    pdf.drawString(86, 285, val_tot_deducoes)
    pdf.drawString(187, 285, base_calculo)
    pdf.drawString(279, 285, aliquota)
    pdf.drawString(367, 285, val_iss)
    pdf.drawString(482, 285, credito)
    pdf.drawString(146, 267, '-')
    pdf.drawString(296, 267, '-')
    pdf.drawString(445, 267, '-')
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(355, 344, val_servicos)

    #OUTRAS INFORMAÇÕES
    pdf.setFont('Helvetica', 8)
    pdf.drawString(62, 238, outras_inf[:126])
    pdf.drawString(62, 228, outras_inf[126:])
    pdf.drawString(10, 10, confirmacao)
    pdf.drawString(10, 822, dia_hoje)
    pdf.drawString(168, 822, inf_nota_cabecalho)
    pdf.drawString(570, 10, '1/1')

    pdf.save()

