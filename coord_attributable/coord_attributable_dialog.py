# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordATDialog
                                 A QGIS plugin
 adds points' coordinates to attribute table, according to the chosen CRS.
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

import os
from qgis.core import QgsCoordinateReferenceSystem
from PyQt5.QtCore import QCoreApplication  #QTranslator
from PyQt5.QtWidgets import QDialog, QTableWidget
from PyQt5.QtWidgets import *
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'coord_attributable_dialog_base.ui'))


class CoordATDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CoordATDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.contAdds = 0 #cont each time a coordinate is added
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.lista_header_LatLong = []
        self.lista_EPSG_code = []
        self.lista_DMS_signal = [] #if output in DMS, 1, else 0
        # default to show as starts the plugin. The most used here with D°M'S"
        crs_start = QgsCoordinateReferenceSystem("EPSG:4674") #4989")
        self.mQgsProjectionSelectionWidget.setCrs(crs_start)
        row_number = 5  # lets add only 5 rows to user to see how it will be
        for row in range(row_number):
            self.tableWidget.insertRow(0)
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Pt {} example of Lat D° M' S\"".format(5-row))) #just to look good
            self.tableWidget.setItem(0, 1, QTableWidgetItem("Pt {} example of Long D° M' S\"".format(5-row)))
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def addCoordinate(self):
        """Add columns corresponding to the coordinates X and Y of
        the chosen CRS """
        
        # TODO:
        # look at https://www.programmersought.com/article/466539668/ to 
        # try to select 2 columns together TableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        if self.mQgsFileWidget.filePath():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

        row_number = 5
        column_number = 2
        column_lat = 0 #Latutude
        column_long = 1 #Longitude
        EPSG_code = self.mQgsProjectionSelectionWidget.crs().authid()
        EPSG_name = self.mQgsProjectionSelectionWidget.crs().description()

        if self.mQgsProjectionSelectionWidget.crs().isValid():
            #could remove old table here but I think it is ugly to see it white, as user    
            
            if self.mQgsProjectionSelectionWidget.crs().isGeographic(): # if it is a geografic 

                reply = QMessageBox.question(self,"Geografic Coordinate",
                    "Do you want D° M' S\"? \n\n'NO' will add decimal degree.",
                    QMessageBox.Yes,QMessageBox.No,)
                
                if reply == QMessageBox.Yes:  #D° M' and S"
                    
                    for i in self.lista_header_LatLong:
                        if i == ("X° "+EPSG_code[5:]):
                            message = QCoreApplication.translate('Message to user','This CRS was already chosen')
                            QMessageBox.warning(self, QCoreApplication.translate('Message to user','Missing information or invalid'), message)
                            break #the break on previous line wont run this lines, even if else is not in loop
                    else:

                        # --- remove old table
                        if self.contAdds == 0:
                            self.tableWidget.removeColumn(0)
                            self.tableWidget.removeColumn(0)
                        
                        header_pair = ["Y° "+EPSG_code[5:], "X° "+EPSG_code[5:]]
                        self.lista_header_LatLong.insert(0, "X° "+EPSG_code[5:])
                        self.lista_header_LatLong.insert(0, "Y° "+EPSG_code[5:])
                        self.lista_EPSG_code.insert(0,EPSG_code)
                        self.lista_EPSG_code.insert(0,EPSG_code)
                        self.lista_DMS_signal.insert(0,1)
                        self.lista_DMS_signal.insert(0,1)

                        #--- header ---
                        self.tableWidget.insertColumn(0)
                        self.tableWidget.insertColumn(0)
                        self.tableWidget.setHorizontalHeaderLabels(header_pair)
                        if self.contAdds == 0:
                            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                        else:
                            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                            self.tableWidget.resizeColumnsToContents()
                        
                        #--- cells ---
                        for row in range(row_number):
                            self.tableWidget.setItem(row, column_lat, QTableWidgetItem("Pt {} Lat D° M' S\" {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description())))
                            self.tableWidget.setItem(row, column_long, QTableWidgetItem("Pt {} Long D° M' S\" {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description())))
                        
                        self.contAdds += 1
   
                else: #decimal degree

                    for i in self.lista_header_LatLong:
                        if i == ("X "+EPSG_code[5:]):
                            message = QCoreApplication.translate('Message to user','This CRS was already chosen')
                            QMessageBox.warning(self, QCoreApplication.translate('Message to user','Missing information or invalid'), message)
                            break #the break on previous line wont run this lines, even if else is not in loop
                    else:
                        # --- remove old table
                        if self.contAdds == 0:
                            self.tableWidget.removeColumn(0)
                            self.tableWidget.removeColumn(0)

                        header_pair = ["Y "+EPSG_code[5:], "X "+EPSG_code[5:]]
                        self.lista_header_LatLong.insert(0, "X "+EPSG_code[5:])
                        self.lista_header_LatLong.insert(0, "Y "+EPSG_code[5:])
                        self.lista_EPSG_code.insert(0,EPSG_code)
                        self.lista_EPSG_code.insert(0,EPSG_code)
                        self.lista_DMS_signal.insert(0,0)
                        self.lista_DMS_signal.insert(0,0)

                        self.tableWidget.insertColumn(0)
                        self.tableWidget.insertColumn(0)
                        self.tableWidget.setHorizontalHeaderLabels(header_pair)
                        if self.contAdds == 0:
                            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                        else:
                            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                            self.tableWidget.resizeColumnsToContents()

                        for row in range(row_number):
                            self.tableWidget.setItem(row, column_lat, QTableWidgetItem(
                                "Pt {} Lat Decimal Degree {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description()))
                                )
                            self.tableWidget.setItem(row, column_long, QTableWidgetItem(
                                "Pt {} Long Decimal Degree {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description()))
                                )
                        
                        self.contAdds += 1

            else: #non geographic

                for i in self.lista_header_LatLong:
                    if i == ("X "+EPSG_code[5:]):
                        message = QCoreApplication.translate('Message to user','This CRS was already chosen')
                        QMessageBox.warning(self, QCoreApplication.translate('Message to user','Missing information or invalid'), message)
                        break
                else:  #the break on previous line wont run this lines, even if else is not in loop
                    # --- remove old table
                    if self.contAdds == 0:
                        self.tableWidget.removeColumn(0)
                        self.tableWidget.removeColumn(0)
                    
                    header_pair = ["Y "+EPSG_code[5:], "X "+EPSG_code[5:]]
                    self.lista_header_LatLong.insert(0, "X "+EPSG_code[5:])
                    self.lista_header_LatLong.insert(0, "Y "+EPSG_code[5:])
                    self.lista_EPSG_code.insert(0,EPSG_code)
                    self.lista_EPSG_code.insert(0,EPSG_code)
                    self.lista_DMS_signal.insert(0,0)
                    self.lista_DMS_signal.insert(0,0)

                    self.tableWidget.insertColumn(0)
                    self.tableWidget.insertColumn(0)
                    self.tableWidget.setHorizontalHeaderLabels(header_pair)
                    if self.contAdds == 0:
                        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                    else:
                        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                        self.tableWidget.resizeColumnsToContents()

                    for row in range(row_number):
                        self.tableWidget.setItem(row, column_lat, QTableWidgetItem("Lat Pt {} {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description())))
                        self.tableWidget.setItem(row, column_long, QTableWidgetItem("Long Pt {} {}".format(row+1, self.mQgsProjectionSelectionWidget.crs().description())))
                    
                    self.contAdds += 1

        

    def removeCoordinate(self):
        """Removes the columns corresponding to the coordinates X and Y 
        of the chosen CRS"""
        if self.contAdds != 0:

            selecionado = self.tableWidget.currentColumn()
            if selecionado == -1:
                print("Select column to remove")
            elif selecionado % 2 == 0:
                self.tableWidget.removeColumn(selecionado)
                self.tableWidget.removeColumn(selecionado)
                self.contAdds -= 1
                self.lista_header_LatLong.pop(selecionado)
                self.lista_header_LatLong.pop(selecionado)
                self.lista_DMS_signal.pop(selecionado)
                self.lista_DMS_signal.pop(selecionado)
            else:
                self.tableWidget.removeColumn(selecionado)
                self.tableWidget.removeColumn(selecionado-1)
                self.lista_header_LatLong.pop(selecionado)
                self.lista_header_LatLong.pop(selecionado-1)
                self.lista_DMS_signal.pop(selecionado)
                self.lista_DMS_signal.pop(selecionado-1)
                self.contAdds -= 1
            
            if self.contAdds == -1: # in case the default values be removed
                self.contAdds = 0
            
            if self.contAdds == 0:
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def enableOkButton(self):
        if self.contAdds != 0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)