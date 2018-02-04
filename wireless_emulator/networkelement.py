import logging
import subprocess
import xml.etree.ElementTree as ET
import copy
import os
from io import StringIO
import json

import wireless_emulator.emulator
from wireless_emulator.utils import addCoreDefaultValuesToNode, printErrorAndExit, addCoreDefaultStatusValuesToNode
from wireless_emulator.interface import *
from wireless_emulator.odlregistration import registerNeToOdl, registerNeToOdlNewVersion
import wireless_emulator.ethCrossConnect as EthXConn

logger = logging.getLogger(__name__)

class NetworkElement:

    def __init__(self, neUuid, neId, interfaces, eth_x_conn = None, dockerType = None, ptpClock = None , dbDic=None):
        self.uuid = neUuid
        self.dbDic=dbDic
        self.id = neId
        self.dockerName = self.uuid.replace(" ", "")
        self.dockerType = dockerType
        self.ptpEnabled = False
        if ptpClock is not None:
            self.ptpClockInstance = str(ptpClock[0])
            self.ptpEnabled = True
            logger.debug(" PTP is enabled. Clock instance is %s", self.ptpClockInstance)

        self.emEnv = wireless_emulator.emulator.Emulator()


        # TODO handle Eth Cross Connections
        self.eth_x_connect = eth_x_conn
        self.ethCrossConnectList = []

        # Configuration XML nodes
        self.xmlConfigurationTree = None
        self.configRootXmlNode = None
        self.networkElementConfigXmlNode = None
        self.ltpConfigXmlNode = None
        self.airInterfacePacConfigXmlNode = None
        self.pureEthernetPacConfigXmlNode = None
        self.ethernetContainerPacConfigXmlNode = None
        self.forwardingConstructConfigXmlNode = None
        self.ethernetPacConfigXmlNode = None
        self.ptpInstanceListConfigXmlNode = None
        self.ptpPortDsListConfigXmlNode = None
        self.forwardingDomainForwardingConstructXmlNode = None
        self.fdLtpXmlNode = None
        self.equipmentConfigXmlNode = None

        # Status XML nodes
        self.xmlStatusTree = None
        self.statusRootXmlNode = None
        self.airInterfaceStatusXmlNode = None
        self.networkElementStatusXmlNode = None
        self.ltpStatusXmlNode = None
        self.pureEthernetStatusXmlNode = None
        self.ethernetContainerStatusXmlNode = None
        self.forwardingConstructStatusXmlNode = None
        self.ethernetPacStatusXmlNode = None
        self.ptpInstanceListStatusXmlNode = None
        self.ptpPortDsListStatusXmlNode = None
        self.equipmentStatusXmlNode = None

        # namespace from host, used when adding a veth pair from the host inside a container, for emulating a physical connection
        self.networkNamespace = None

        self.networkIPAddress = self.emEnv.mgmtIpFactory.getFreeManagementNetworkIP()
        if self.networkIPAddress is None:
            logger.critical("Could not retrieve a free Management Network IP address for NE=%s", self.uuid)
            raise ValueError("Invalid Network IP address")
        self.managementIPAddressString = str(self.networkIPAddress[1])

        self.netconfPortNumber = None
        self.sshPortNumber = None
        self.restPortNumber = None
        if self.emEnv.portBasedEmulation is True:
            self.netconfPortNumber = self.emEnv.netconfPortBase + self.id
            self.restPortNumber = self.emEnv.restPortBase + self.id
            self.sshPortNumber = self.emEnv.sshPortBase + self.id
            self.managementIPAddressString = self.emEnv.emulatorIp
        else:
            self.netconfPortNumber = 8300
            self.sshPortNumber = 2200
            self.restPortNumber = 7000

        self.interfaces = interfaces
        self.interfaceList = []

        # docker network name
        self.networkName = "wte_net_" + str(self.id)

        tree = ET.parse(self.emEnv.xmlConfigFile)
        if tree is None:
            logger.critical("Could not parse XML default values configuration file!")
            printErrorAndExit()
        else:
            self.xmlConfigurationTree = tree

        tree = ET.parse(self.emEnv.xmlStatusFile)
        if tree is None:
            logger.critical("Could not parse XML default values status file!")
            printErrorAndExit()
        else:
            self.xmlStatusTree = tree

        # XML namespaces needed when searching the config XML
        self.namespaces = {'microwave-model' : 'urn:onf:params:xml:ns:yang:microwave-model',
                           'core-model' : 'urn:onf:params:xml:ns:yang:core-model',
                           'onf-ethernet-conditional-packages' : 'urn:onf:params:xml:ns:yang:onf-ethernet-conditional-packages',
                           'ptp' : 'urn:ietf:params:xml:ns:yang:ietf-ptp-dataset',
                           'ptp-ex': 'urn:onf:params:xml:ns:yang:onf-ptp-dataset'}
        self.saveXmlTemplates()

        logger.info("Created NetworkElement object with uuid=%s and id=%s and IP=%s",
                    self.uuid, self.id, self.managementIPAddressString)

        self.scriptIntf = StringIO()
        self.scriptIntf.write('#!/bin/bash\n\n')

    def getNeId(self):
        return self.id

    def getNeUuid(self):
        return self.uuid

    def getInterfaceFromInterfaceUuid(self, reqIntfId):
        for intf in self.interfaceList:
            intfId = intf.getInterfaceUuid()
            if intfId == reqIntfId:
                return intf
        logger.debug("Could not find interface having uuid=%s in ne=%s", reqIntfId, self.uuid)
        return None

    def getInterfaceFromInterfaceName(self, reqIntfName):
        for intf in self.interfaceList:
            intfId = intf.getInterfaceName()
            if intfId == reqIntfName:
                return intf
        logger.debug("Could not find interface having name=%s in ne=%s", reqIntfName, self.uuid)
        return None

    def saveXmlTemplates(self):
        self.saveConfigXmlTemplates()
        self.saveStatusXmlTemplates()

    def saveConfigXmlTemplates(self):

        self.configRootXmlNode = self.xmlConfigurationTree.getroot()

        airInterface = self.configRootXmlNode.find('microwave-model:mw-air-interface-pac', self.namespaces)
        self.airInterfacePacConfigXmlNode = copy.deepcopy(airInterface)
        self.configRootXmlNode.remove(airInterface)

        self.networkElementConfigXmlNode = self.configRootXmlNode.find('core-model:network-element', self.namespaces)

        forwardingDomain = self.networkElementConfigXmlNode.find('core-model:fd', self.namespaces)
        fd_fc_xmlNode = forwardingDomain.find('core-model:fc', self.namespaces)
        self.forwardingDomainForwardingConstructXmlNode = copy.deepcopy(fd_fc_xmlNode)
        forwardingDomain.remove(fd_fc_xmlNode)

        fdLtp = forwardingDomain.find('core-model:ltp', self.namespaces)
        self.fdLtpXmlNode = copy.deepcopy(fdLtp)
        forwardingDomain.remove(fdLtp)

        ltp = self.networkElementConfigXmlNode.find('core-model:ltp', self.namespaces)
        self.ltpConfigXmlNode = copy.deepcopy(ltp)
        self.networkElementConfigXmlNode.remove(ltp)

        pureEthernet = self.configRootXmlNode.find('microwave-model:mw-pure-ethernet-structure-pac', self.namespaces)
        self.pureEthernetPacConfigXmlNode = copy.deepcopy(pureEthernet)
        self.configRootXmlNode.remove(pureEthernet)

        ethernetContainer = self.configRootXmlNode.find('microwave-model:mw-ethernet-container-pac', self.namespaces)
        self.ethernetContainerPacConfigXmlNode = copy.deepcopy(ethernetContainer)
        self.configRootXmlNode.remove(ethernetContainer)

        forwardingConstruct = self.configRootXmlNode.find('core-model:forwarding-construct', self.namespaces)
        self.forwardingConstructConfigXmlNode = copy.deepcopy(forwardingConstruct)
        self.configRootXmlNode.remove(forwardingConstruct)

        ethernetPac = self.configRootXmlNode.find('onf-ethernet-conditional-packages:ethernet-pac', self.namespaces)
        self.ethernetPacConfigXmlNode = copy.deepcopy(ethernetPac)
        self.configRootXmlNode.remove(ethernetPac)

        ptpInstanceList = self.configRootXmlNode.find('ptp:instance-list', self.namespaces)
        self.ptpInstanceListConfigXmlNode = copy.deepcopy(ptpInstanceList)
        ptpPortDsList = self.ptpInstanceListConfigXmlNode.find('ptp:port-ds-list', self.namespaces)
        self.ptpPortDsListConfigXmlNode = copy.deepcopy(ptpPortDsList)
        self.ptpInstanceListConfigXmlNode.remove(ptpPortDsList)
        self.configRootXmlNode.remove(ptpInstanceList)

        equipmentNode = self.configRootXmlNode.find('core-model:equipment', self.namespaces)
        self.equipmentConfigXmlNode = copy.deepcopy(equipmentNode)
        self.configRootXmlNode.remove(equipmentNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:co-channel-group', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:mw-air-interface-hsb-end-point-pac', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:mw-air-interface-hsb-fc-switch-pac', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:mw-air-interface-diversity-pac', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:mw-hybrid-mw-structure-pac', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('microwave-model:mw-tdm-container-pac', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('core-model:operation-envelope', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('ptp:transparent-clock-default-ds', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

        uselessNode = self.configRootXmlNode.find('ptp:transparent-clock-port-ds-list', self.namespaces)
        self.configRootXmlNode.remove(uselessNode)

    def saveStatusXmlTemplates(self):

        self.statusRootXmlNode = self.xmlStatusTree.getroot()

        airInterface = self.statusRootXmlNode.find('mw-air-interface-pac')
        self.airInterfaceStatusXmlNode = copy.deepcopy(airInterface)
        self.statusRootXmlNode.remove(airInterface)

        self.networkElementStatusXmlNode = self.statusRootXmlNode.find('network-element')

        ltp = self.networkElementStatusXmlNode.find('ltp')
        self.ltpStatusXmlNode = copy.deepcopy(ltp)
        self.networkElementStatusXmlNode.remove(ltp)

        pureEthernetStructure = self.statusRootXmlNode.find('mw-pure-ethernet-structure-pac')
        self.pureEthernetStatusXmlNode = copy.deepcopy(pureEthernetStructure)
        self.statusRootXmlNode.remove(pureEthernetStructure)

        ethernetContainer = self.statusRootXmlNode.find('mw-ethernet-container-pac')
        self.ethernetContainerStatusXmlNode = copy.deepcopy(ethernetContainer)
        self.statusRootXmlNode.remove(ethernetContainer)

        forwardingConstruct = self.statusRootXmlNode.find('forwarding-construct')
        self.forwardingConstructStatusXmlNode = copy.deepcopy(forwardingConstruct)
        self.statusRootXmlNode.remove(forwardingConstruct)

        ethernetPac = self.statusRootXmlNode.find('ethernet-pac')
        self.ethernetPacStatusXmlNode = copy.deepcopy(ethernetPac)
        self.statusRootXmlNode.remove(ethernetPac)

        ptpInstanceList = self.statusRootXmlNode.find('instance-list')
        self.ptpInstanceListStatusXmlNode = copy.deepcopy(ptpInstanceList)
        ptpPortDsList = self.ptpInstanceListStatusXmlNode.find('port-ds-list', self.namespaces)
        self.ptpPortDsListStatusXmlNode = copy.deepcopy(ptpPortDsList)
        self.ptpInstanceListStatusXmlNode.remove(ptpPortDsList)
        self.statusRootXmlNode.remove(ptpInstanceList)

        equipmentNode = self.statusRootXmlNode.find('equipment')
        self.equipmentStatusXmlNode = copy.deepcopy(equipmentNode)
        self.statusRootXmlNode.remove(equipmentNode)

        uselessNode = self.statusRootXmlNode.find('co-channel-group')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('mw-air-interface-hsb-end-point-pac')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('mw-air-interface-hsb-fc-switch-pac')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('mw-air-interface-diversity-pac')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('mw-hybrid-mw-structure-pac')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('mw-tdm-container-pac')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('operation-envelope')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('transparent-clock-default-ds')
        self.statusRootXmlNode.remove(uselessNode)

        uselessNode = self.statusRootXmlNode.find('transparent-clock-port-ds-list')
        self.statusRootXmlNode.remove(uselessNode)

    def buildCoreModelXml(self):
        #network-element part here
        node = self.networkElementConfigXmlNode

        uuid = node.find('core-model:uuid', self.namespaces)
        uuid.text = self.uuid
        fd = node.find('core-model:fd', self.namespaces)
        uuid = fd.find('core-model:uuid', self.namespaces)
        uuid.text = 'eth-switch'
        layerProtocol = fd.find('core-model:layer-protocol-name', self.namespaces)
        layerProtocol.text = 'ETH'
        addCoreDefaultValuesToNode(fd, 'eth-switch', self.namespaces)
        addCoreDefaultValuesToNode(node,self.uuid, self.namespaces, self)

        self.buildEquipmentModelXml()

    def buildEquipmentModelXml(self):
        # equipment model part here
        node = copy.deepcopy(self.equipmentConfigXmlNode)

        uuid = node.find('core-model:uuid', self.namespaces)
        uuid.text = self.uuid + '-eq'
        addCoreDefaultValuesToNode(node, self.uuid + '-eq', self.namespaces, None)

        category = node.find('core-model:category', self.namespaces)
        categoryIn = category.find('core-model:category', self.namespaces)
        categoryIn.text = 'stand-alone-unit'

        manufacturedThing = node.find('core-model:manufactured-thing', self.namespaces)
        manufacturerProperties = manufacturedThing.find('core-model:manufacturer-properties', self.namespaces)

        manufacturerIdentifier = manufacturerProperties.find('core-model:manufacturer-identifier', self.namespaces)
        manufacturerIdentifier.text = 'ActionTech'

        manufacturerName = manufacturerProperties.find('core-model:manufacturer-name', self.namespaces)
        manufacturerName.text = 'Wireless Transport Emulator'

        equipmentType = manufacturedThing.find('core-model:equipment-type', self.namespaces)
        description = equipmentType.find('core-model:description', self.namespaces)
        description.text = 'High capacity packet radio outdoor unit'
        partTypeIdentifier = equipmentType.find('core-model:part-type-identifier', self.namespaces)
        partTypeIdentifier.text = '123-345-543'
        typeName = equipmentType.find('core-model:type-name', self.namespaces)
        typeName.text = 'EmulatedDevice'
        modelIdentifier = equipmentType.find('core-model:model-identifier', self.namespaces)
        modelIdentifier.text = 'MOD001'
        version = equipmentType.find('core-model:version', self.namespaces)
        version.text = '1.0'

        equipmentInstance = manufacturedThing.find('core-model:equipment-instance', self.namespaces)
        manufactureDate = equipmentInstance.find('core-model:manufacture-date', self.namespaces)
        manufactureDate.text = '2019-09-09T00:00:00.0Z'
        serialNumber = equipmentInstance.find('core-model:serial-number', self.namespaces)
        serialNumber.text = 'SN321123'

        self.configRootXmlNode.append(node)

    def buildCoreModelStatusXml(self):
        node = self.networkElementStatusXmlNode

        fd = node.find('fd')
        uuid = fd.find('uuid')
        uuid.text = 'eth-switch'
        addCoreDefaultStatusValuesToNode(fd)

        addCoreDefaultStatusValuesToNode(node)

        self.buildEquipmentModelStatusXml()

    def buildEquipmentModelStatusXml(self):
        node = copy.deepcopy(self.equipmentStatusXmlNode)

        uuid = node.find('uuid')
        uuid.text = self.uuid + '-eq'
        addCoreDefaultStatusValuesToNode(node)

        self.statusRootXmlNode.append(node)

    def buildPtpModelConfigXml(self):
        node = self.configRootXmlNode

        instanceNumber = self.ptpInstanceListConfigXmlNode.find('ptp:instance-number', self.namespaces)
        instanceNumber.text = self.ptpClockInstance

        defaultDs = self.ptpInstanceListConfigXmlNode.find('ptp:default-ds', self.namespaces)

        twoStepFlag = defaultDs.find('ptp:two-step-flag', self.namespaces)
        twoStepFlag.text = 'true'

        clockIdentity = defaultDs.find('ptp:clock-identity', self.namespaces)
        # byteRepr = ' '.join(format(ord(x), 'b') for x in 'PTPCLOCK')
        # byteRepr.replace(" ", "")
        clockIdentity.text = 'UFRQU2xhdmU='

        numberPorts = defaultDs.find('ptp:number-ports', self.namespaces)
        numberPorts.text = '0'

        clockQuality = defaultDs.find('ptp:clock-quality', self.namespaces)

        clockClass = clockQuality.find('ptp:clock-class', self.namespaces)
        clockClass.text = '248'

        clockAccuracy = clockQuality.find('ptp:clock-accuracy', self.namespaces)
        clockAccuracy.text = '254'

        priority2 = defaultDs.find('ptp:priority2', self.namespaces)
        priority2.text = '128'

        domainNumber = defaultDs.find('ptp:domain-number', self.namespaces)
        domainNumber.text = '24'

        slaveOnly = defaultDs.find('ptp:slave-only', self.namespaces)
        slaveOnly.text = 'false'

        parentDs = self.ptpInstanceListConfigXmlNode.find('ptp:parent-ds', self.namespaces)

        parentPortIdentity = parentDs.find('ptp:parent-port-identity', self.namespaces)

        clockIdentity = parentPortIdentity.find('ptp:clock-identity', self.namespaces)
        # byteRepr = ' '.join(format(ord(x), 'b') for x in 'MASTER01')
        # byteRepr.replace(" ", "")
        clockIdentity.text = 'UEFSRU5UMDE='

        portNumber = parentPortIdentity.find('ptp:port-number', self.namespaces)
        portNumber.text = '1'

        timePropertiesDs = self.ptpInstanceListConfigXmlNode.find('ptp:time-properties-ds', self.namespaces)

        timeTraceable = timePropertiesDs.find('ptp:time-traceable', self.namespaces)
        timeTraceable.text = 'false'

        frequencyTraceable = timePropertiesDs.find('ptp:frequency-traceable', self.namespaces)
        frequencyTraceable.text = 'false'

        ptpTimescale = timePropertiesDs.find('ptp:ptp-timescale', self.namespaces)
        ptpTimescale.text = 'true'

        grandmasterIdentity = parentDs.find('ptp:grandmaster-identity', self.namespaces)
        grandmasterIdentity.text = 'R1JBTkQwMDE='

        node.append(self.ptpInstanceListConfigXmlNode)

    def buildPtpModelStatusXml(self):
        node = self.statusRootXmlNode

        instanceNumber = self.ptpInstanceListStatusXmlNode.find('instance-number')
        instanceNumber.text = self.ptpClockInstance

        node.append(self.ptpInstanceListStatusXmlNode)

    def buildNotificationStatusXml(self):
        node = self.statusRootXmlNode

        notif = ET.SubElement(node, "notifications")
        timeout = ET.SubElement(notif, "timeout")
        timeout.text = str(self.emEnv.configJson['notificationPeriod'])

    def createInterfaces(self):
        portNumId = 1
        for intf in self.interfaces:
            intfObj = None
            if intf['layer'] == "MWPS":

                for port in intf['LTPs']:
                    intfObj = MwpsInterface(port['id'], portNumId, self, port['supportedAlarms'],
                                            port['physical-port-reference'], port['conditional-package'])
                    portNumId += 1
                    intfObj.buildXmlFiles()
                    self.interfaceList.append(intfObj)

            elif intf['layer'] == "MWS":

                for port in intf['LTPs']:
                    intfObj = MwsInterface(port['id'], portNumId, self, port['supportedAlarms'], port['serverLTPs'],
                                           port['conditional-package'])
                    portNumId += 1
                    intfObj.buildXmlFiles()
                    self.interfaceList.append(intfObj)

            elif intf['layer'] == "ETC":

                for port in intf['LTPs']:
                    if port.get('serverLTPs') is not None:
                        intfObj = MwEthContainerInterface(port['id'], portNumId, self, port['supportedAlarms'],
                                                          port['serverLTPs'], port['conditional-package'])
                    portNumId += 1
                    intfObj.buildXmlFiles()
                    self.interfaceList.append(intfObj)

            elif intf['layer'] == "ETY":

                for port in intf['LTPs']:
                    intfObj = ElectricalEtyInterface(port['id'], portNumId, self, port['physical-port-reference'])

                    portNumId += 1
                    intfObj.buildXmlFiles()
                    self.interfaceList.append(intfObj)

            elif intf['layer'] == "ETH":

                for port in intf['LTPs']:
                    intfObj = EthCtpInterface(port['id'], portNumId, self, port['serverLTPs'],
                                              port['conditional-package'])
                    portNumId += 1
                    intfObj.buildXmlFiles()
                    self.interfaceList.append(intfObj)

            else:
                logger.critical("Illegal layer value %s found in JSON configuration file for NE=%s",
                                intf['layer'], self.uuid)
                raise ValueError("Illegal layer value")

    def addEthCrossConnections(self):
        if self.eth_x_connect is not None:
            id = 1
            for xconn in self.eth_x_connect:
                xconnObj = EthXConn.EthCrossConnect(id, self, xconn)
                if xconnObj is not None:
                    self.ethCrossConnectList.append(xconnObj)
                    xconnObj.buildXmlFiles()
                    id += 1

    # TODO add support for new docker container
    def createDockerContainer(self):

        print("Creating docker container %s..." % (self.dockerName))

        if self.emEnv.portBasedEmulation is True:
            stringCmd = None
            if self.dockerType == 'JavaNetconfServer':
                stringCmd = "docker create -it --privileged -p %s:%s:830 -p %s:%s:22 --name=%s javasimulator" % \
                            (self.managementIPAddressString, self.netconfPortNumber,
                             self.managementIPAddressString, self.sshPortNumber, self.dockerName)
            else:
                stringCmd = "docker create -it --privileged -p %s:%s:830 -p %s:%s:22 -p %s:%s:700 --name=%s openyuma" % \
                            (self.managementIPAddressString, self.netconfPortNumber,
                             self.managementIPAddressString, self.sshPortNumber,
			     self.managementIPAddressString, self.restPortNumber, self.dockerName)
        else:
            self.createDockerNetwork()
            stringCmd = None
            if self.dockerType == 'JavaNetconfServer':
                stringCmd = "docker create -it --privileged -p %s:%s:830 -p %s:%s:22 --name=%s --network=%s javasimulator" % \
                            (self.managementIPAddressString, self.netconfPortNumber,
                             self.managementIPAddressString, self.sshPortNumber,
                             self.dockerName, self.networkName)
            else:
                stringCmd = "docker create -it --privileged -p %s:%s:830 -p %s:%s:22 --name=%s --network=%s openyuma" % \
                            (self.managementIPAddressString, self.netconfPortNumber,
                             self.managementIPAddressString, self.sshPortNumber,
                             self.dockerName, self.networkName)


        if stringCmd is not None:
            self.emEnv.executeCommandInOS(stringCmd)
            logger.debug("Created docker container %s having IP=%s", self.dockerName, self.managementIPAddressString)


    def createDockerNetwork(self):

        netAddressString = str(self.networkIPAddress.with_prefixlen)
        print("Creating docker network %s..." % (netAddressString))

        stringCmd = "docker network create -d bridge --subnet=%s --ip-range=%s %s" % \
                    (netAddressString, netAddressString, self.networkName)
        self.emEnv.executeCommandInOS(stringCmd)

        logger.debug("Created docker network %s having address %s", self.networkName, netAddressString)

    # TODO add support for new docker container
    def copyXmlConfigFileToDockerContainer(self):
        outFileName = "startup-cfg.xml"
        self.xmlConfigurationTree.write(outFileName)
        targetPath = "/usr/src/OpenYuma"

        stringCmd = "docker cp %s %s:%s" % \
                    (outFileName, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)

        stringCmd = "rm -f %s" % (outFileName)
        self.emEnv.executeCommandInOS(stringCmd)

#TODO add support for new docker container
    def copyXmlStatusFileToDockerContainer(self):
        outFileName = "microwave-model-status.xml"
        self.xmlStatusTree.write(outFileName)
        targetPath = "/usr/src/OpenYuma"

        stringCmd = "docker cp %s %s:%s" % \
                    (outFileName, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)

        stringCmd = "rm -f %s" % (outFileName)
        self.emEnv.executeCommandInOS(stringCmd)

    def startDockerContainer(self):
        stringCmd = "docker start %s" % (self.dockerName)
        self.emEnv.executeCommandInOS(stringCmd)

#TODO add support for new docker container
    def copyYangFilesToDockerContainer(self):

        directory = 'yang'
        for filename in os.listdir(directory):
            if filename.endswith(".yang"):
                stringCmd = "docker cp %s %s:%s" % \
                            (os.path.join(directory, filename), self.dockerName, "/usr/share/yuma/modules")
                self.emEnv.executeCommandInOS(stringCmd)

    def saveNetworkNamespace(self):
        stringCmd = "docker inspect -f '{{.State.Pid}}' \"%s\"" % (self.dockerName)
        returnValue = self.emEnv.executeCommandAndGetResultInOS(stringCmd)
        for line in returnValue:
            self.networkNamespace = line.decode("utf-8").rstrip('\n')

    def addNetworkElement(self):
        print("Adding Network element %s..." % (self.uuid))
        self.buildCoreModelXml()
        self.buildCoreModelStatusXml()

        if self.ptpEnabled is True:
            self.buildPtpModelConfigXml()
            self.buildPtpModelStatusXml()

        self.buildNotificationStatusXml()

        self.createInterfaces()
        self.addEthCrossConnections()

        self.createDockerContainer()

        self.copyXmlConfigFileToDockerContainer()
        self.copyXmlStatusFileToDockerContainer()
        self.copyYangFilesToDockerContainer()

        self.startDockerContainer()
        if self.emEnv.registerToOdl == True:
           # registerNeToOdl(self.emEnv.controllerInfo, self.uuid, self.managementIPAddressString)
           for controller in self.emEnv.controllerList:
               try:
                    registerNeToOdlNewVersion(controller, self.uuid, self.managementIPAddressString,
                                         self.netconfPortNumber)
                    break
               except:
                    print("Failed to register NE=%s having IP=%s and port=%s to the ODL controller having IP=%s" %
                         (self.uuid, self.managementIPAddressString, self.netconfPortNumber, controller['ip-address']))
                    continue

        self.saveNetworkNamespace()

        #debug
        self.xmlConfigurationTree.write('output-config-' + self.dockerName + '.xml')
        self.xmlStatusTree.write('output-status-' + self.dockerName + '.xml')

        #added 
	#add database file to docker
        targetPath = "/usr/src/OpenYuma"
        dbFile = 'dataBase.json'
        with open(dbFile, 'w') as db:
                json.dump(self.dbDic, db)
        stringCmd = "docker cp %s %s:%s" % \
                    (dbFile, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)

	#add alarmTable to docker
        self.createAlarmTable()

	#add rest file to docker
        restFile ='rest.py'
        stringCmd = "docker cp %s %s:%s" % (restFile, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)

	#get permission to exec rest.py 
        command = 'chmod 777 rest.py'
        stringCmd = "docker exec --detach -it %s %s" % (self.dockerName, command)
        self.emEnv.executeCommandInOS(stringCmd)
	
	#exec rest.py 
        command = 'python /usr/src/OpenYuma/rest.py'
        stringCmd = "docker exec --detach -it %s %s" % (self.dockerName, command)
        self.emEnv.executeCommandInOS(stringCmd)    
	


    def createAlarmTable(self):

        targetPath = "/usr/src/OpenYuma"
        dbFile = 'alarmTable.json'
        dict2 = {}

        for zone in self.dbDic['zones']:
                dict0 = {} 
                dict1 = {}
                for ap in zone['accessPoints']:
                        for usr in ap['users']:	
                                dict0[usr['address']] = "0"	
                dict1['isChanged'] = "0"
                dict1['lastEvent'] = "" 	
                dict1['users'] = dict0 
                dict2[zone['zoneId']] = dict1
        with open(dbFile, 'w') as db:
                json.dump(dict2, db)
        stringCmd = "docker cp %s %s:%s" % (dbFile, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)
	
#added

    def addInterfacesInDockerContainer(self):

        for intf in self.interfaceList:
            if intf.layer == 'MWPS':
                self.addDummyEthInterface(intf)
            elif intf.layer == 'MWS':
                self.addMwsInterface(intf)
            elif intf.layer == 'ETC':
                self.addMwEthContInterface(intf)
            elif intf.layer == 'ETY':
                self.addEtyEthInterface(intf)
            elif intf.layer == 'ETH':
                self.addEthCtpInterface(intf)
        for xconn in self.ethCrossConnectList:
            xconn.addXConn()

    def addMwsInterface(self, interfaceObj):
        logger.debug("Adding MWS interface %s to docker container %s", interfaceObj.getInterfaceName(), self.uuid)
        print("Adding MWS interface %s to docker container %s" % (interfaceObj.getInterfaceName(), self.uuid))

        command = "ip link add name %s type bond" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        command = "/bin/bash -c \"echo 0 > /sys/class/net/%s/bonding/mode\"" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        command = "/bin/bash -c \"echo 100 > /sys/class/net/%s/bonding/miimon\"" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        for serverLtp in interfaceObj.serverLtpsList:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()
            command = "ip link set %s down" % serverName
            self.executeCommandInContainer(command)

            command = "ip link set %s master %s" % (serverName, interfaceObj.getInterfaceName())
            self.executeCommandInContainer(command)
        command = "ip link set %s up" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

    def addMwEthContInterface(self, interfaceObj):

        logger.debug("Adding ETC interface %s to docker container %s", interfaceObj.getInterfaceName(), self.uuid)
        print("Adding ETC interface %s to docker container %s" % (interfaceObj.getInterfaceName(), self.uuid))

        command = "ip link add name %s type bond" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        command = "/bin/bash -c \"echo 0 > /sys/class/net/%s/bonding/mode\"" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        command = "/bin/bash -c \"echo 100 > /sys/class/net/%s/bonding/miimon\"" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

        for serverLtp in interfaceObj.serverLtps:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()

            command = "ip link set %s down" % serverName
            self.executeCommandInContainer(command)

            command = "ip link set %s master %s" % (serverName, interfaceObj.getInterfaceName())
            self.executeCommandInContainer(command)

        command = "ip link set %s up" % interfaceObj.getInterfaceName()
        self.executeCommandInContainer(command)

    def addEtyEthInterface(self, interfaceObj):
        if self.emEnv.isInterfaceObjPartOfLink(interfaceObj) is True:
            logger.debug("NOT adding interface %s to docker container %s because it was already added by the link",
                         interfaceObj.getInterfaceName(), self.uuid)
        else:
            logger.debug(
                "Adding ETY interface %s to docker container %s...",
                interfaceObj.getInterfaceName(), self.uuid)
            print(
                "Adding ETY interface %s to docker container %s..." %
                (interfaceObj.getInterfaceName(), self.uuid))

            command = "ip link add name %s type dummy" % interfaceObj.getInterfaceName()
            self.executeCommandInContainer(command)

            command = "ip link set dev %s up" % interfaceObj.getInterfaceName()
            self.executeCommandInContainer(command)

    def addEthCtpInterface(self, interfaceObj):
        logger.debug(
            "Adding ETH interface %s to docker container %s...",
            interfaceObj.getInterfaceName(), self.uuid)
        print(
            "Adding ETH interface %s to docker container %s..." %
            (interfaceObj.getInterfaceName(), self.uuid))

        if len(interfaceObj.serverLtpsList) != 1:
            print("Could not add ETH interface, because it has more that one server LTP..")
            return

        for serverLtp in interfaceObj.serverLtpsList:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()

            command = "ip link add name %s link %s type vlan id 0" % (interfaceObj.getInterfaceName(), serverName)
            self.executeCommandInContainer(command)

            command = "ip link set dev %s up" % interfaceObj.getInterfaceName()
            self.executeCommandInContainer(command)

    def addDummyEthInterface(self, interfaceObj):
        if self.emEnv.isInterfaceObjPartOfLink(interfaceObj) is True:
            logger.debug("NOT adding interface %s to docker container %s because it was already added by the link",
                         interfaceObj.getInterfaceName(), self.uuid)
        else:
            logger.debug(
                "Adding dummy interface %s to docker container %s...",
                interfaceObj.getInterfaceName(), self.uuid)
            print(
                "Adding dummy interface %s to docker container %s..." %
                (interfaceObj.getInterfaceName(), self.uuid))

            command = "ip link add name %s type dummy" % interfaceObj.getInterfaceName()
            self.executeCommandInContainer(command)

            # command = "ip address add %s/30 dev %s" % (interfaceObj.getIpAddress(), interfaceObj.getInterfaceName())
            # self.executeCommandInContainer(command)

            command = "ip link set %s up" % interfaceObj.getInterfaceName()
            self.executeCommandInContainer(command)

    def executeCommandInContainer(self, command):
        if command == '' or command is None:
            return
        stringCmd = "docker exec -it %s %s" % (self.dockerName, command)
        cmd = subprocess.Popen(stringCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in cmd.stderr:
            logger.critical("Failed executing command %s", command)
            strLine = line.decode("utf-8").rstrip('\n')
            logger.critical("Stderr: %s", strLine)
            raise RuntimeError
        for line in cmd.stdout:
            print(line.decode("utf-8").rstrip('\n'))

    def getCpuUsage(self, interval, index, results):
        cpu_percent = 0.0
        for i in range(0, interval):
            cmd = "ps -g `docker inspect -f '{{.State.Pid}}' %s` --no-headers -o \"pcpu\"" % self.dockerName
            output = self.emEnv.executeCommandAndGetResultInOS(cmd)
            for line in output:
                cpu_percent += float(line)

        cpu_percent /= float(interval)
        results[index] = cpu_percent

    def addInterfacesInDockerContainerToScript(self):

        for intf in self.interfaceList:
            if intf.layer == 'MWPS':
                self.addDummyEthInterfaceToScript(intf)
            elif intf.layer == 'MWS':
                self.addMwsInterfaceToScript(intf)
            elif intf.layer == 'ETC':
                self.addMwEthContInterfaceToScript(intf)
            elif intf.layer == 'ETY':
                self.addEtyEthInterfaceToScript(intf)
            elif intf.layer == 'ETH':
                self.addEthCtpInterfaceToScript(intf)
        for xconn in self.ethCrossConnectList:
            xconn.addXConnToScript()

        self.copyInterfaceScriptToDockerContainer()
        self.runInterfaceScriptInDockerContainer()

    def addMwsInterfaceToScript(self, interfaceObj):
        command = "ip link add name %s type bond\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        command = "echo 0 > /sys/class/net/%s/bonding/mode\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        command = "echo 100 > /sys/class/net/%s/bonding/miimon\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        for serverLtp in interfaceObj.serverLtpsList:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()
            command = "ip link set %s down\n" % serverName
            self.scriptIntf.write(command)

            command = "ip link set %s master %s\n" % (serverName, interfaceObj.getInterfaceName())
            self.scriptIntf.write(command)

        command = "ip link set %s up\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

    def addMwEthContInterfaceToScript(self, interfaceObj):

        command = "ip link add name %s type bond\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        command = "echo 0 > /sys/class/net/%s/bonding/mode\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        command = "echo 100 > /sys/class/net/%s/bonding/miimon\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

        for serverLtp in interfaceObj.serverLtps:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()

            command = "ip link set %s down\n" % serverName
            self.scriptIntf.write(command)

            command = "ip link set %s master %s\n" % (serverName, interfaceObj.getInterfaceName())
            self.scriptIntf.write(command)

        command = "ip link set %s up\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

    def addEtyEthInterfaceToScript(self, interfaceObj):
        if self.emEnv.isInterfaceObjPartOfLink(interfaceObj) is True:
            pass
        else:
            command = "ip link add name %s type dummy\n" % interfaceObj.getInterfaceName()
            self.scriptIntf.write(command)

            command = "ip link set dev %s up\n" % interfaceObj.getInterfaceName()
            self.scriptIntf.write(command)

        command = "tc qdisc add dev %s root handle 5:0 hfsc default 1\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)
        command = "tc class add dev %s parent 5:0 classid 5:1 hfsc sc rate 10Gbit ul rate 10Gbit\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

    def addEthCtpInterfaceToScript(self, interfaceObj):

        if len(interfaceObj.serverLtpsList) != 1:
            return

        for serverLtp in interfaceObj.serverLtpsList:
            serverObj = self.getInterfaceFromInterfaceUuid(serverLtp)
            serverName = serverObj.getInterfaceName()

            command = "ip link add name %s link %s type vlan id 0\n" % (interfaceObj.getInterfaceName(), serverName)
            self.scriptIntf.write(command)

            command = "ip link set dev %s up\n" % interfaceObj.getInterfaceName()
            self.scriptIntf.write(command)

    def addDummyEthInterfaceToScript(self, interfaceObj):
        if self.emEnv.isInterfaceObjPartOfLink(interfaceObj) is True:
            pass
        else:
            command = "ip link add name %s type dummy\n" % interfaceObj.getInterfaceName()
            self.scriptIntf.write(command)

            # command = "ip address add %s/30 dev %s" % (interfaceObj.getIpAddress(), interfaceObj.getInterfaceName())
            # self.executeCommandInContainer(command)

            command = "ip link set %s up\n" % interfaceObj.getInterfaceName()
            self.scriptIntf.write(command)

        command = "tc qdisc add dev %s root handle 5:0 hfsc default 1\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)
        command = "tc class add dev %s parent 5:0 classid 5:1 hfsc sc rate 100Mbit ul rate 100Mbit\n" % interfaceObj.getInterfaceName()
        self.scriptIntf.write(command)

    def copyInterfaceScriptToDockerContainer(self):
        outFileName = "buildIntf.sh"

        f = open(outFileName, 'w+')
        f.write(self.scriptIntf.getvalue())
        f.close()

        targetPath = "/usr/src/OpenYuma"

        os.chmod('./buildIntf.sh', 777)

        stringCmd = "docker cp %s %s:%s" % \
                    (outFileName, self.dockerName, targetPath)
        self.emEnv.executeCommandInOS(stringCmd)

        stringCmd = "rm -f %s" % (outFileName)
        self.emEnv.executeCommandInOS(stringCmd)

    def runInterfaceScriptInDockerContainer(self):
        cmd = "/usr/src/OpenYuma/buildIntf.sh"
        self.executeCommandInContainer(cmd)
