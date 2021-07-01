# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OcoDialog
                                 A QGIS plugin
 Faz layout das ocorrencias. morfo. pranchas e relatorio
                             -------------------
        begin                : 2021-02-24
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Romario Moraes Carvalho Neto
        email                : romariocarvalho@hotmail.com
 ***************************************************************************/

"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtGui import QPixmap, QIntValidator
from qgis.core import QgsMapLayerProxyModel
from qgis.PyQt.QtWidgets import QMessageBox

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'oco_dialog_base.ui'))


class OcoDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(OcoDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>. and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.plugin_dir = os.path.dirname(__file__)
        self.setupUi(self)
        self.mQgsFileWidget.setStorageMode(QgsFileWidget.GetDirectory)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.icones()
        self.groupBox_oco_margem.setEnabled(False)
        self.groupBox_oco_leito.setEnabled(False)
        self.groupBox_morfo.setEnabled(False)
        self.groupBox_oco_margem.clicked.connect(self.unirGroupBox)
        self.button_box.setEnabled(False)
                
        self.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.mMapLayerComboBox_2.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBox_3.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.mMapLayerComboBox_4.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.label_quanti_fotos.clear()
        self.label_quanti_pts.clear()
        self.label_nome_foto.clear()
        self.label_nome_ponto.clear()

        self.onlyInt = QIntValidator()
        self.larg_M_LineEdit.setValidator(self.onlyInt)

        # controle inicial de entrada de dados:
        self.primeiraVez = 0 #vai mudar quando carregar os fields
        self.mMapLayerComboBox_2.setEnabled(False)
        self.mMapLayerComboBox_3.setEnabled(False)
        self.mMapLayerComboBox_4.setEnabled(False)
        self.larg_M_LineEdit.setEnabled(False)
        self.mQgsDoubleSpinBox.setEnabled(False)
        self.mQgsDoubleSpinBox.setValue(8)
        self.comboBox_atr.setEnabled(False)
        self.mQgsFileWidget.setEnabled(False)

        self.mMapLayerComboBox.layerChanged.connect(lambda: self.mMapLayerComboBox_3.setEnabled(True))
        self.mMapLayerComboBox_3.layerChanged.connect(lambda: self.mMapLayerComboBox_2.setEnabled(True))
        self.mMapLayerComboBox_2.layerChanged.connect(lambda: self.mMapLayerComboBox_4.setEnabled(True))
        self.mMapLayerComboBox_2.layerChanged.connect(self.trancaForcarVerificacao)   
        self.mMapLayerComboBox_2.layerChanged.connect(self.carregarFields)     
        self.mMapLayerComboBox_4.layerChanged.connect(lambda: self.larg_M_LineEdit.setEnabled(True)) 
        self.mMapLayerComboBox_4.layerChanged.connect(self.trancaForcarVerificacao)
        self.mMapLayerComboBox_4.layerChanged.connect(self.carregarFields)
        
        self.larg_M_LineEdit.valueChanged.connect(lambda: self.mQgsDoubleSpinBox.setEnabled(True))
        self.larg_M_LineEdit.valueChanged.connect(lambda: self.comboBox_atr.setEnabled(True))
        #self.mQgsDoubleSpinBox.valueChanged.connect(lambda: self.comboBox_atr.setEnabled(True))
        self.comboBox_atr.clear()
        self.comboBox_atr.activated.connect(self.verificarFieldsPontos)  #add aqui função para verificar se o field selecionado está no outro layer

        self.lista_radio_buttons = [[self.radioButton_erosiva_fraca,'Erosiva Fraca','255,255,185'],
                                    [self.radioButton_erosiva_media,'Erosiva Média','255,242,0'],
                                    [self.radioButton_erosiva_forte,'Erosiva Forte','255,201,14'],
                                    [self.radioButton_erosiva_muito,'Erosiva Muito Forte','255,128,0'],
                                    [self.radioButton_construtiva_fraca,'Construtiva Fraca','191,255,191'],
                                    [self.radioButton_construtiva_media,'Construtiva Média','0,255,0'],
                                    [self.radioButton_construtiva_forte,'Construtiva Forte','0,200,0'],
                                    [self.radioButton_construtiva_muito,'Construtiva Muito Forte','0,120,0'],
                                    [self.radioButton_neutra_fraca,'Neutra Fraca','174,225,238'],
                                    [self.radioButton_neutra_media,'Neutra Média','5,194,250'],
                                    [self.radioButton_neutra_forte,'Neutra Forte','0,120,240'],
                                    [self.radioButton_neutra_muito,'Neutra Muito Forte','0,0,232'],
                                    [self.radioButton_altura_baixo,'N//A','funcao'],
                                    [self.radioButton_altura_medio,'N//A','funcao'],
                                    [self.radioButton_altura_alto,'N//A','funcao']]
        
    def icones(self):
        """Carrega figura inicial e as figuras 40x25 pixel"""
        photoInicial = QPixmap(f'{self.plugin_dir}//imagens//FiguraInicial.jpg')
        self.photo.clear()
        #self.label_3.setPixmap(photoInicial)
        self.photo.setPixmap(photoInicial)

        ## margem
        self.lista_icones_margem = [[self.label_viva_margem,'viva_margem.png'],
                                    [self.label_morta_margem,'morta_margem.png'],
                                    [self.label_acesso,'acesso.png'],
                                    [self.label_cerca,'cerca.png'],
                                    [self.label_rampa,'rampa.png'],
                                    [self.label_foz,'foz.png'],
                                    [self.label_eclusa,'eclusa.png'],
                                    [self.label_porto,'porto.png'],
                                    [self.label_lixo,'lixo.png'],
                                    [self.label_bomba,'bomba_irrigacao.png'],
                                    [self.label_regua,'regua.png'],
                                    [self.label_placa,'placa_diversas.png'],
                                    [self.label_ponte,'ponte.png'],
                                    [self.label_barranco,'barranco.png'],
                                    [self.label_balneario,'balneario.png'],
                                    [self.label_estaleiro,'estaleiro.png'],
                                    [self.label_trapiche,'trapiche.png'],
                                    [self.label_edificacao,'edificacao.png'],
                                    [self.label_animal_vivo,'animal_vivo.png'],
                                    [self.label_mangueira,'mangueira.png'],
                                    [self.label_queimada,'queimada.png'],
                                    [self.label_instalacao_diversas,'instalacao_diversas.png'],
                                    [self.label_lavoura,'lavoura.png'],
                                    [self.label_outros_diversos,'outros_diversos.png'],
                                    [self.label_rede_eletrica,'rede_eletrica.png'],
                                    [self.label_protecao_talude,'protecao_talude.png'],
                                    [self.label_fissura_arvore_viva,'fissura_arvore_viva.png'],
                                    [self.label_diversos_APP,'diversos_APP.png'],
                                    [self.label_fissura_barranco,'fissura_barranco.png'],
                                    [self.label_solapamento,'solapamento.png'],
                                    [self.label_animal_morto,'animal_morto.png'],
                                    [self.label_rede_alta_tensao,'rede_alta_tensao.png'],
                                    [self.label_acampamento,'acampamento.png'],
                                    [self.label_banco_areia,'banco_areia.png'],
                                    [self.label_banco_areia_tocos,'banco_areia_tocos.png'],
                                    [self.label_bioengenharia,'bioengenharia.png'],
                                    [self.label_bomba_desativada,'bomba_desativada.png'],                       
                                    [self.label_porto_animais,'porto_animais.png'],
                                    [self.label_abertura_canal,'abertura_canal.png'],
                                    [self.label_fissura_arvore_morta,'fissura_arvore_morta.png'],
                                    [self.label_terminal_minerio,'terminal_minerio.png'],
                                    [self.label_descarga_lavoura,'descarga_lavoura.png'],
                                    [self.label_descarga_esgoto,'descarga_esgoto.png'],
                                    [self.label_desmatamento_APP,'desmatamento_APP.png'],
                                    [self.label_captacao_domestica,'captacao_domestica.png'],
                                    [self.label_placa_advertencia,'placa_advertencia.png'],
                                    [self.label_placa_controle,'placa_controle.png'],
                                    [self.label_placa_sinalizacao,'placa_sinalizacao.png'],
                                    [self.label_referencia_local,'referencia_local.png'],
                                    [self.label_porto_caiques,'porto_caiques.png'],
                                    [self.label_posto_controle,'posto_controle.png']]

        for icn in self.lista_icones_margem:
            icon = QPixmap(f'{self.plugin_dir}//imagens//{icn[1]}')
            icn[0].setPixmap(icon)


        ## leito
        lista_icones_leito =[[self.label_viva_leito, 'viva_leito.png'],
                             [self.label_morta_leito, 'morta_leito.png'],
                             [self.label_ilhota, 'ilhota.png'],
                             [self.label_rochas, 'rochas.png'],
                             [self.label_espuma, 'espuma.png'],
                             [self.label_ponte_leito, 'ponte.png'],
                             [self.label_itaipava, 'itaipava.png'],
                             [self.label_flutuacao_diversas, 'flutuacao_diversas.png'],
                             [self.label_boia_sinalizacao, 'boia_sinalizacao.png'],
                             [self.label_embalagens_perigosas, 'embalagens_perigosas.png'],
                             [self.label_encalhe_embarcacao, 'encalhe_embarcacao.png'],
                             [self.label_oleos, 'oleos.png'],
                             [self.label_equipamento_pesca, 'equipamento_pesca.png'],
                             [self.label_flutuacao_posto_controle, 'flutuacao_posto_controle.png'],
                             [self.label_embarcacao, 'embarcacao.png'],
                             [self.label_encalhe_diversos, 'encalhe_diversos.png']]

        for icn in lista_icones_leito:
            icon_leito = QPixmap(f'{self.plugin_dir}//imagens//{icn[1]}')
            icn[0].setPixmap(icon_leito)

        ## Morfo
        lista_icones_morfo = [[self.label_erosiva_fraca, 'erosiva_fraca.png'],
                                [self.label_erosiva_media, 'erosiva_media.png'],
                                [self.label_erosiva_forte, 'erosiva_forte.png'],
                                [self.label_erosiva_muito, 'erosiva_muito.png'],
                                [self.label_construtiva_fraca, 'construtiva_fraca.png'],
                                [self.label_construtiva_media, 'construtiva_media.png'],
                                [self.label_construtiva_forte, 'construtiva_forte.png'],
                                [self.label_construtiva_muito, 'construtiva_muito.png'],
                                [self.label_neutra_fraca, 'neutra_fraca.png'],
                                [self.label_neutra_media, 'neutra_media.png'],
                                [self.label_neutra_forte, 'neutra_forte.png'],
                                [self.label_neutra_muito, 'neutra_muito.png']]

        for icn in lista_icones_morfo:
            icn[0].setPixmap(QPixmap(f'{self.plugin_dir}//imagens//{icn[1]}'))

    def carregarFields(self):
        if self.primeiraVez != 0:
            pts_D = self.mMapLayerComboBox_4.currentLayer()
            pts_E = self.mMapLayerComboBox_2.currentLayer()
            fields_pts_D = [field.name() for field in pts_D.fields()]
            fields_pts_E = [field.name() for field in pts_E.fields()]
            fields_comuns = [str(i) for i in fields_pts_D if i in fields_pts_E]

            feats_D = pts_D.getFeatures()
            quanti_pts_D = sum(1 for i in feats_D)
            feats_E = pts_E.getFeatures() 
            quanti_pts_E = sum(1 for i in feats_E)
            self.quati_pts = quanti_pts_D + quanti_pts_E
            texto = f'Total de Pontos: {self.quati_pts}'
            self.label_quanti_pts.setText(texto)

            self.comboBox_atr.clear()
            self.comboBox_atr.addItems(fields_comuns)

            if fields_comuns == []:
                mensagem1 = 'Não há atributo em comum'
                mensagem2 = 'Escolha pontos da esquerda e da direita que possuam atributo em comum!'
                QMessageBox.warning(self, mensagem1, mensagem2)
        self.primeiraVez = 1

    def verificarFieldsPontos(self):
        AllItems = [self.comboBox_atr.itemText(i) for i in range(self.comboBox_atr.count())]
        if AllItems == []:
            self.trancaForcarVerificacao()
        else:
            self.mQgsFileWidget.setEnabled(True)

    def trancaForcarVerificacao(self):
        self.mQgsFileWidget.setEnabled(False)

    def unirGroupBox(self):
        if self.groupBox_oco_margem.isChecked():
            self.groupBox_oco_leito.setEnabled(True)
        else:
            self.groupBox_oco_leito.setEnabled(False)