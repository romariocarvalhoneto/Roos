# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordAT
                                 A QGIS plugin
 Adds points' coordinates to attribute table, according to the chosen CRS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-07-21
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Romário Moraes Carvalho Neto
        email                : romariocarvalho@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import *
from qgis.core import (QgsMapLayerProxyModel, QgsVectorDataProvider, QgsGeometry, QgsFeature,
                       QgsPointXY, QgsVectorLayer, QgsField, QgsCoordinateReferenceSystem,
                       QgsVectorFileWriter, QgsProject, QgsCoordinateTransform, QgsWkbTypes)
from qgis import processing
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .coord_attributable_dialog import CoordATDialog
import os.path


class CoordAT:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CoordAT_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Coord. AttribuTable')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CoordAT', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/coord_attributable/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Add points coordinate to Attribute Table'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Coord. AttribuTable'),
                action)
            self.iface.removeToolBarIcon(action)

                    # CRS=EPSGcode, DMS_format_signal=bool
    def addAttribute(self, CRS, layer_input, outputPath, NomeColunaAdicionar, DMS_format_signal):
        """Adds a coordinate"""
        crs_loop = QgsCoordinateReferenceSystem(CRS)

        if DMS_format_signal == 1: #add D°M'S"
            # check if the crs are the same
            if layer_input.sourceCrs() == crs_loop: # don't need to transform
                layer_output = QgsVectorLayer(outputPath, "", "ogr")

                caps = layer_output.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.AddAttributes:
                    res = layer_output.dataProvider().addAttributes([QgsField(NomeColunaAdicionar, QVariant.String)])
                
                layer_output.updateFields()

                listaFieldName = [] #list fields (cabecalho)
                cabecalho = layer_output.fields()
                for field in cabecalho:
                    listaFieldName.append(field.name())

                features = layer_output.getFeatures()
                contFid = 0
                for feature in features:
                    geom = feature.geometry()
                    fid = contFid   # ID of the feature we will modify
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:

                        pt_y = geom.asPoint().y()
                        py_x = geom.asPoint().x()

                        if NomeColunaAdicionar[0] == 'Y':
                            d = int(pt_y)
                            m = int((pt_y - d) * 60)
                            s = (pt_y - d - m/60) * 3600.00
                            z = round(s, 3)
                            if d >= 0:
                                pt_format_DMS = " {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "N {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            else:
                                pt_format_DMS = "-{}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "S {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })

                            contFid += 1
                        else:    
                            d = int(py_x)
                            m = int((py_x - d) * 60)
                            s = (py_x - d - m/60) * 3600.00
                            z = round(s, 3)
                            if d >= 0:
                                pt_format_DMS = " {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                print(pt_format_DMS)
                                #pt_format_DMS = "E {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            else:
                                pt_format_DMS = "-{}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                print(pt_format_DMS)
                                #pt_format_DMS = "W {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            
                            contFid += 1

            else: #need to transform

                layer_output = QgsVectorLayer(outputPath, "", "ogr")

                caps = layer_output.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.AddAttributes:
                    res = layer_output.dataProvider().addAttributes([QgsField(NomeColunaAdicionar, QVariant.String)])
                
                layer_output.updateFields()

                listaFieldName = [] #list fields (cabecalho)
                cabecalho = layer_output.fields()
                for field in cabecalho:
                    listaFieldName.append(field.name())

                features = layer_output.getFeatures()
                contFid = 0
                for feature in features:
                    geom = feature.geometry()
                    fid = contFid   # ID of the feature we will modify
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:
                        crsSrc = layer_input.sourceCrs()
                        transformContext = QgsProject.instance()  #.transformContext()
                        xform = QgsCoordinateTransform(crsSrc, crs_loop, transformContext)

                        # forward transformation: src -> dest
                        pt = xform.transform(QgsPointXY(geom.asPoint().x(), geom.asPoint().y()))

                        if NomeColunaAdicionar[0] == 'Y':
                            d = int(pt.y())
                            m = int((pt.y() - d) * 60)
                            s = (pt.y() - d - m/60) * 3600.00
                            z = round(s, 3)
                            if d >= 0:
                                pt_format_DMS = " {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "N {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            else:
                                pt_format_DMS = "-{}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "S {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })

                            contFid += 1
                        else:    
                            d = int(pt.x())
                            m = int((pt.x() - d) * 60)
                            s = (pt.x() - d - m/60) * 3600.00
                            z = round(s, 3)
                            if d >= 0:
                                pt_format_DMS = " {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "E {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            else:
                                pt_format_DMS = "-{}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                #pt_format_DMS = "W {}° {}' {}\" ".format(abs(d),abs(m),abs(z))
                                attrs = { listaFieldName.index(NomeColunaAdicionar) : pt_format_DMS }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                                layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            
                            contFid += 1

        else: #not D°M'S"
            # check if the crs are the same
            if layer_input.sourceCrs() == crs_loop: #dont transform
                layer_output = QgsVectorLayer(outputPath, "", "ogr")

                caps = layer_output.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.AddAttributes:  
                    res = layer_output.dataProvider().addAttributes([QgsField(NomeColunaAdicionar, QVariant.Double)])
                
                layer_output.updateFields()

                listaFieldName = [] #list fields (cabecalho)
                cabecalho = layer_output.fields()
                for field in cabecalho:
                    listaFieldName.append(field.name())

                features = layer_output.getFeatures()
                contFid = 0
                for feature in features:
                    geom = feature.geometry()
                    fid = contFid   # ID of the feature we will modify
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:
                        if NomeColunaAdicionar[0] == 'Y':
                            attrs = { listaFieldName.index(NomeColunaAdicionar) : geom.asPoint().y() }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                            layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            contFid += 1
                        else:    
                            attrs = { listaFieldName.index(NomeColunaAdicionar) : geom.asPoint().x() }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                            layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            contFid += 1

            else: # transform

                layer_output = QgsVectorLayer(outputPath, "", "ogr")

                caps = layer_output.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.AddAttributes:  
                    res = layer_output.dataProvider().addAttributes([QgsField(NomeColunaAdicionar, QVariant.Double)])
                
                layer_output.updateFields()

                listaFieldName = [] #list fields (cabecalho)
                cabecalho = layer_output.fields()
                for field in cabecalho:
                    listaFieldName.append(field.name())

                features = layer_output.getFeatures()
                contFid = 0
                for feature in features:
                    geom = feature.geometry()
                    fid = contFid   # ID of the feature we will modify
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:
                        crsSrc = layer_input.sourceCrs()
                        transformContext = QgsProject.instance()  #.transformContext()
                        xform = QgsCoordinateTransform(crsSrc, crs_loop, transformContext)

                        # forward transformation: src -> dest
                        pt = xform.transform(QgsPointXY(geom.asPoint().x(), geom.asPoint().y()))

                        if NomeColunaAdicionar[0] == 'Y':
                            attrs = { listaFieldName.index(NomeColunaAdicionar) : pt.y()}   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                            layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            contFid += 1
                        else:    
                            attrs = { listaFieldName.index(NomeColunaAdicionar) : pt.x() }   #changes values of attributes with index 0 (primeiro) and 1 (segundo)
                            layer_output.dataProvider().changeAttributeValues({ fid : attrs })
                            contFid += 1

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        #if self.first_start == True:
            #self.first_start = False
        self.dlg = CoordATDialog()
        self.dlg.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        filename = self.dlg.mQgsFileWidget.setStorageMode(3) #QgsFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        _filter = self.dlg.mQgsFileWidget.setFilter('*.shp') 
        signal_enable_ok = self.dlg.mQgsFileWidget.fileChanged.connect(self.dlg.enableOkButton)
        self.dlg.addButton.clicked.connect(self.dlg.addCoordinate)
        self.dlg.removeButton.clicked.connect(self.dlg.removeCoordinate)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            layer_selecionado = self.dlg.mMapLayerComboBox.currentLayer() # gets the selected layer
            output_path = self.dlg.mQgsFileWidget.filePath()
            chosen_CRS_header = self.dlg.lista_header_LatLong
            lista_chosen_CRS = self.dlg.lista_EPSG_code
            chosen_DMS_format_signal = self.dlg.lista_DMS_signal

            # makes a copy of the point layer 
            layer_selecionado.selectAll()
            clone_layer = processing.run("native:saveselectedfeatures", {'INPUT': layer_selecionado, 'OUTPUT': output_path})#['OUTPUT']
            layer_selecionado.removeSelection()
            # ---------------------------
            
            cont = 0 
            for crs_header in chosen_CRS_header:
                self.addAttribute(lista_chosen_CRS[cont], layer_selecionado, output_path, crs_header, chosen_DMS_format_signal[cont])
                cont += 1

            new_layer_points = self.iface.addVectorLayer(output_path,"", "ogr")
