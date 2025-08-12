#include "PdTermSerial.h"
#include <QMessageBox>
#include <QDebug>

PdTermSerial::PdTermSerial(QObject *parent) : QObject(parent), serial(new QSerialPort(this))
{
    connect(serial, &QSerialPort::readyRead, this, &PdTermSerial::handleReadyRead);
    connect(serial, &QSerialPort::errorOccurred, this, &PdTermSerial::handleError);
}

PdTermSerial::~PdTermSerial()
{
    if(serial->isOpen()) {
        serial->close();
    }
}

void PdTermSerial::refreshPorts(QComboBox *portCombo)
{
    if (!portCombo) return;
    
    portCombo->clear();
    const auto ports = QSerialPortInfo::availablePorts();
    
    for (const QSerialPortInfo &port : ports) {
        QString portName = port.portName();
        if (portName.startsWith("ttyUSB") || portName.startsWith("ttyACM")) {
            portCombo->addItem(portName);
            qDebug() << "Porta encontrada:" << portName;
        }
    }
    
    emit statusChanged(portCombo->count() > 0 
        ? QString("%1 portas encontradas").arg(portCombo->count())
        : "Nenhuma porta encontrada");
}

bool PdTermSerial::connectSerial(const QString &portName)
{
    if (serial->isOpen()) return true;

    serial->setPortName(portName);
    if (serial->open(QIODevice::ReadWrite)) {
        emit statusChanged("Conectado - " + portName);
        return true;
    }
    
    emit errorOccurred("Não foi possível abrir a porta serial");
    return false;
}

void PdTermSerial::disconnectSerial()
{
    if (serial->isOpen()) {
        serial->close();
        emit statusChanged("Desconectado");
    }
}

void PdTermSerial::sendData(const QByteArray &data)
{
    if (!serial->isOpen()) {
        emit errorOccurred("Porta serial não está aberta");
        return;
    }

    qint64 bytesWritten = serial->write(data);
    if (bytesWritten == -1) {
        emit errorOccurred("Falha no envio: " + serial->errorString());
    } else {
        serial->flush();
    }
}

void PdTermSerial::handleReadyRead()
{
    emit dataReceived(serial->readAll());
}

void PdTermSerial::handleError(QSerialPort::SerialPortError error)
{
    if (error != QSerialPort::NoError) {
        emit errorOccurred(serial->errorString());
        if (serial->isOpen()) {
            serial->close();
        }
    }
}

bool PdTermSerial::isConnected() const
{
    return serial && serial->isOpen();
}
